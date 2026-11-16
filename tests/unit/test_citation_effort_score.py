"""Controls for exact citation grading and operational effort."""

import json
from hashlib import sha256

from p3if.citation_effort_score import _effort, _grade, _read_actions


def _fixture():
    span = {
        "source_sha256": "a" * 64,
        "pointer": "/relationships/3",
        "start_char": 4,
        "end_char": 17,
        "start_byte": 7,
        "end_byte": 20,
        "quote_sha256": "b" * 64,
    }
    citation = {"kind": "relationship", "id": "ref", "before": span, "after": None}
    return citation, {"case_id": "C01", "citations": [citation]}


def _encode(value):
    return json.dumps(value).encode()


def test_distinguishes_explicit_absence_from_omission_and_wrong_range():
    citation, case = _fixture()
    assert [item["result"] for item in _grade(case, _encode(case))] == ["correct", "correct"]
    wrong = {**citation["before"], "start_byte": 4}
    answer = {"case_id": "C01", "citations": [{**citation, "before": wrong}]}
    answer["citations"][0].pop("after")
    first, second = _grade(case, _encode(answer))
    assert (first["result"], first["mismatched_fields"], second["result"]) == (
        "incorrect",
        ["start_byte"],
        "missing",
    )
    answer["citations"].append(answer["citations"][0])
    assert {item["result"] for item in _grade(case, _encode(answer))} == {"malformed"}


def test_effort_counts_failed_search_and_binds_submission_bytes(tmp_path):
    _, case = _fixture()
    answer = _encode(case)
    events = [
        ("schedule", None, 1, 2, "ok"),
        ("start", "C01", 2, 3, "ok"),
        ("open", "C01", 5_000_000, 6_000_000, "ok"),
        ("find", "C01", 7_000_000, 8_000_000, "no_hits"),
        ("submit", "C01", 10_000_000, 11_000_000, "ok"),
    ]
    log = tmp_path / "actions.jsonl"
    with log.open("w", encoding="utf-8") as output:
        for action, case_id, start, end, status in events:
            output.write(
                json.dumps(
                    {
                        "schema_version": "p3if.citation-review-action.v1",
                        "action": action,
                        "case_id": case_id,
                        "status": status,
                        "started_monotonic_ns": start,
                        "finished_monotonic_ns": end,
                        "started_at_utc": "2026-11-15T00:00:00Z",
                        "finished_at_utc": "2026-11-15T00:00:00Z",
                        "answer_sha256": sha256(answer).hexdigest() if action == "submit" else None,
                    }
                )
                + "\n"
            )
    rows, trace = _read_actions(log, ["C01"])
    assert trace["schedule_operations"] == 1
    assert _effort(rows["C01"], answer) == {
        "status": "measured",
        "evidence_operations": 2,
        "operation_counts": {"open": 1, "find": 1},
        "unsuccessful_operations": 1,
        "elapsed_ms": 6,
    }
    assert _effort(rows["C01"], answer + b" ") == {"status": "invalid"}
