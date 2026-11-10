"""Verify the preregistered inputs without invoking either review treatment."""

import hashlib
import json
from pathlib import Path

import pytest

from p3if.reviewer_study_cases import build_cases

ROOT = Path(__file__).resolve().parents[2]
METHODS = ROOT / "docs/manuscript"
SPECIFICATION = METHODS / "reviewer-study-case-spec.json"
FROZEN = METHODS / "reviewer-study-case-manifest.json"
FIXTURES = ROOT / "data/domains"


def test_frozen_case_sources_and_exact_citations(tmp_path):
    output = tmp_path / "pilot"
    build_cases(FIXTURES, SPECIFICATION, output)
    manifest_bytes = (output / "case-manifest.json").read_bytes()
    assert manifest_bytes == FROZEN.read_bytes()
    manifest = json.loads(manifest_bytes)
    for case in manifest["cases"]:
        pair = []
        for role in ("before", "after"):
            source = (output / case["case_id"] / f"{role}.json").read_bytes()
            pair.append(source)
            assert hashlib.sha256(source).hexdigest() == case[f"{role}_sha256"]
            citation = case["citations"][role]
            if citation is None:
                continue
            assert citation["source_sha256"] == case[f"{role}_sha256"]
            span = source[citation["start_byte"] : citation["end_byte"]]
            span_text = source.decode("utf-8")[citation["start_char"] : citation["end_char"]]
            assert span.decode("utf-8") == span_text
            assert hashlib.sha256(span).hexdigest() == citation["quote_sha256"]
            collection, index = citation["pointer"].lstrip("/").split("/")
            relationship = json.loads(source)[collection][int(index)]
            assert json.loads(span) == relationship
            assert relationship["id"] == case["expected"]["events"][0]["id"]
        if case["intervention"] == "identical_bytes":
            assert pair[0] == pair[1]
        else:
            assert pair[0] != pair[1]
            assert (json.loads(pair[0]) == json.loads(pair[1])) == (
                case["intervention"] == "encoding_only"
            )


def test_fixture_drift_prevents_case_generation(tmp_path):
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    for name in ("scienceresearch.json", "matheducation.json"):
        data = (FIXTURES / name).read_bytes()
        (fixtures / name).write_bytes(data + b"\n")
    output = tmp_path / "pilot"
    with pytest.raises(ValueError, match="differs from the frozen source"):
        build_cases(fixtures, SPECIFICATION, output)
    assert not output.exists()
