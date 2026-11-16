"""Verify the frozen case builder without running the transition under test."""

import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

from p3if.held_out_cases import build_cases
from p3if.interchange import InterchangeError

ROOT = Path(__file__).resolve().parents[2]
METHODS = ROOT / "docs/manuscript"
SPECIFICATION = METHODS / "held-out-case-spec.json"
FROZEN = METHODS / "held-out-case-manifest.json"
FIXTURES = ROOT / "data/domains"


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def test_held_out_cases_reproduce_all_exact_spans(tmp_path):
    output = tmp_path / "cases"
    build_cases(FIXTURES, SPECIFICATION, output)
    artifact = (output / "case-manifest.json").read_bytes()
    assert artifact == FROZEN.read_bytes()
    manifest = json.loads(artifact)
    assert Counter(case["domain"] for case in manifest["cases"]) == {
        "ScienceResearch": 8,
        "MathEducation": 8,
    }
    assert all(case["before_sha256"] != case["after_sha256"] for case in manifest["cases"])
    assert sum(len(case["expected"]["events"]) for case in manifest["cases"]) == 48
    quotes = 0
    for case in manifest["cases"]:
        event_index = {(row["kind"], row["id"]): row for row in case["expected"]["events"]}
        assert event_index.keys() == {(row["kind"], row["id"]) for row in case["citations"]}
        for role in ("before", "after"):
            source = (output / case["case_id"] / f"{role}.json").read_bytes()
            document = json.loads(source)
            assert _sha(source) == case[f"{role}_sha256"]
            for citation in case["citations"]:
                event = event_index[citation["kind"], citation["id"]]
                span = citation[role]
                assert (span is None) == (event[role] is None)
                if span is None:
                    continue
                quotes += 1
                assert span["source_sha256"] == case[f"{role}_sha256"]
                quote = source[span["start_byte"] : span["end_byte"]]
                quote_text = source.decode("utf-8")[span["start_char"] : span["end_char"]]
                assert quote.decode("utf-8") == quote_text
                assert _sha(quote) == span["quote_sha256"]
                record = document
                for component in span["pointer"].split("/")[1:]:
                    record = (
                        record[int(component)] if isinstance(record, list) else record[component]
                    )
                assert json.loads(quote) == record
                assert record["id"] == citation["id"]
        if case["intervention"] == "rewire_add_remove":
            shifted = next(
                item
                for item in case["citations"]
                if all(item[role] for role in ("before", "after"))
            )
            assert shifted["before"]["pointer"] == "/relationships/0"
            assert shifted["after"]["pointer"] != shifted["before"]["pointer"]
            assert shifted["after"]["start_byte"] > shifted["after"]["start_char"]
    assert quotes == 78


def test_held_out_rejects_repeated_edits(tmp_path):
    specification = json.loads(SPECIFICATION.read_bytes())
    edits = specification["cases"][1]["edits"]
    edits.append(edits[0])
    candidate = tmp_path / "invalid.json"
    candidate.write_text(json.dumps(specification), encoding="utf-8")
    output = tmp_path / "cases"
    with pytest.raises(ValueError, match="Edit each record at most once"):
        build_cases(FIXTURES, candidate, output)
    assert not output.exists()


def test_held_out_rejects_dangling_endpoint(tmp_path):
    specification = json.loads(SPECIFICATION.read_bytes())
    specification["cases"][1]["edits"][0]["set"]["process_id"] = "unknown-process"
    candidate = tmp_path / "invalid.json"
    candidate.write_text(json.dumps(specification), encoding="utf-8")
    output = tmp_path / "cases"
    with pytest.raises(InterchangeError, match="absent or belongs to a different axis"):
        build_cases(FIXTURES, candidate, output)
    assert not output.exists()
