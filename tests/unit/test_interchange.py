"""Exercise the public interchange contract with real documents and typed links."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from p3if.interchange import (
    MAX_BYTES,
    MAX_DEPTH,
    MAX_JSON_VALUES,
    InterchangeError,
    canonical_bytes,
    decode_json,
    interchange_schema,
    interchange_sha256,
    load_interchange,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "examples" / "interchange" / "framework-v1.json"


def _sample() -> dict[str, Any]:
    return json.loads(FIXTURE.read_bytes())


def _encode(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def test_canonical_round_trip_preserves_axes_omission_and_explicit_zero() -> None:
    """Keep stable IDs, optional values, partial links, and nested process data."""
    document = load_interchange(FIXTURE.read_bytes())
    assert (len(document.properties), len(document.processes), len(document.perspectives)) == (
        2,
        1,
        1,
    )
    triad, pair = document.relationships
    assert triad.strength == 0.0 and "strength" in triad.model_fields_set
    assert pair.strength is None and "strength" not in pair.model_fields_set
    assert pair.process_id is None
    assert document.processes[0].steps == (
        {"name": "Compare digest", "retry": False, "labels": ["α", "🗂"]},
    )
    normalized = canonical_bytes(document)
    assert canonical_bytes(load_interchange(normalized)) == normalized
    assert interchange_sha256(document) == (
        "b3fd06e9462902e58b78ce79a28b7e3fc626bdebc324d3135ba47c206452c263"
    )
    payload = _sample()
    payload["properties"].reverse()
    payload["relationships"].reverse()
    assert canonical_bytes(load_interchange(_encode(payload))) == normalized


def test_explicit_null_keeps_distinct_wire_identity() -> None:
    """Keep an explicit absent measurement separate from an omitted declaration."""
    payload = _sample()
    payload["relationships"][0]["confidence"] = None
    explicit = load_interchange(_encode(payload))
    original = load_interchange(FIXTURE.read_bytes())
    assert explicit.relationships[0].confidence is None
    assert "confidence" in explicit.relationships[0].model_fields_set
    assert interchange_sha256(explicit) != interchange_sha256(original)


@pytest.mark.parametrize("axis", ["properties", "processes", "perspectives"])
def test_optional_description_preserves_omission(axis: str) -> None:
    """Keep historical axis records that did not declare a description."""
    payload = _sample()
    del payload[axis][0]["description"]
    omitted = load_interchange(_encode(payload))
    assert "description" not in json.loads(canonical_bytes(omitted))[axis][0]

    payload[axis][0]["description"] = None
    explicit_null = load_interchange(_encode(payload))
    assert json.loads(canonical_bytes(explicit_null))[axis][0]["description"] is None
    assert interchange_sha256(explicit_null) != interchange_sha256(omitted)


@pytest.mark.parametrize("version", [True, 1.0, "1", 2])
def test_requires_exact_integer_version(version: object) -> None:
    """Refuse alternate version representations and unsupported versions."""
    payload = _sample()
    payload["version"] = version
    with pytest.raises(InterchangeError, match="version"):
        load_interchange(_encode(payload))


def test_duplicate_pattern_identity_across_axes_is_refused() -> None:
    """Give every relationship endpoint an unambiguous stable pattern ID."""
    payload = _sample()
    payload["processes"][0]["id"] = payload["properties"][0]["id"]
    with pytest.raises(InterchangeError, match="duplicate pattern identity"):
        load_interchange(_encode(payload))


def test_duplicate_relationship_identity_is_refused() -> None:
    """Keep two distinct relationships from sharing the same identity."""
    payload = _sample()
    payload["relationships"][1]["id"] = payload["relationships"][0]["id"]
    with pytest.raises(InterchangeError, match="duplicate relationship identity"):
        load_interchange(_encode(payload))


@pytest.mark.parametrize("target", ["missing", "property.retention-window"])
def test_dangling_or_wrong_axis_endpoint_is_refused(target: str) -> None:
    """Resolve each present endpoint in its own declared dimension."""
    payload = _sample()
    payload["relationships"][0]["process_id"] = target
    with pytest.raises(InterchangeError, match="process_id"):
        load_interchange(_encode(payload))


def test_requires_two_typed_axes() -> None:
    """Declaring one endpoint and an explicit null fails the graph contract."""
    payload = _sample()
    payload["relationships"][0]["process_id"] = None
    del payload["relationships"][0]["perspective_id"]
    with pytest.raises(InterchangeError, match="at least two dimensions"):
        load_interchange(_encode(payload))


def test_forbids_unknown_fields_on_axis_entities() -> None:
    """Reject unknown wire fields so callers never silently drop data."""
    payload = _sample()
    payload["processes"][0]["arbitrary_new_field"] = "producer data"
    with pytest.raises(InterchangeError, match="arbitrary_new_field"):
        load_interchange(_encode(payload))


@pytest.mark.parametrize(
    ("source", "diagnostic"),
    [
        (b'{"outer":{"x":0,"x":1}}', "duplicate member"),
        (b'{"score":NaN}', "invalid JSON number"),
        (b'{"score":1e99999}', "must be finite"),
        (b'{"bad":"\\ud800"}', "Unicode scalar"),
        (b'{"bad":"\xff"}', "well-formed UTF-8"),
        (b"[]", "object at the document root"),
        (b'{"large":' + b"1" * 129 + b"}", "supported precision"),
        (b'{"x":' + b"[" * MAX_DEPTH + b"0" + b"]" * MAX_DEPTH + b"}", "structure exceeds"),
        (b'{"x":[' + b"0," * MAX_JSON_VALUES + b"0]}", "structure exceeds"),
        (b" " * (MAX_BYTES + 1), "bytes of UTF-8 JSON"),
    ],
)
def test_refuses_malformed_or_unbounded_json(source: bytes, diagnostic: str) -> None:
    """Fail before constructing graph models when input exceeds its wire budget."""
    with pytest.raises(InterchangeError, match=diagnostic):
        decode_json(source)


def test_published_schema_matches_version_and_structural_contract() -> None:
    """Keep machine-readable shape in sync across the supported Pydantic versions."""
    path = ROOT / "schemas" / "p3if-interchange-v1.schema.json"
    published = json.loads(path.read_bytes())
    generated = interchange_schema()
    assert published["$id"] == generated["$id"]
    assert set(published["required"]) == set(generated["required"])
    assert published["properties"]["version"]["const"] == 1
    assert published["additionalProperties"] is False
    assert (
        published["$defs"]["InterchangeRelationship"]["anyOf"]
        == generated["$defs"]["InterchangeRelationship"]["anyOf"]
    )
