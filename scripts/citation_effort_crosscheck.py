"""Independently bind archived citation answers, chronology, and effort scores."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from statistics import median
import json

ROLES = ("before", "after")
RESULTS = ("correct", "incorrect", "missing", "malformed")
SPAN = (
    "source_sha256",
    "pointer",
    "start_char",
    "end_char",
    "start_byte",
    "end_byte",
    "quote_sha256",
)
EVIDENCE = {"open", "find", "search", "cite"}
EVENTS = EVIDENCE | {"schedule", "start", "submit"}
FIELDS = {
    "schema_version",
    "case_id",
    "action",
    "resource",
    "side",
    "status",
    "hits",
    "response_bytes",
    "answer_sha256",
    "started_at_utc",
    "finished_at_utc",
    "started_monotonic_ns",
    "finished_monotonic_ns",
}
MISSING = object()


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate JSON object member")
    return result


def invalid_constant(_token):
    raise ValueError("Nonstandard JSON number")


def parse(raw):
    return json.loads(raw.decode(), object_pairs_hook=unique, parse_constant=invalid_constant)


def digest(raw):
    return sha256(raw).hexdigest() if raw is not None else None


def utc(value):
    observed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert observed.tzinfo is not None
    return observed.astimezone(timezone.utc)


def verdict(expected, actual):
    if actual is MISSING:
        return "missing", []
    if actual is None:
        return ("correct", []) if expected is None else ("incorrect", ["presence"])
    if not isinstance(actual, dict) or set(actual) != set(SPAN):
        return "malformed", []
    if any(
        (not isinstance(actual[name], int) or isinstance(actual[name], bool) or actual[name] < 0)
        for name in SPAN[2:6]
    ):
        return "malformed", []
    if any(not isinstance(actual[name], str) for name in (SPAN[0], SPAN[1], SPAN[-1])):
        return "malformed", []
    if expected is None:
        return "incorrect", ["presence"]
    mismatches = [field for field in SPAN if expected[field] != actual[field]]
    return ("incorrect", mismatches) if mismatches else ("correct", [])


def grade(case, raw):
    expected = {(row["kind"], row["id"]): row for row in case["citations"]}
    assert len(expected) == len(case["citations"]) > 0
    rows = {}
    malformed = False
    if raw is not None:
        try:
            answer = parse(raw)
            if (
                set(answer) != {"case_id", "citations"}
                or answer["case_id"] != case["case_id"]
                or not isinstance(answer["citations"], list)
            ):
                raise ValueError("Unexpected case envelope")
            for entry in answer["citations"]:
                identity = (entry["kind"], entry["id"])
                if (
                    identity in rows
                    or identity not in expected
                    or set(entry) - {"kind", "id", "before", "after"}
                ):
                    raise ValueError("Wrong question inventory")
                rows[identity] = entry
        except (ValueError, TypeError, KeyError):
            malformed = True
    for (kind, identity), question in expected.items():
        for role in ROLES:
            value = question[role]
            status, errors = (
                ("malformed", [])
                if malformed
                else verdict(value, rows.get((kind, identity), {}).get(role, MISSING))
            )
            yield {
                "kind": kind,
                "id": identity,
                "side": role,
                "expected_present": value is not None,
                "result": status,
                "mismatched_fields": errors,
            }


def actions(folder, case_ids, registration, scoring):
    path = folder / "actions.jsonl"
    by_case = defaultdict(list)
    if not path.is_file():
        return by_case, {
            "status": "missing",
            "sha256": None,
            "schedule_operations": None,
        }
    raw = path.read_bytes()
    lines = raw.splitlines()
    assert lines, f"Empty {folder.name} log"
    sequence = {case_id: number for number, case_id in enumerate(case_ids)}
    schedule = 0
    prior_position = -1
    previous_end = 0
    for line in lines:
        entry = parse(line)
        assert set(entry) == FIELDS, f"Unexpected {folder.name} action fields"
        assert entry["schema_version"] == "p3if.citation-review-action.v1"
        action, case_id = entry["action"], entry["case_id"]
        begin, end = entry["started_monotonic_ns"], entry["finished_monotonic_ns"]
        assert action in EVENTS and entry["status"] in {"ok", "no_hits", "error"}
        assert (
            all(isinstance(value, int) and not isinstance(value, bool) for value in (begin, end))
            and 0 < begin <= end
            and begin >= previous_end
        )
        assert (
            registration <= utc(entry["started_at_utc"]) <= utc(entry["finished_at_utc"]) < scoring
        )
        previous_end = end
        if action == "schedule":
            assert case_id is None
            schedule += 1
            continue
        assert case_id in sequence and sequence[case_id] >= prior_position
        prior_position = sequence[case_id]
        by_case[case_id].append(entry)
    trace = {"status": "parsed", "sha256": digest(raw), "schedule_operations": schedule}
    return by_case, trace


def effort(entries, answer_hash):
    if not entries:
        return {"status": "missing"}
    operations = [row for row in entries if row["action"] in EVIDENCE]
    submits = [row for row in entries if row["action"] == "submit" and row["status"] == "ok"]
    if answer_hash is None or not operations or len(submits) != 1:
        return {"status": "invalid"}
    submit = submits[0]
    assert submit["answer_sha256"] == answer_hash, "Submission hash differs from archived answer"
    assert entries[0]["action"] == "start" and entries[0]["status"] == "ok"
    assert sum(entry["action"] == "start" for entry in entries) == 1
    assert operations[-1]["finished_monotonic_ns"] <= submit["started_monotonic_ns"]
    elapsed = submit["finished_monotonic_ns"] - operations[0]["started_monotonic_ns"]
    return {
        "status": "measured",
        "evidence_operations": len(operations),
        "operation_counts": dict(Counter(operation["action"] for operation in operations)),
        "unsuccessful_operations": sum(operation["status"] != "ok" for operation in operations),
        "elapsed_ms": elapsed // 1_000_000,
    }


def counts(sides):
    return {
        "assigned": len(sides),
        **{status: sum(row["result"] == status for row in sides) for status in RESULTS},
    }


def summarize(rows):
    sides = [side for row in rows for side in row["sides"]]
    measured = [row["effort"] for row in rows if row["effort"]["status"] == "measured"]
    return {
        "cases": len(rows),
        "complete_correct_cases": sum(
            all(side["result"] == "correct" for side in row["sides"]) for row in rows
        ),
        "accuracy": counts(sides),
        "present": counts([side for side in sides if side["expected_present"]]),
        "absent": counts([side for side in sides if not side["expected_present"]]),
        "effort": {
            "measured": len(measured),
            "unmeasured": len(rows) - len(measured),
            "median_operations": median(row["evidence_operations"] for row in measured)
            if measured
            else None,
            "median_elapsed_ms": median(row["elapsed_ms"] for row in measured)
            if measured
            else None,
        },
    }


def matched(rows, workflow_arms):
    by_case = defaultdict(dict)
    for row in rows:
        by_case[row["case_id"]][row["condition"]] = row
    side_groups = (
        "both_correct",
        f"{workflow_arms[0]}_only",
        f"{workflow_arms[1]}_only",
        "neither_correct",
    )
    totals = {name: 0 for name in side_groups}
    effort_rows = []
    for case_id, arms in sorted(by_case.items()):
        left, right = (arms[arm] for arm in workflow_arms)

        def sides(row):
            return {
                (item["kind"], item["id"], item["side"]): item["result"] == "correct"
                for item in row["sides"]
            }

        a, b = sides(left), sides(right)
        assert a.keys() == b.keys()
        for key in a:
            totals[side_groups[(not a[key]) * 2 + (not b[key])]] += 1
        first, second = left["effort"], right["effort"]
        if first["status"] == second["status"] == "measured":
            operations = first["evidence_operations"] - second["evidence_operations"]
            elapsed = first["elapsed_ms"] - second["elapsed_ms"]
        else:
            operations, elapsed = None, None
        effort_rows.append(
            {
                "case_id": case_id,
                "operation_difference": operations,
                "elapsed_ms_difference": elapsed,
            }
        )
    differences = [row for row in effort_rows if row["operation_difference"] is not None]
    return {
        "sides": totals,
        "cases": effort_rows,
        "measured_case_pairs": len(differences),
        "median_operation_difference": median(row["operation_difference"] for row in differences)
        if differences
        else None,
        "median_elapsed_ms_difference": median(row["elapsed_ms_difference"] for row in differences)
        if differences
        else None,
    }


def main() -> None:
    """Cross-check an archived batch and write its independent result."""
    if not __debug__:
        raise SystemExit("Run the independent cross-check without optimization.")
    parser = ArgumentParser(description=__doc__)
    for name in ("case_manifest", "packet_manifest", "submissions", "score"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--registered-utc", required=True)
    parser.add_argument("--scoring-started-utc", required=True)
    parser.add_argument("--navigation-ablation", action="store_true")
    args = parser.parse_args()
    workflow_arms = (
        ("navigation", "no_navigation") if args.navigation_ablation else ("p3if", "diff")
    )
    registration, scoring = utc(args.registered_utc), utc(args.scoring_started_utc)
    assert registration < scoring
    case_raw, packet_raw, score_raw = (
        path.read_bytes() for path in (args.case_manifest, args.packet_manifest, args.score)
    )
    cases, packets, score = map(parse, (case_raw, packet_raw, score_raw))
    assert digest(case_raw) == packets["case_manifest_sha256"] == score["case_manifest_sha256"]
    assert digest(packet_raw) == score["packet_manifest_sha256"]
    case_index = {case["case_id"]: case for case in cases["cases"]}
    assert len(case_index) == 16
    assignments = defaultdict(list)
    for slot in packets["assignments"]:
        assignments[slot["session"]].append(slot)
    assert set(assignments) == {"S1", "S2", "S3", "S4"}
    expected_rows = {}
    for session, slots in assignments.items():
        ids = [slot["case_id"] for slot in slots]
        assert len(ids) == len(set(ids)) == 8
        folder = args.submissions / session
        by_case, trace = actions(folder, ids, registration, scoring)
        assert trace == score["sessions"][session], f"Action ledger differs for {session}"
        for slot in slots:
            case_id = slot["case_id"]
            case = case_index[case_id]
            path = folder / f"{case_id}.json"
            raw = path.read_bytes() if path.is_file() else None
            graded = list(grade(case, raw))
            expected_rows[session, case_id] = {
                **slot,
                "domain": case["domain"],
                "answer_sha256": digest(raw),
                "complete_correct": all(side["result"] == "correct" for side in graded),
                "sides": graded,
                "effort": effort(by_case[case_id], digest(raw)),
            }
    assert len(expected_rows) == len(score["rows"]) == 32
    assert all(expected_rows[row["session"], row["case_id"]] == row for row in score["rows"])
    rows = list(expected_rows.values())
    assert score["workflows"] == {
        arm: summarize([row for row in rows if row["condition"] == arm]) for arm in workflow_arms
    }
    assert score["paired"] == matched(rows, workflow_arms)
    for domain in {row["domain"] for row in rows}:
        subset = [row for row in rows if row["domain"] == domain]
        expected = {
            arm: summarize([row for row in subset if row["condition"] == arm])
            for arm in workflow_arms
        }
        assert score["domains"][domain] == {**expected, "paired": matched(subset, workflow_arms)}
    print(
        json.dumps(
            {
                "score_sha256": digest(score_raw),
                "chronological_action_ledgers": sum(
                    entry["status"] == "parsed" for entry in score["sessions"].values()
                ),
                "scheduled_cases": len(rows),
                "scheduled_sides": sum(len(row["sides"]) for row in rows),
                "matched": score["paired"],
                "workflow_accuracy": {
                    arm: score["workflows"][arm]["accuracy"] for arm in workflow_arms
                },
                "workflow_effort": {
                    arm: score["workflows"][arm]["effort"] for arm in workflow_arms
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
