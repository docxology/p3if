"""Exercise the analysis commands and their compatibility with existing inspection."""

import json
from pathlib import Path

from p3if.cli import main

EXAMPLE = Path(__file__).resolve().parents[2] / "examples/interchange/framework-v1.json"


def test_cli_analyze_and_legacy_inspect(tmp_path: Path) -> None:
    analysis = tmp_path / "analysis.json"
    inspection = tmp_path / "inspection.json"
    assert main(["analyze", str(EXAMPLE), "-o", str(analysis)]) == 0
    assert main(["inspect", str(EXAMPLE), "-o", str(inspection)]) == 0
    report = json.loads(analysis.read_bytes())
    original = json.loads(inspection.read_bytes())
    assert report["semantic_sha256"] == original["sha256"]
    assert original["axes"] == {"properties": 2, "processes": 1, "perspectives": 1}
    assert original["unlinked_axes"] == {"properties": 0, "processes": 0, "perspectives": 0}
    assert original["relationships"] == {
        "pairs": 1,
        "triples": 1,
        "explicit_strength": 1,
        "explicit_confidence": 0,
    }
    assert original["coordinate_space"] == {"linked_triples": 1, "possible_triples": 2}
    assert report["strength"]["omitted"] == report["strength"]["zero"] == 1


def test_cli_compare_reports_same_id_rewire_and_refuses_different_framework(tmp_path: Path) -> None:
    document = json.loads(EXAMPLE.read_bytes())
    process = {**document["processes"][0], "id": "process.recheck-intake", "name": "Recheck intake"}
    document["processes"].append(process)
    link = document["relationships"][0]
    link["process_id"] = process["id"]
    del link["strength"]
    after = tmp_path / "after.json"
    after.write_text(json.dumps(document), encoding="utf-8")
    output = tmp_path / "comparison.json"
    args = ["compare", str(EXAMPLE), str(after), "-o", str(output)]
    assert main(args) == 0
    report = json.loads(output.read_bytes())
    groups = {group["kind"]: group for group in report["groups"]}
    assert groups["process"]["added"] == [process["id"]]
    assert groups["relationship"]["modified"] == [
        {"id": link["id"], "fields": ["process_id", "strength"], "rewired": True}
    ]

    document["framework"]["id"] = "different-framework"
    after.write_text(json.dumps(document), encoding="utf-8")
    refused = tmp_path / "refused.json"
    assert main([*args[:-1], str(refused)]) == 2
    assert not refused.exists()
    assert main(["compare", "-", "-"]) == 2
