"""Score masked held-out review responses against their frozen case key.

The unit is the complete case response. A wrong, malformed, or unanswered
case remains in the scheduled denominator. Cases are paired across workflows.
"""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any, ClassVar, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .held_out_reviewer_packets import CASE_IDS, PACKET_SCHEMA, SESSIONS, assignment_rows

_JSON = dict[str, Any]
_EventKey = tuple[str, str]
_ScoreState = Literal["omitted", "explicit_null", "reported_zero", "reported_nonzero"]
_CONDITIONS = ("p3if", "diff")
_RESULTS = ("correct", "incorrect", "missing", "malformed")


class _ClosedModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", strict=True)


class _Scores(_ClosedModel):
    strength: _ScoreState
    confidence: _ScoreState


class _Side(_ClosedModel):
    coordinate: list[Optional[str]] = Field(min_length=3, max_length=3)
    scores: Optional[_Scores]


class _Event(_ClosedModel):
    kind: Literal["framework", "property", "process", "perspective", "relationship"]
    id: str = Field(min_length=1)
    change: Literal["added", "removed", "modified"]
    fields: list[str]
    rewired: bool
    before: Optional[_Side]
    after: Optional[_Side]

    def key(self) -> _EventKey:
        return self.kind, self.id


class _Response(_ClosedModel):
    case_id: str
    classification: Literal["identical_bytes", "encoding_only", "declared_change"]
    events: list[_Event]

    def events_by_key(self) -> dict[_EventKey, _Event]:
        indexed = {event.key(): event for event in self.events}
        if len(indexed) != len(self.events):
            raise ValueError("A response contains duplicate event keys.")
        if any(len(event.fields) != len(set(event.fields)) for event in self.events):
            raise ValueError("An event contains duplicate changed fields.")
        return indexed


def _unique_object(pairs: list[tuple[str, Any]]) -> _JSON:
    parsed = dict(pairs)
    if len(parsed) != len(pairs):
        raise ValueError("Duplicate JSON key.")
    return parsed


def _nonfinite_constant(value: str) -> None:
    raise ValueError(f"Non-finite JSON constant {value}.")


def _strict_json(raw: bytes) -> Any:
    return json.loads(
        raw.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_nonfinite_constant
    )


def _case_key(raw: bytes) -> dict[str, _JSON]:
    manifest = _strict_json(raw)
    if manifest["schema_version"] != "p3if.held-out-case-manifest.v1":
        raise ValueError("Unsupported held-out case manifest.")
    rows = manifest["cases"]
    indexed = {row["case_id"]: row for row in rows}
    if len(indexed) != len(rows) or indexed.keys() != set(CASE_IDS):
        raise ValueError("Unexpected held-out case IDs.")
    return indexed


def _schedule(raw: bytes, case_digest: str) -> list[_JSON]:
    manifest = _strict_json(raw)
    if (
        manifest["schema_version"] != PACKET_SCHEMA
        or manifest["case_manifest_sha256"] != case_digest
    ):
        raise ValueError("The packet manifest does not bind the supplied held-out key.")
    expected = assignment_rows()
    if json.dumps(manifest["assignments"], sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError("The packet manifest disagrees with the frozen assignment schedule.")
    return expected


def _session_answers(path: Path, assigned: set[str]) -> tuple[dict[str, Any], set[str], _JSON]:
    try:
        source = path.read_bytes()
    except FileNotFoundError:
        return {}, set(), {"file_status": "missing", "unassignable_rows": 0}
    digest = sha256(source).hexdigest()
    try:
        raw = _strict_json(source)
    except (UnicodeDecodeError, ValueError, RecursionError):
        raw = None
    if not isinstance(raw, list):
        return {}, assigned, {"file_status": "malformed", "unassignable_rows": 0, "sha256": digest}
    indexed: dict[str, Any] = {}
    duplicates: set[str] = set()
    unassignable = 0
    for row in raw:
        case_id = row.get("case_id") if isinstance(row, dict) else None
        if not isinstance(case_id, str) or case_id not in assigned:
            unassignable += 1
        elif case_id in indexed:
            duplicates.add(case_id)
        else:
            indexed[case_id] = row
    return (
        indexed,
        duplicates,
        {
            "file_status": "parsed",
            "sha256": digest,
            "unassignable_rows": unassignable,
            "duplicate_case_ids": sorted(duplicates),
        },
    )


def _side_errors(prefix: str, expected: Optional[_Side], answer: Optional[_Side]) -> list[str]:
    if expected is None or answer is None:
        return [] if expected is answer else [f"{prefix}_presence"]
    errors = []
    if expected.coordinate != answer.coordinate:
        errors.append(f"{prefix}_coordinate")
    if expected.scores != answer.scores:
        errors.append(f"{prefix}_scores")
    return errors


def _event_errors(expected: _Event, answer: _Event) -> list[str]:
    errors = []
    if expected.change != answer.change:
        errors.append("change")
    if set(expected.fields) != set(answer.fields):
        errors.append("fields")
    if expected.rewired != answer.rewired:
        errors.append("rewired")
    return [
        *errors,
        *_side_errors("before", expected.before, answer.before),
        *_side_errors("after", expected.after, answer.after),
    ]


def _describe_scores(expected: _Response, answer: Any, duplicate_or_invalid: bool) -> _JSON:
    if duplicate_or_invalid:
        return {"result": "malformed", "comparison": None}
    if answer is None:
        return {"result": "missing", "comparison": None}
    try:
        response = _Response.model_validate(answer)
        actual = response.events_by_key()
    except (ValidationError, ValueError):
        return {"result": "malformed", "comparison": None}

    required = expected.events_by_key()
    missing = sorted(required.keys() - actual.keys())
    extraneous = sorted(actual.keys() - required.keys())
    disagreements = []
    for kind, identity in sorted(actual.keys() & required.keys()):
        parts = _event_errors(required[kind, identity], actual[kind, identity])
        if parts:
            disagreements.append({"kind": kind, "id": identity, "components": parts})
    classification_correct = expected.classification == response.classification
    correct = classification_correct and not missing and not extraneous and not disagreements
    return {
        "result": "correct" if correct else "incorrect",
        "comparison": {
            "classification_correct": classification_correct,
            "reported_classification": response.classification,
            "missing_events": [{"kind": kind, "id": identity} for kind, identity in missing],
            "extraneous_events": [{"kind": kind, "id": identity} for kind, identity in extraneous],
            "event_disagreements": disagreements,
        },
    }


def _counts(rows: list[_JSON]) -> _JSON:
    return {
        "assigned": len(rows),
        **{result: sum(row["result"] == result for row in rows) for result in _RESULTS},
        "encoding_controls": sum(row["expected_classification"] == "encoding_only" for row in rows),
        "false_declared_changes": sum(row["false_declared_change"] for row in rows),
    }


def _pair_rows(rows: list[_JSON]) -> list[_JSON]:
    paired = {(row["case_id"], row["condition"]): row for row in rows}
    return [
        {
            "case_id": case_id,
            "domain": paired[case_id, "p3if"]["domain"],
            **{condition: paired[case_id, condition]["result"] for condition in _CONDITIONS},
        }
        for case_id in CASE_IDS
    ]


def _pair_counts(rows: list[_JSON]) -> _JSON:
    counts = {"both_correct": 0, "p3if_only": 0, "diff_only": 0, "neither_correct": 0}
    categories = {
        (True, True): "both_correct",
        (True, False): "p3if_only",
        (False, True): "diff_only",
        (False, False): "neither_correct",
    }
    for row in rows:
        pair = (row["p3if"] == "correct", row["diff"] == "correct")
        counts[categories[pair]] += 1
    return {
        "pairs": len(rows),
        **counts,
        "difference_correct_cases": counts["p3if_only"] - counts["diff_only"],
    }


def score_review(case_manifest: Path, packet_manifest: Path, responses_dir: Path) -> _JSON:
    """Score fixed assignments and return a digest-bound deterministic receipt.

    Args:
        case_manifest: Exact frozen answer manifest supplied to packet preparation.
        packet_manifest: Exact registered packet inventory and assignment schedule.
        responses_dir: Directory holding one JSON array per reviewer session.

    Returns:
        Row scores, session input digests, matched counts, and domain/arm summaries.

    Raises:
        ValueError: The frozen key or packet schedule conflicts with the assignment.
        OSError: A file could not be read for a reason other than missing responses.
    """
    cases_raw, packets_raw = case_manifest.read_bytes(), packet_manifest.read_bytes()
    case_digest = sha256(cases_raw).hexdigest()
    by_id = _case_key(cases_raw)
    scheduled = _schedule(packets_raw, case_digest)
    scheduled_ids = {
        session: {row["case_id"] for row in scheduled if row["session"] == session}
        for session in SESSIONS
    }
    inputs = {
        session: _session_answers(responses_dir / f"{session}.json", scheduled_ids[session])
        for session in SESSIONS
    }
    rows = []
    for slot in scheduled:
        case = by_id[slot["case_id"]]
        answer, malformed, _ = inputs[slot["session"]]
        expected = _Response.model_validate(case["expected"])
        if expected.case_id != slot["case_id"]:
            raise ValueError("A frozen answer is filed under a different case ID.")
        grade = _describe_scores(
            expected, answer.get(expected.case_id), expected.case_id in malformed
        )
        comparison = grade["comparison"]
        rows.append(
            {
                **slot,
                "domain": case["domain"],
                "intervention": case["intervention"],
                "expected_classification": expected.classification,
                **grade,
                "false_declared_change": (
                    expected.classification == "encoding_only"
                    and comparison is not None
                    and comparison["reported_classification"] == "declared_change"
                ),
            }
        )
    pairs = _pair_rows(rows)
    domains = sorted({row["domain"] for row in rows})
    return {
        "schema_version": "p3if.held-out-reviewer-score.v1",
        "case_manifest_sha256": case_digest,
        "packet_manifest_sha256": sha256(packets_raw).hexdigest(),
        "sessions": {session: inputs[session][2] for session in SESSIONS},
        "rows": rows,
        "paired_rows": pairs,
        "counts": {
            condition: _counts([row for row in rows if row["condition"] == condition])
            for condition in _CONDITIONS
        },
        "paired_counts": _pair_counts(pairs),
        "domains": {
            domain: {
                "counts": {
                    condition: _counts(
                        [
                            row
                            for row in rows
                            if row["condition"] == condition and row["domain"] == domain
                        ]
                    )
                    for condition in _CONDITIONS
                },
                "paired_counts": _pair_counts([row for row in pairs if row["domain"] == domain]),
            }
            for domain in domains
        },
    }
