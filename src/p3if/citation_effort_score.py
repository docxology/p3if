"""Score frozen citation answers and measure effort from instrumented review logs."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from statistics import median
from typing import Any

from .held_out_reviewer_score import _strict_json

Object = dict[str, Any]
_SESSIONS = ("S1", "S2", "S3", "S4")
_ROLES = ("before", "after")
_SPAN_FIELDS = (
    "source_sha256",
    "pointer",
    "start_char",
    "end_char",
    "start_byte",
    "end_byte",
    "quote_sha256",
)
_EVIDENCE_ACTIONS = frozenset(("open", "find", "search", "cite"))
_ACTIONS = _EVIDENCE_ACTIONS | {"schedule", "start", "submit"}
_RESULTS = ("correct", "incorrect", "missing", "malformed")
_ABSENT = object()


@dataclass(frozen=True)
class _StudyDesign:
    arms: tuple[str, str]
    case_prefix: str
    packet_schema: str
    score_schema: str


_CITATION_EFFORT = _StudyDesign(
    ("p3if", "diff"), "C", "p3if.citation-effort-packets.v1", "p3if.citation-effort-score.v1"
)
_NAVIGATION_ABLATION = _StudyDesign(
    ("navigation", "no_navigation"),
    "A",
    "p3if.navigation-ablation-packets.v1",
    "p3if.navigation-ablation-score.v1",
)


def _hash(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _index(rows: list[Object]) -> dict[tuple[str, str], Object]:
    by_key = {(row["kind"], row["id"]): row for row in rows}
    if len(by_key) != len(rows):
        raise ValueError("Duplicate question identity")
    return by_key


def _integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _span(value: Any) -> bool:
    if not isinstance(value, dict) or set(value) != set(_SPAN_FIELDS):
        return False
    return all(_integer(value[field]) and value[field] >= 0 for field in _SPAN_FIELDS[2:6]) and all(
        isinstance(value[field], str) for field in ("source_sha256", "pointer", "quote_sha256")
    )


def _grade_side(expected: Object | None, candidate: Any) -> tuple[str, list[str]]:
    if candidate is _ABSENT:
        return "missing", []
    if candidate is None:
        return ("correct", []) if expected is None else ("incorrect", ["presence"])
    if not _span(candidate):
        return "malformed", []
    if expected is None:
        return "incorrect", ["presence"]
    differences = [field for field in _SPAN_FIELDS if expected[field] != candidate[field]]
    return ("incorrect", differences) if differences else ("correct", [])


def _grade(case: Object, raw: bytes | None) -> list[Object]:
    expected = _index(case["citations"])
    actual: dict[tuple[str, str], Object] = {}
    malformed = False
    if raw is not None:
        try:
            value = _strict_json(raw)
            if (
                not isinstance(value, dict)
                or set(value) != {"case_id", "citations"}
                or value["case_id"] != case["case_id"]
                or not isinstance(value["citations"], list)
            ):
                raise ValueError("Invalid case response")
            actual = _index(value["citations"])
            if not actual.keys() <= expected.keys() or any(
                not row.keys() <= {"kind", "id", "before", "after"} for row in actual.values()
            ):
                raise ValueError("Unexpected question or field")
        except (KeyError, TypeError, ValueError, AttributeError):
            malformed = True

    sides = []
    for (kind, identity), evidence in expected.items():
        answer = actual.get((kind, identity), {})
        for role in _ROLES:
            proof = evidence[role]
            status, fields = (
                ("malformed", []) if malformed else _grade_side(proof, answer.get(role, _ABSENT))
            )
            sides.append(
                {
                    "kind": kind,
                    "id": identity,
                    "side": role,
                    "expected_present": proof is not None,
                    "result": status,
                    "mismatched_fields": fields,
                }
            )
    return sides


def _read_actions(path: Path, assigned: list[str]) -> tuple[dict[str, list[Object]], Object]:
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return {}, {"status": "missing", "sha256": None, "schedule_operations": None}
    provenance = {"sha256": _hash(raw), "schedule_operations": None}
    try:
        events = [_strict_json(line) for line in raw.splitlines()]
        if not events:
            raise ValueError("Empty action log")
        by_case: dict[str, list[Object]] = {}
        position = {case_id: number for number, case_id in enumerate(assigned)}
        last_position = -1
        last_end = 0
        schedules = 0
        for event in events:
            action = event["action"]
            start, end = event["started_monotonic_ns"], event["finished_monotonic_ns"]
            if (
                event["schema_version"] != "p3if.citation-review-action.v1"
                or action not in _ACTIONS
                or (
                    action == "submit"
                    and event["status"] == "ok"
                    and not isinstance(event["answer_sha256"], str)
                )
                or not all(
                    isinstance(event[field], str) for field in ("started_at_utc", "finished_at_utc")
                )
                or event["status"] not in {"ok", "no_hits", "error"}
                or not _integer(start)
                or not _integer(end)
                or not 0 < start <= end
                or start < last_end
            ):
                raise ValueError("Malformed action")
            last_end = end
            case_id = event["case_id"]
            if action == "schedule":
                if case_id is not None:
                    raise ValueError("Schedule is not a case action")
                schedules += 1
                continue
            if position[case_id] < last_position:
                raise ValueError("Actions outside the registered sequence")
            last_position = position[case_id]
            by_case.setdefault(case_id, []).append(event)
    except (AttributeError, KeyError, TypeError, ValueError):
        return {}, {"status": "invalid", **provenance}
    return by_case, {"status": "parsed", **provenance, "schedule_operations": schedules}


def _effort(actions: list[Object], raw: bytes | None) -> Object:
    evidence = [row for row in actions if row["action"] in _EVIDENCE_ACTIONS]
    submits = [row for row in actions if row["action"] == "submit" and row["status"] == "ok"]
    if not actions:
        return {"status": "missing"}
    if (
        raw is None
        or not evidence
        or len(submits) != 1
        or submits[0]["answer_sha256"] != _hash(raw)
        or submits[0]["started_monotonic_ns"] < evidence[-1]["finished_monotonic_ns"]
    ):
        return {"status": "invalid"}
    elapsed = submits[0]["finished_monotonic_ns"] - evidence[0]["started_monotonic_ns"]
    return {
        "status": "measured",
        "evidence_operations": len(evidence),
        "operation_counts": dict(sorted(Counter(row["action"] for row in evidence).items())),
        "unsuccessful_operations": sum(row["status"] != "ok" for row in evidence),
        "elapsed_ms": elapsed // 1_000_000,
    }


def _counts(sides: list[Object]) -> Object:
    values = Counter(row["result"] for row in sides)
    return {"assigned": len(sides), **{outcome: values[outcome] for outcome in _RESULTS}}


def _effort_summary(rows: list[Object]) -> Object:
    summaries = [row["effort"] for row in rows if row["effort"]["status"] == "measured"]
    return {
        "measured": len(summaries),
        "unmeasured": len(rows) - len(summaries),
        "median_operations": (
            median([row["evidence_operations"] for row in summaries]) if summaries else None
        ),
        "median_elapsed_ms": (
            median([row["elapsed_ms"] for row in summaries]) if summaries else None
        ),
    }


def _summary(rows: list[Object]) -> Object:
    sides = [side for row in rows for side in row["sides"]]
    return {
        "cases": len(rows),
        "complete_correct_cases": sum(row["complete_correct"] for row in rows),
        "accuracy": _counts(sides),
        "present": _counts([row for row in sides if row["expected_present"]]),
        "absent": _counts([row for row in sides if not row["expected_present"]]),
        "effort": _effort_summary(rows),
    }


def _paired(rows: list[Object], arms: tuple[str, str]) -> Object:
    matched = {(row["case_id"], row["condition"]): row for row in rows}
    counts: Counter[str] = Counter()
    operation_differences: list[int] = []
    elapsed_differences: list[int] = []
    pairs = []
    first_only, second_only = (f"{arm}_only" for arm in arms)
    for case_id in sorted({row["case_id"] for row in rows}):
        left, right = (matched[case_id, arm] for arm in arms)
        for a, b in zip(left["sides"], right["sides"]):
            first, second = a["result"] == "correct", b["result"] == "correct"
            label = (
                "both_correct"
                if first and second
                else first_only if first else second_only if second else "neither_correct"
            )
            counts[label] += 1
        ea, eb = left["effort"], right["effort"]
        pair = {"case_id": case_id, "operation_difference": None, "elapsed_ms_difference": None}
        if ea["status"] == eb["status"] == "measured":
            operation = ea["evidence_operations"] - eb["evidence_operations"]
            elapsed = ea["elapsed_ms"] - eb["elapsed_ms"]
            operation_differences.append(operation)
            elapsed_differences.append(elapsed)
            pair.update(operation_difference=operation, elapsed_ms_difference=elapsed)
        pairs.append(pair)
    return {
        "sides": {
            name: counts[name]
            for name in ("both_correct", first_only, second_only, "neither_correct")
        },
        "measured_case_pairs": len(operation_differences),
        "median_operation_difference": (
            median(operation_differences) if operation_differences else None
        ),
        "median_elapsed_ms_difference": (
            median(elapsed_differences) if elapsed_differences else None
        ),
        "cases": pairs,
    }


def score_study(case_manifest: Path, packet_manifest: Path, submissions: Path) -> Object:
    """Bind and score every scheduled citation side and every usable effort trace.

    Args:
        case_manifest: Frozen cases and citation reference.
        packet_manifest: Frozen assignment and packet inventory.
        submissions: Directory with one folder of raw responses and logs per session.

    Returns:
        Deterministic row, domain, workflow and matched summaries.
    """
    return _score_study(case_manifest, packet_manifest, submissions, _CITATION_EFFORT)


def score_navigation_ablation(
    case_manifest: Path, packet_manifest: Path, submissions: Path
) -> Object:
    """Score the frozen navigation ablation using the exact citation and effort rules.

    Args:
        case_manifest: Frozen case citations for the navigation ablation.
        packet_manifest: Frozen crossover assignment and packet inventory.
        submissions: Original per-session responses and reader action ledgers.

    Returns:
        Deterministic accuracy and effort summaries for both ablation arms.
    """
    return _score_study(case_manifest, packet_manifest, submissions, _NAVIGATION_ABLATION)


def _score_study(
    case_manifest: Path, packet_manifest: Path, submissions: Path, design: _StudyDesign
) -> Object:
    case_raw, packet_raw = case_manifest.read_bytes(), packet_manifest.read_bytes()
    case_key, packet = _strict_json(case_raw), _strict_json(packet_raw)
    case_hash = _hash(case_raw)
    cases = {case["case_id"]: case for case in case_key["cases"]}
    assignments = packet["assignments"]
    if (
        case_key["schema_version"] != "p3if.citation-case-manifest.v1"
        or packet["schema_version"] != design.packet_schema
        or packet["case_manifest_sha256"] != case_hash
        or set(cases) != {f"{design.case_prefix}{i:02d}" for i in range(1, 17)}
        or len(case_key["cases"]) != 16
        or Counter((row["case_id"], row["condition"]) for row in assignments)
        != {(case_id, arm): 1 for case_id in cases for arm in design.arms}
        or Counter(row["session"] for row in assignments) != {session: 8 for session in _SESSIONS}
    ):
        raise ValueError("Packet assignments or case identities drifted")
    rows = []
    traces = {}
    for session in _SESSIONS:
        owned = [row for row in assignments if row["session"] == session]
        folder = submissions / session
        actions, trace = _read_actions(folder / "actions.jsonl", [row["case_id"] for row in owned])
        traces[session] = trace
        for assignment in owned:
            case_id = assignment["case_id"]
            case = cases[case_id]
            try:
                raw: bytes | None = (folder / f"{case_id}.json").read_bytes()
            except FileNotFoundError:
                raw = None
            sides = _grade(case, raw)
            effort = _effort(actions.get(case_id, []), raw)
            if trace["status"] == "invalid":
                effort = {"status": "invalid"}
            rows.append(
                {
                    **assignment,
                    "domain": case["domain"],
                    "answer_sha256": _hash(raw) if raw is not None else None,
                    "complete_correct": all(side["result"] == "correct" for side in sides),
                    "sides": sides,
                    "effort": effort,
                }
            )
    return {
        "schema_version": design.score_schema,
        "case_manifest_sha256": case_hash,
        "packet_manifest_sha256": _hash(packet_raw),
        "sessions": traces,
        "rows": rows,
        "workflows": {
            arm: _summary([row for row in rows if row["condition"] == arm]) for arm in design.arms
        },
        "paired": _paired(rows, design.arms),
        "domains": {
            domain: {
                **{
                    arm: _summary(
                        [row for row in rows if row["domain"] == domain and row["condition"] == arm]
                    )
                    for arm in design.arms
                },
                "paired": _paired([row for row in rows if row["domain"] == domain], design.arms),
            }
            for domain in sorted({row["domain"] for row in rows})
        },
    }
