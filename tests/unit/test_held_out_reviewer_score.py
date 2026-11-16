"""Check fixed denominators and strict structured scoring for the masked study."""

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest

from p3if.held_out_reviewer_packets import PACKET_SCHEMA, SESSIONS, assignment_rows
from p3if.held_out_reviewer_score import score_review

_CASE_MANIFEST = Path(__file__).resolve().parents[2] / "docs/manuscript/held-out-case-manifest.json"


def _write(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def _packet_key(path):
    manifest = {
        "schema_version": PACKET_SCHEMA,
        "case_manifest_sha256": sha256(_CASE_MANIFEST.read_bytes()).hexdigest(),
        "assignments": assignment_rows(),
        "files": {},
    }
    _write(path, manifest)
    return manifest


def _case_answers():
    cases = json.loads(_CASE_MANIFEST.read_bytes())["cases"]
    return {case["case_id"]: case["expected"] for case in cases}


def test_exact_score_accepts_event_and_field_order_without_changing_pairs(tmp_path):
    packets = tmp_path / "packets.json"
    _packet_key(packets)
    key = _case_answers()
    responses = tmp_path / "answers"
    responses.mkdir()
    for session in SESSIONS:
        assignments = [row for row in assignment_rows() if row["session"] == session]
        answers = [deepcopy(key[row["case_id"]]) for row in reversed(assignments)]
        for answer in answers:
            answer["events"].reverse()
            for event in answer["events"]:
                event["fields"].reverse()
        _write(responses / f"{session}.json", answers)

    result = score_review(_CASE_MANIFEST, packets, responses)
    assert result["paired_counts"] == {
        "pairs": 16,
        "both_correct": 16,
        "p3if_only": 0,
        "diff_only": 0,
        "neither_correct": 0,
        "difference_correct_cases": 0,
    }
    assert {
        name: totals["paired_counts"]["pairs"] for name, totals in result["domains"].items()
    } == {
        "MathEducation": 8,
        "ScienceResearch": 8,
    }
    assert all(
        totals["correct"] == totals["assigned"] == 16 for totals in result["counts"].values()
    )
    assert result["packet_manifest_sha256"] == sha256(packets.read_bytes()).hexdigest()
    assert (
        result["sessions"]["S1"]["sha256"]
        == sha256((responses / "S1.json").read_bytes()).hexdigest()
    )
    assert result == score_review(_CASE_MANIFEST, packets, responses)


def test_missing_malformed_and_wrong_answers_stay_in_fixed_denominator(tmp_path):
    packets = tmp_path / "packets.json"
    _packet_key(packets)
    key = _case_answers()
    responses = tmp_path / "answers"
    responses.mkdir()

    bad = deepcopy(key["H10"])
    event = next(row for row in bad["events"] if row["change"] == "modified")
    event["fields"].append("unsupported_field")
    event["rewired"] = False
    event["after"]["scores"]["confidence"] = "explicit_null"

    repeated = deepcopy(key["H04"])
    repeated["events"].append(repeated["events"][0])
    _write(
        responses / "S1.json",
        [key["H01"], bad, repeated, key["H15"], key["H15"], key["H02"], {}],
    )
    _write(responses / "S2.json", [{**key["H09"], "classification": "declared_change"}])
    (responses / "S3.json").write_bytes(b'{"bad": NaN}')

    result = score_review(_CASE_MANIFEST, packets, responses)
    assert len(result["rows"]) == 32
    rows = {(row["session"], row["case_id"]): row for row in result["rows"]}
    assert rows["S1", "H01"]["result"] == "correct"
    assert rows["S1", "H10"]["result"] == "incorrect"
    assert rows["S1", "H10"]["comparison"]["event_disagreements"] == [
        {
            "kind": "relationship",
            "id": event["id"],
            "components": ["fields", "rewired", "after_scores"],
        }
    ]
    assert rows["S1", "H04"]["result"] == rows["S1", "H15"]["result"] == "malformed"
    assert rows["S1", "H16"]["result"] == "missing"
    assert rows["S2", "H09"]["false_declared_change"]
    assert {row["result"] for row in result["rows"] if row["session"] == "S3"} == {"malformed"}
    assert {row["result"] for row in result["rows"] if row["session"] == "S4"} == {"missing"}
    assert result["sessions"]["S1"]["unassignable_rows"] == 2
    assert result["sessions"]["S1"]["duplicate_case_ids"] == ["H15"]
    assert result["paired_counts"]["p3if_only"] == 1


def test_changed_packet_key_or_schedule_refuses_instead_of_rescoring(tmp_path):
    packets = tmp_path / "packets.json"
    original = _packet_key(packets)
    changed = deepcopy(original)
    changed["case_manifest_sha256"] = "0" * 64
    _write(packets, changed)
    with pytest.raises(ValueError, match="supplied held-out key"):
        score_review(_CASE_MANIFEST, packets, tmp_path)

    changed = deepcopy(original)
    changed["assignments"][0]["period"] = True
    _write(packets, changed)
    with pytest.raises(ValueError, match="frozen assignment schedule"):
        score_review(_CASE_MANIFEST, packets, tmp_path)
