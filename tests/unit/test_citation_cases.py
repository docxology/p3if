"""Check the study key against the original source bytes and document structure."""

import json
from collections import Counter
from hashlib import sha256
from pathlib import Path

import pytest

from p3if.citation_cases import build_cases

ROOT = Path(__file__).resolve().parents[2]
METHODS = ROOT / "docs/manuscript"
SPECIFICATION = METHODS / "citation-case-spec.json"
FROZEN = METHODS / "citation-case-manifest.json"
FIXTURES = ROOT / "data/domains"
COLLECTIONS = {
    "property": "properties",
    "process": "processes",
    "perspective": "perspectives",
    "relationship": "relationships",
}


def _record(document, kind, identity):
    if kind == "framework":
        return document["framework"] if document["framework"]["id"] == identity else None
    return next((row for row in document[COLLECTIONS[kind]] if row["id"] == identity), None)


def _resolve(document, pointer):
    for component in pointer.split("/")[1:]:
        document = document[int(component)] if isinstance(document, list) else document[component]
    return document


def test_citation_cases_reproduce_sources_and_exact_spans(tmp_path):
    output = tmp_path / "cases"
    build_cases(FIXTURES, SPECIFICATION, output)
    artifact = (output / "case-manifest.json").read_bytes()
    assert artifact == FROZEN.read_bytes()
    cases = json.loads(artifact)["cases"]
    assert Counter(case["domain"] for case in cases) == {
        "ScienceResearch": 8,
        "MathEducation": 8,
    }
    assert Counter(case["expected"]["classification"] for case in cases) == {
        "identical_bytes": 1,
        "encoding_only": 1,
        "declared_change": 14,
    }
    prior = json.loads((METHODS / "held-out-case-manifest.json").read_bytes())["cases"]
    assert {item["id"] for case in cases for item in case["expected"]["events"]}.isdisjoint(
        {item["id"] for case in prior for item in case["expected"]["events"]}
    )
    assert {row[f"{role}_sha256"] for row in cases for role in ("before", "after")}.isdisjoint(
        {row[f"{role}_sha256"] for row in prior for role in ("before", "after")}
    )

    present = absent = repeated_source = 0
    for case in cases:
        assert case["questions"] == [
            {field: answer[field] for field in ("kind", "id")} for answer in case["citations"]
        ]
        for role in ("before", "after"):
            source = (output / case["case_id"] / f"{role}.json").read_bytes()
            decoded = source.decode("utf-8")
            document = json.loads(decoded)
            assert sha256(source).hexdigest() == case[f"{role}_sha256"]
            for row in case["citations"]:
                record = _record(document, row["kind"], row["id"])
                span = row[role]
                if record is None:
                    assert span is None
                    absent += 1
                    continue
                present += 1
                assert span["source_sha256"] == case[f"{role}_sha256"]
                quoted = source[span["start_byte"] : span["end_byte"]]
                assert quoted.decode("utf-8") == decoded[span["start_char"] : span["end_char"]]
                assert sha256(quoted).hexdigest() == span["quote_sha256"]
                assert json.loads(quoted) == _resolve(document, span["pointer"]) == record
                case_is_decoy = case["intervention"] == "byte_identical_nested_decoy"
                if case_is_decoy and row["kind"] == "property":
                    repeated_source += 1
                    assert source.count(quoted) == 2
                    assert span["start_byte"] == source.rindex(quoted)
    assert (present, absent, repeated_source) == (62, 10, 4)


def test_citation_case_refuses_unknown_target_on_both_sides(tmp_path):
    spec = json.loads(SPECIFICATION.read_bytes())
    spec["cases"][0]["questions"][0]["id"] = "identity-absent-from-both-snapshots"
    candidate = tmp_path / "spec.json"
    candidate.write_text(json.dumps(spec), encoding="utf-8")
    output = tmp_path / "cases"
    with pytest.raises(ValueError, match="absent from both snapshots"):
        build_cases(FIXTURES, candidate, output)
    assert not output.exists()
