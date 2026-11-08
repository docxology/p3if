"""Exercise the public interchange producer with real native framework objects."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from p3if.cli import inspect_interchange, main
from p3if.core.framework import P3IFFramework
from p3if.core.models import Perspective, Process, Property, Relationship
from p3if.data.exporters import export_to_json
from p3if.data.importers import import_from_json
from p3if.interchange import FrameworkIdentity, InterchangeError, canonical_bytes
from p3if.interchange_native import (
    framework_from_interchange,
    interchange_from_framework,
    migrate_legacy,
)


def _framework() -> P3IFFramework:
    framework = P3IFFramework()
    framework.add_pattern(
        Property(
            id="availability",
            name="Availability",
            domain="support",
            description="Service can be reached.",
            unit="percent",
            range_min=0.0,
            range_max=100.0,
            metadata={"source": {"clause": "A.4"}},
        )
    )
    framework.add_pattern(
        Process(
            id="restore",
            name="Restore",
            domain="support",
            description="Restore service from a snapshot.",
            steps=[{"label": "Validate 📄", "required": True}],
            prerequisites=["external-backup"],
        )
    )
    framework.add_pattern(
        Perspective(
            id="operator",
            name="Operator",
            domain="support",
            description="On-call perspective.",
            viewpoint="Operations",
            concerns=["recovery time"],
        )
    )
    framework.add_relationship(
        Relationship(
            id="availability-restore",
            property_id="availability",
            process_id="restore",
            strength=0.0,
        )
    )
    framework.add_relationship(
        Relationship(
            id="operator-restore",
            property_id="availability",
            process_id="restore",
            perspective_id="operator",
            evidence_sources=["A.4"],
        )
    )
    return framework


def test_native_interchange_retains_explicit_fields_and_missing_scores() -> None:
    identity = FrameworkIdentity(id="service", name="Service recovery", metadata={"edition": 2})
    framework = _framework()
    process = framework.get_pattern("restore")
    assert isinstance(process, Process)
    process.update_metadata("owner", "operations")
    process.add_tag(" Recovery ")
    snapshot = interchange_from_framework(framework, identity)
    data = json.loads(canonical_bytes(snapshot))
    assert data["properties"][0]["metadata"]["source"]["clause"] == "A.4"
    assert data["processes"][0]["steps"] == [{"label": "Validate 📄", "required": True}]
    assert data["processes"][0]["metadata"] == {"owner": "operations"}
    assert data["processes"][0]["tags"] == ["recovery"]
    assert data["perspectives"][0]["viewpoint"] == "Operations"
    assert data["relationships"][0]["strength"] == 0.0
    assert "confidence" not in data["relationships"][0]
    assert "strength" not in data["relationships"][1]
    restored = framework_from_interchange(snapshot)
    assert canonical_bytes(interchange_from_framework(restored, identity)) == canonical_bytes(
        snapshot
    )
    assert inspect_interchange(snapshot)["relationships"] == {
        "pairs": 1,
        "triples": 1,
        "explicit_strength": 1,
        "explicit_confidence": 0,
    }


def test_legacy_grouped_export_keeps_native_viewpoint_and_migrates(tmp_path: Path) -> None:
    exported = export_to_json(_framework(), tmp_path / "legacy.json")
    restored = import_from_json(exported)
    perspective = restored.get_pattern("operator")
    assert isinstance(perspective, Perspective) and perspective.viewpoint == "Operations"
    identity = FrameworkIdentity(id="service", name="Service recovery")
    migrated = migrate_legacy(exported.read_bytes(), identity)
    assert migrated.perspectives[0].viewpoint == "Operations"
    assert len(migrated.relationships) == 2
    framework_from_interchange(migrated)


def test_migration_preserves_missing_viewpoint_and_rejects_key_mismatch() -> None:
    identity = FrameworkIdentity(id="legacy", name="Legacy example")
    perspective = {"id": "p", "name": "Reader", "description": "Reader view", "domain": "docs"}
    grouped = {
        "properties": [],
        "processes": [],
        "perspectives": [perspective],
        "relationships": [],
    }
    migrated = migrate_legacy(json.dumps(grouped).encode(), identity)
    assert "viewpoint" not in json.loads(canonical_bytes(migrated))["perspectives"][0]
    with pytest.raises(InterchangeError, match="viewpoint"):
        framework_from_interchange(migrated)

    keyed = {
        "patterns": {"wrong": {**perspective, "type": "perspective"}},
        "relationships": {},
    }
    with pytest.raises(InterchangeError, match="keys must match"):
        migrate_legacy(json.dumps(keyed).encode(), identity)


def test_migrate_domain_preserves_exact_ids_metadata_and_missing_descriptions() -> None:
    project = Path(__file__).resolve().parents[2]
    data = (project / "data/domains/scienceresearch.json").read_bytes()
    declared = json.loads(data)
    identity = FrameworkIdentity(id="science-research", name="Science research")
    migrated = json.loads(canonical_bytes(migrate_legacy(data, identity)))
    for axis in ("properties", "processes", "perspectives"):
        assert migrated[axis] == sorted(declared["patterns"][axis], key=lambda row: row["id"])
    assert migrated["relationships"] == sorted(declared["relationships"], key=lambda row: row["id"])
    assert migrated["framework"]["metadata"]["legacy_export"] == {
        key: declared[key] for key in ("domain", "version", "metadata")
    }
    declared["properties"].reverse()
    with pytest.raises(InterchangeError, match="properties names must match"):
        migrate_legacy(json.dumps(declared).encode(), identity)


def test_domain_template_is_valid_and_materializable() -> None:
    project = Path(__file__).resolve().parents[2]
    template = (project / "data/domains/template_domain.json").read_bytes()
    identity = FrameworkIdentity(id="template", name="Domain template")
    migrated = migrate_legacy(template, identity)
    framework = framework_from_interchange(migrated)
    assert len(framework.get_all_patterns()) == 3
    assert len(framework.get_all_relationships()) == 1


def test_cli_refuses_to_replace_a_canonical_output(tmp_path: Path) -> None:
    identity = FrameworkIdentity(id="service", name="Service recovery")
    data = canonical_bytes(interchange_from_framework(_framework(), identity))
    source = tmp_path / "wire.json"
    source.write_bytes(data)
    target = tmp_path / "result.json"
    args = ["roundtrip", str(source), "--output", str(target)]
    assert main(args) == 0
    assert target.read_bytes() == data
    target.write_bytes(b"original")
    assert main(args) == 2
    assert target.read_bytes() == b"original"
    assert list(tmp_path.glob(".p3if-*")) == []


def test_roundtrip_stdout_is_canonical_json(tmp_path: Path) -> None:
    identity = FrameworkIdentity(id="service", name="Service recovery")
    data = canonical_bytes(interchange_from_framework(_framework(), identity))
    source = tmp_path / "wire.json"
    source.write_bytes(data)
    project = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-B", "-m", "p3if", "roundtrip", str(source)],
        env={**os.environ, "PYTHONPATH": str(project / "src")},
        stdin=subprocess.DEVNULL,
        capture_output=True,
        check=True,
        timeout=15,
    )
    assert result.stdout == data
