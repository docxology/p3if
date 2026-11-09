"""Verify sparse coverage and exact stable-identity comparisons with real data."""

import json
from pathlib import Path
from typing import Any

import pytest

from p3if.interchange import Interchange, InterchangeError, interchange_sha256, load_interchange
from p3if.interchange_analysis import analyze_interchange, compare_interchange

_FIXTURE = Path(__file__).resolve().parents[2] / "examples" / "interchange" / "framework-v1.json"


def _sample() -> dict[str, Any]:
    return json.loads(_FIXTURE.read_bytes())


def _load(payload: dict[str, Any]) -> Interchange:
    return load_interchange(json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def test_coverage_keeps_pair_and_triple_coordinates_and_score_states_separate() -> None:
    """Repeated links preserve relationship counts and only one coordinate."""
    payload = _sample()
    payload["perspectives"].append(
        {"id": "perspective.unlinked", "name": "Independent reviewer", "domain": "test"}
    )
    original = payload["relationships"][0]
    payload["relationships"].append(
        {
            **original,
            "id": "relationship.repeat",
            "strength": None,
            "confidence": 0.75,
        }
    )
    graph = _load(payload)
    report = analyze_interchange(graph)
    assert report.semantic_sha256 == interchange_sha256(graph)
    assert report.framework_id == graph.framework.id
    assert report.relationship_count == 3
    assert [(row.axis, row.total, row.linked, row.unlinked) for row in report.axes] == [
        ("property", 2, 2, 0),
        ("process", 1, 1, 0),
        ("perspective", 2, 1, 1),
    ]
    assert [
        (row.axes, row.relationships, row.observed, row.possible, row.unobserved)
        for row in report.spaces
    ] == [
        (("property", "process"), 0, 0, 2, 2),
        (("property", "perspective"), 1, 1, 4, 3),
        (("process", "perspective"), 0, 0, 2, 2),
        (("property", "process", "perspective"), 2, 1, 4, 3),
    ]
    assert report.strength.model_dump() == {
        "omitted": 1,
        "null": 1,
        "missing": 2,
        "zero": 1,
        "nonzero": 0,
        "reported": 1,
    }
    assert report.confidence.model_dump() == {
        "omitted": 2,
        "null": 0,
        "missing": 2,
        "zero": 0,
        "nonzero": 1,
        "reported": 1,
    }


def test_large_sparse_denominators_do_not_expand_coordinates() -> None:
    """Report one explicit coordinate against a billion possible triples."""
    payload = _sample()
    for group in ("properties", "processes", "perspectives"):
        payload[group] = [
            {"id": f"{group}-{index}", "name": f"{group} {index}", "domain": "test"}
            for index in range(1000)
        ]
    payload["relationships"] = [
        {
            "id": "only-declared-link",
            "property_id": "properties-17",
            "process_id": "processes-18",
            "perspective_id": "perspectives-19",
        }
    ]
    report = analyze_interchange(_load(payload))
    assert [(axis.total, axis.linked, axis.unlinked) for axis in report.axes] == [
        (1000, 1, 999),
        (1000, 1, 999),
        (1000, 1, 999),
    ]
    assert [(space.possible, space.observed) for space in report.spaces] == [
        (1_000_000, 0),
        (1_000_000, 0),
        (1_000_000, 0),
        (1_000_000_000, 1),
    ]


def test_empty_axes_preserve_zero_denominators() -> None:
    """An undeclared dimension contributes no possible coordinates."""
    payload = _sample()
    payload["properties"] = []
    payload["relationships"] = []
    report = analyze_interchange(_load(payload))
    assert [space.possible for space in report.spaces] == [0, 0, 1, 0]
    assert all(space.observed == 0 for space in report.spaces)
    assert all(axis.linked == 0 for axis in report.axes)
    assert report.strength.missing == report.confidence.missing == 0


def test_comparison_reports_identity_changes_rewires_and_exact_metadata_types() -> None:
    """Compare declared wire fields, including typed nested metadata."""
    before = _sample()
    obsolete = {"id": "property.obsolete", "name": "Old", "domain": "test"}
    before["properties"].append(obsolete)
    after = _sample()
    after["framework"]["name"] = "Renamed framework"
    after["framework"]["metadata"]["synthetic"] = 1
    after["properties"][0]["name"] = "New retention label"
    after["properties"].append({"id": "property.new", "name": "New", "domain": "test"})
    after["relationships"][0]["property_id"] = "property.retention-window"
    after["relationships"][0]["confidence"] = 0.0
    after["relationships"][1]["process_id"] = None

    left, right = _load(before), _load(after)
    report = compare_interchange(left, right)
    assert report.framework_id == left.framework.id
    assert (report.before_sha256, report.after_sha256) == (
        interchange_sha256(left),
        interchange_sha256(right),
    )
    assert report.framework_fields == ("metadata", "name")
    properties, processes, perspectives, relationships = report.groups
    assert [group.kind for group in report.groups] == [
        "property",
        "process",
        "perspective",
        "relationship",
    ]
    assert properties.before_total == properties.after_total == 3
    assert properties.added == ("property.new",)
    assert properties.removed == ("property.obsolete",)
    assert [(change.id, change.fields) for change in properties.modified] == [
        ("property.retention-window", ("name",))
    ]
    assert not processes.modified and not perspectives.modified
    assert [(change.id, change.fields, change.rewired) for change in relationships.modified] == [
        ("relationship.fidelity-at-intake", ("confidence", "property_id"), True),
        ("relationship.retention-stakeholder", ("process_id",), False),
    ]


def test_reordered_id_sets_produce_no_deltas() -> None:
    """Canonical graph order and comparison order are independent of input order."""
    first = _sample()
    second = _sample()
    second["properties"].reverse()
    second["relationships"].reverse()
    report = compare_interchange(_load(first), _load(second))
    assert report.before_sha256 == report.after_sha256
    assert not report.framework_fields
    assert all(
        not group.added and not group.removed and not group.modified for group in report.groups
    )


def test_comparison_requires_matching_framework_ids() -> None:
    """A display name cannot make unrelated stable framework IDs comparable."""
    original = _sample()
    foreign = _sample()
    foreign["framework"]["id"] = "different.archive"
    with pytest.raises(InterchangeError, match="matching framework IDs"):
        compare_interchange(_load(original), _load(foreign))
