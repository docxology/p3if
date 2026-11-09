"""Exercise stable transition coordinates and the offline CLI contract."""

import json
from pathlib import Path
from typing import Any

from p3if.cli import main
from p3if.interchange import Interchange, load_interchange
from p3if.interchange_transition import TransitionEvent, transition_interchange

_EXAMPLE = Path(__file__).resolve().parents[2] / "examples/interchange/framework-v1.json"


def _load(value: dict[str, Any]) -> Interchange:
    return load_interchange(json.dumps(value, ensure_ascii=False).encode("utf-8"))


def test_transition_reports_sparse_coordinates_on_both_sides() -> None:
    """Keep absent records, omitted endpoints, and exact rewires distinct."""
    before = load_interchange(_EXAMPLE.read_bytes())
    raw = json.loads(_EXAMPLE.read_bytes())
    raw["framework"]["name"] = "Revised archive"
    del raw["properties"][0]
    raw["processes"].append(
        {"id": "process.recheck-intake", "name": "Recheck", "domain": "synthetic-archive"}
    )
    link = raw["relationships"][0]
    del link["strength"]
    link["process_id"] = "process.recheck-intake"
    raw["relationships"][1] = {
        "id": "relationship.added-pair",
        "property_id": "property.source-fidelity",
        "process_id": "process.recheck-intake",
    }
    after = _load(raw)
    report = transition_interchange(before, after)
    assert report.axes.model_dump() == {
        "properties": ("property.retention-window", "property.source-fidelity"),
        "processes": ("process.recheck-intake", "process.verify-intake"),
        "perspectives": ("perspective.archive-operator",),
    }
    assert [(row.kind, row.id, row.change) for row in report.events] == [
        ("framework", "synthetic.archive-example", "modified"),
        ("property", "property.retention-window", "removed"),
        ("process", "process.recheck-intake", "added"),
        ("relationship", "relationship.added-pair", "added"),
        ("relationship", "relationship.fidelity-at-intake", "modified"),
        ("relationship", "relationship.retention-stakeholder", "removed"),
    ]
    framework, removed_property, process, pair, modified, removed_link = report.events
    assert framework.before == framework.after == (None, None, None)
    assert framework.fields == ("name",)
    assert removed_property.before == ("property.retention-window", None, None)
    assert removed_property.after is None
    assert process.before is None and process.after == (None, "process.recheck-intake", None)
    assert pair.before is None
    assert pair.after == ("property.source-fidelity", "process.recheck-intake", None)
    assert modified == TransitionEvent(
        kind="relationship",
        id="relationship.fidelity-at-intake",
        change="modified",
        fields=("process_id", "strength"),
        rewired=True,
        before=(
            "property.source-fidelity",
            "process.verify-intake",
            "perspective.archive-operator",
        ),
        after=(
            "property.source-fidelity",
            "process.recheck-intake",
            "perspective.archive-operator",
        ),
    )
    assert removed_link.before == (
        "property.retention-window",
        None,
        "perspective.archive-operator",
    )
    assert removed_link.after is None

    reverse = transition_interchange(after, before)
    assert reverse.before_sha256 == report.after_sha256
    assert reverse.after_sha256 == report.before_sha256
    assert reverse.axes == report.axes
    assert [(row.before, row.after) for row in reverse.events] == [
        (row.after, row.before) for row in report.events
    ]


def test_transition_orders_ids_without_equating_formatting_to_a_change() -> None:
    """Reordered arrays and different source formatting keep an empty transition."""
    source = _EXAMPLE.read_bytes()
    reordered = json.loads(source)
    reordered["properties"].reverse()
    reordered["relationships"].reverse()
    report = transition_interchange(load_interchange(source), _load(reordered))
    assert report.before_sha256 == report.after_sha256
    assert report.events == ()
    assert report.axes.properties == ("property.retention-window", "property.source-fidelity")


def test_transition_cli_writes_json_and_refuses_unrelated_snapshots(tmp_path: Path) -> None:
    """Serialize exact coordinates and keep invalid comparisons from writing output."""
    source = json.loads(_EXAMPLE.read_bytes())
    source["relationships"][0]["strength"] = None
    after = tmp_path / "after.json"
    after.write_text(json.dumps(source), encoding="utf-8")
    output = tmp_path / "transition.json"
    assert main(["transition", str(_EXAMPLE), str(after), "-o", str(output)]) == 0
    result = json.loads(output.read_bytes())
    (event,) = result["events"]
    assert event["fields"] == ["strength"]
    assert (
        event["before"]
        == event["after"]
        == [
            "property.source-fidelity",
            "process.verify-intake",
            "perspective.archive-operator",
        ]
    )
    assert event["rewired"] is False
    source["framework"]["id"] = "unrelated"
    after.write_text(json.dumps(source), encoding="utf-8")
    missing = tmp_path / "invalid.json"
    assert main(["transition", str(_EXAMPLE), str(after), "-o", str(missing)]) == 2
    assert not missing.exists()
    assert main(["transition", "-", "-"]) == 2
