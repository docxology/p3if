"""Prepare masked reviewer packets and score the registered two-domain pilot.

Packet construction verifies the source digests and never copies the intervention
key. Scoring uses the independently frozen key and keeps every assignment in the
accuracy denominator, including missing or malformed answers.
"""

from __future__ import annotations

import json
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any, ClassVar, Literal, Optional

from pydantic import BaseModel, ConfigDict, ValidationError

from .interchange import load_interchange
from .interchange_audit import audit_interchange
from .interchange_transition import transition_interchange

Object = dict[str, Any]
ScoreState = Literal["omitted", "explicit_null", "reported_zero", "reported_nonzero"]
_ASSIGNMENT = {"T1": ("p3if", "diff"), "T2": ("diff", "p3if")}
_PANELS = ("A", "B")
_AXES = ("properties", "processes", "perspectives")
_INSTRUCTIONS = """# Review instructions

Review each case in the order in `schedule.json`. Read the additional report(s)
and use the two original snapshots and ID-to-name lookup as needed. Describe what
the snapshots declare. Report one object per case in a JSON array.

Each case object has `case_id`, `classification` and `events`. Classify exact
identical bytes as `identical_bytes`, differing bytes with the same declarations
as `encoding_only`, and differing declarations as `declared_change`.

For each changed relationship give `id`, `change` (`added`, `removed` or
`modified`), `fields` (only for modifications, otherwise `[]`), `before` and
`after`. Give each present side as an object with `endpoints` (property ID,
process ID, perspective ID, in that order) and `scores` (keys `strength` and
`confidence`). For each score use `omitted`, `explicit_null`, `reported_zero`
or `reported_nonzero`. The state for an absent relationship is null. For an
exact copy or a re-encoding use `events: []`. Compare all declared fields
including their presence, and give each changed stable ID once.
"""


class _ClosedModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", strict=True)


class _Scores(_ClosedModel):
    strength: ScoreState
    confidence: ScoreState


class _Side(_ClosedModel):
    endpoints: list[Optional[str]]
    scores: _Scores


class _Event(_ClosedModel):
    id: str
    change: Literal["added", "removed", "modified"]
    fields: list[str]
    before: Optional[_Side]
    after: Optional[_Side]


class _Response(_ClosedModel):
    case_id: str
    classification: Literal["identical_bytes", "encoding_only", "declared_change"]
    events: list[_Event]


def _read(path: Path) -> Any:
    def unique(pairs: list[tuple[str, Any]]) -> Object:
        value = dict(pairs)
        if len(value) != len(pairs):
            raise ValueError(f"Duplicate JSON key in {path.name}.")
        return value

    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def _write(path: Path, data: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        )
        stream.write("\n")


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _case_index(manifest: Object) -> dict[str, Object]:
    if manifest["schema_version"] != "p3if.reviewer-case-manifest.v1":
        raise ValueError("Unsupported case manifest version.")
    rows = manifest["cases"]
    by_id = {row["case_id"]: row for row in rows}
    ids = [case_id for panel in _PANELS for case_id in manifest["panels"][panel]]
    if (
        len(rows) != 12
        or len(by_id) != 12
        or any(len(manifest["panels"][panel]) != 6 for panel in _PANELS)
        or set(ids) != set(by_id)
    ):
        raise ValueError("The two registered panels must allocate each case exactly once.")
    if any(case_id != f"R{index:02d}" for index, case_id in enumerate(sorted(by_id), 1)):
        raise ValueError("Invalid registered case IDs.")
    return by_id


def _records(document: Object) -> dict[str, Object]:
    rows = document["relationships"]
    records = {row["id"]: row for row in rows}
    if len(records) != len(rows):
        raise ValueError("Snapshot has duplicate relationship IDs.")
    return records


def _diff(before: Object, after: Object, before_sha: str, after_sha: str) -> Object:
    first, second = _records(before), _records(after)
    changes: Object = {}
    for identity in sorted(first.keys() | second.keys()):
        old, new = first.get(identity), second.get(identity)
        if old is None:
            changes[identity] = {"added": new}
        elif new is None:
            changes[identity] = {"removed": old}
        elif old != new:
            changes[identity] = {
                "fields": {
                    field: {
                        "before": {"value": old[field]} if field in old else {},
                        "after": {"value": new[field]} if field in new else {},
                    }
                    for field in sorted(old.keys() | new.keys())
                    if field not in old or field not in new or old[field] != new[field]
                }
            }
    return {"before_sha256": before_sha, "after_sha256": after_sha, "relationships": changes}


def _packet(case: Object, sources: Path, destination: Path, condition: str) -> None:
    before, after = ((sources / f"{side}.json").read_bytes() for side in ("before", "after"))
    before_sha, after_sha = _digest(before), _digest(after)
    if (before_sha, after_sha) != (case["before_sha256"], case["after_sha256"]):
        raise ValueError(f"Source changed for {case['case_id']}.")
    old, new = json.loads(before), json.loads(after)
    destination.mkdir()
    (destination / "before.json").write_bytes(before)
    (destination / "after.json").write_bytes(after)
    _write(
        destination / "lookup.json",
        {
            axis: {row["id"]: row["name"] for side in (old, new) for row in side[axis]}
            for axis in _AXES
        },
    )
    if condition == "p3if":
        _write(destination / "audit.json", audit_interchange(before, after).model_dump(mode="json"))
        transition = transition_interchange(load_interchange(before), load_interchange(after))
        _write(destination / "transition.json", transition.model_dump(mode="json"))
    else:
        _write(destination / "diff.json", _diff(old, new, before_sha, after_sha))


def prepare_packets(cases: Path, output: Path) -> None:
    """Create two isolated session folders and a deterministic SHA-256 inventory.

    Args:
        cases: Generated cases directory containing the frozen case manifest.
        output: New directory in which to write packets and their inventory.
    """
    manifest_path = cases / "case-manifest.json"
    manifest = _read(manifest_path)
    by_id = _case_index(manifest)
    output.mkdir()
    for session, conditions in _ASSIGNMENT.items():
        root = output / session
        root.mkdir()
        (root / "instructions.md").write_bytes(_INSTRUCTIONS.encode("utf-8"))
        schedule = []
        for period, (panel, condition) in enumerate(zip(_PANELS, conditions), start=1):
            for case_id in manifest["panels"][panel]:
                folder = f"{period}/{case_id}"
                (root / folder).parent.mkdir(exist_ok=True)
                _packet(by_id[case_id], cases / case_id, root / folder, condition)
                schedule.append({"period": period, "case_id": case_id, "folder": folder})
        _write(root / "schedule.json", schedule)
    files = {
        path.relative_to(output).as_posix(): _digest(path.read_bytes())
        for path in sorted(output.rglob("*"))
        if path.is_file()
    }
    _write(
        output / "packet-manifest.json",
        {
            "schema_version": "p3if.reviewer-study-packets.v1",
            "case_manifest_sha256": _digest(manifest_path.read_bytes()),
            "files": files,
        },
    )


def _normalized(response: _Response) -> Object:
    value = response.model_dump(mode="json")
    for event in value["events"]:
        event["fields"].sort()
    value["events"].sort(key=lambda event: event["id"])
    return value


def _score_row(expected: _Response, answer: Any) -> str:
    if answer is None:
        return "missing"
    try:
        received = _Response.model_validate(answer)
    except ValidationError:
        return "malformed"
    return "correct" if _normalized(received) == _normalized(expected) else "incorrect"


def _answers(responses: Path, session: str, ids: set[str]) -> dict[str, Any]:
    path = responses / f"{session}.json"
    if not path.exists():
        return {}
    raw = _read(path)
    if not isinstance(raw, list):
        raise ValueError(f"Expected a response array for {session}.")
    indexed: dict[str, Any] = {}
    for row in raw:
        case_id = row.get("case_id") if isinstance(row, dict) else None
        if not isinstance(case_id, str) or case_id not in ids or case_id in indexed:
            raise ValueError(f"Missing, unknown, or duplicate case ID in {session}.")
        indexed[case_id] = row
    return indexed


def score_pilot(manifest_path: Path, responses: Path) -> Object:
    """Score both fixed pilot assignments, including unanswered cases.

    Args:
        manifest_path: Frozen answer and case manifest.
        responses: Directory of T1.json and T2.json reviewer response arrays.

    Returns:
        Row-level statuses and descriptive counts, with no human-study inference.
    """
    manifest = _read(manifest_path)
    by_id = _case_index(manifest)
    rows = []
    for session, conditions in _ASSIGNMENT.items():
        answers = _answers(responses, session, set(by_id))
        for period, (panel, condition) in enumerate(zip(_PANELS, conditions), start=1):
            for case_id in manifest["panels"][panel]:
                case = by_id[case_id]
                expected = _Response.model_validate(case["expected"])
                answer = answers.get(case_id)
                rows.append(
                    {
                        "session": session,
                        "period": period,
                        "condition": condition,
                        "case_id": case_id,
                        "domain": case["domain"],
                        "intervention": case["intervention"],
                        "result": _score_row(expected, answer),
                        "false_declared_change": (
                            expected.classification == "encoding_only"
                            and isinstance(answer, dict)
                            and answer.get("classification") == "declared_change"
                        ),
                    }
                )
    return {
        "schema_version": "p3if.reviewer-study-score.v1",
        "case_manifest_sha256": _digest(manifest_path.read_bytes()),
        "response_sha256": {
            path.stem: _digest(path.read_bytes())
            for session in _ASSIGNMENT
            if (path := responses / f"{session}.json").is_file()
        },
        "rows": rows,
        "counts": {
            condition: dict(Counter(row["result"] for row in rows if row["condition"] == condition))
            for condition in ("p3if", "diff")
        },
    }
