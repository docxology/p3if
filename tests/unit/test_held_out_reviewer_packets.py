"""Verify fixed assignment balance, exact packet inputs and strict raw field diff."""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import json

import pytest

from p3if.held_out_cases import build_cases
from p3if.held_out_reviewer_packets import (
    CASE_IDS,
    PACKET_SCHEMA,
    SESSIONS,
    assignment_rows,
    prepare_packets,
    stable_id_diff,
)

_ROOT = Path(__file__).resolve().parents[2]
_DOCS = _ROOT / "docs/manuscript"
_MANIFEST = _DOCS / "held-out-case-manifest.json"


def _case_directory(tmp_path: Path) -> Path:
    destination = tmp_path / "cases"
    build_cases(_ROOT / "data/domains", _DOCS / "held-out-case-spec.json", destination)
    return destination


def test_frozen_delivery_layout_and_common_bytes(tmp_path: Path) -> None:
    cases = _case_directory(tmp_path)
    destination = tmp_path / "packets"
    prepare_packets(cases, _MANIFEST, destination)
    case_rows = {item["case_id"]: item for item in json.loads(_MANIFEST.read_bytes())["cases"]}
    manifest = json.loads((destination / "packet-manifest.json").read_bytes())
    assert manifest["schema_version"] == PACKET_SCHEMA
    assert manifest["case_manifest_sha256"] == sha256(_MANIFEST.read_bytes()).hexdigest()
    assert manifest["assignments"] == assignment_rows()
    assert Counter((row["case_id"], row["condition"]) for row in manifest["assignments"]) == {
        (case_id, condition): 1 for case_id in CASE_IDS for condition in ("diff", "p3if")
    }
    assert len(manifest["files"]) == 136
    for name, digest in manifest["files"].items():
        assert sha256((destination / name).read_bytes()).hexdigest() == digest

    common = {}
    orders = []
    for session in SESSIONS:
        session_root = destination / session
        assert {item.name for item in session_root.iterdir()} == {
            "1",
            "2",
            "instructions.md",
            "schedule.json",
        }
        schedule = json.loads((session_root / "schedule.json").read_bytes())
        assert len({entry["case_id"] for entry in schedule}) == len(schedule) == 8
        assert all(set(entry) == {"period", "case_id", "folder"} for entry in schedule)
        rows = [row for row in manifest["assignments"] if row["session"] == session]
        assert [entry["case_id"] for entry in schedule] == [row["case_id"] for row in rows]
        conditions = []
        for period in (1, 2):
            group = [row for row in rows if row["period"] == period]
            assert Counter(case_rows[row["case_id"]]["domain"] for row in group) == {
                "ScienceResearch": 2,
                "MathEducation": 2,
            }
            assert len({row["condition"] for row in group}) == 1
            conditions.append(group[0]["condition"])
        orders.append(tuple(conditions))
        for entry in schedule:
            case_id = entry["case_id"]
            folder = session_root / entry["folder"]
            assert {item.name for item in folder.iterdir()} == {
                "before.json",
                "after.json",
                "lookup.json",
                "report.json",
            }
            blobs = tuple(
                (folder / name).read_bytes()
                for name in ("before.json", "after.json", "lookup.json")
            )
            assert common.setdefault(case_id, blobs) == blobs
            for side, raw in zip(("before", "after"), blobs):
                assert raw == (cases / case_id / f"{side}.json").read_bytes()
            report = json.loads((folder / "report.json").read_bytes())
            assert set(report) == {"source_sha256", "summary", "changes"}
            assert "method" not in report["summary"]
            assert report["source_sha256"] == {
                side: case_rows[case_id][f"{side}_sha256"] for side in ("before", "after")
            }
    assert Counter(orders) == {("diff", "p3if"): 2, ("p3if", "diff"): 2}


def test_stable_id_diff_preserves_typed_fields_and_all_kinds() -> None:
    before = {
        "framework": {"id": "f", "name": "Old"},
        "properties": [{"id": "p", "name": "P"}],
        "processes": [{"id": "m", "name": "M"}],
        "perspectives": [{"id": "v", "name": "V"}],
        "relationships": [{"id": "r", "metadata": {"value": True, "steps": [1, 2]}}],
    }
    after = {
        **before,
        "framework": {"id": "f", "name": "New"},
        "properties": [],
        "processes": [{"id": "m", "name": "M", "details": None}],
        "perspectives": [*before["perspectives"], {"id": "w", "name": "W"}],
        "relationships": [{"id": "r", "metadata": {"value": 1, "steps": [2, 1]}}],
    }
    report = stable_id_diff(json.dumps(before).encode(), json.dumps(after).encode())
    events = {row["kind"]: row for row in report["changes"]["events"]}
    assert report["summary"]["classification"] == "declared_change"
    assert set(events) == {"framework", "property", "process", "perspective", "relationship"}
    assert events["property"]["before"] == before["properties"][0]
    assert events["perspective"]["after"] == after["perspectives"][-1]
    assert events["process"]["fields"]["details"] == {"before": {}, "after": {"value": None}}
    assert events["relationship"]["fields"]["metadata"]["before"]["value"]["value"] is True
    assert events["relationship"]["fields"]["metadata"]["after"]["value"]["steps"] == [2, 1]
    assert stable_id_diff(json.dumps(before).encode(), json.dumps(before, indent=1).encode())[
        "summary"
    ] == {"classification": "encoding_only"}


def test_source_tamper_fails_before_any_packet_is_written(tmp_path: Path) -> None:
    cases = _case_directory(tmp_path)
    after = cases / "H16" / "after.json"
    after.write_bytes(after.read_bytes() + b" ")
    destination = tmp_path / "packets"
    with pytest.raises(ValueError, match="Exact source digest mismatch for H16"):
        prepare_packets(cases, _MANIFEST, destination)
    assert not destination.exists()
