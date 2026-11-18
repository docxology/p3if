"""Verify the sole packet intervention and the masked reader's exact citations."""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys

import pytest

from p3if.citation_cases import build_cases
from p3if.citation_review_tool import ACTION_SCHEMA, KINDS
from p3if.navigation_ablation_packets import CASE_IDS, PACKET_SCHEMA, SESSIONS, prepare_packets

_ROOT = Path(__file__).resolve().parents[2]
_DOCS = _ROOT / "docs/manuscript"
_MANIFEST = _DOCS / "navigation-case-manifest.json"
_COMMON = ("before.json", "after.json", "questions.json", "lookup.json")
_TOOLS = ("instructions.md", "review.py")
_ARMS = ("navigation", "no_navigation")


@pytest.fixture(scope="module")
def packets(tmp_path_factory: pytest.TempPathFactory) -> Path:
    workspace = tmp_path_factory.mktemp("navigation")
    cases = workspace / "cases"
    build_cases(_ROOT / "data/domains", _DOCS / "navigation-case-spec.json", cases)
    packets = workspace / "packets"
    prepare_packets(cases, _MANIFEST, packets)
    return packets


def test_packet_inventory_and_counterbalancing(packets: Path) -> None:
    inventory = (packets / "packet-manifest.json").read_bytes()
    assert inventory == (_DOCS / "navigation-ablation" / "packet-manifest.json").read_bytes()
    manifest = json.loads(inventory)
    assert manifest["schema_version"] == PACKET_SCHEMA
    assert manifest["case_manifest_sha256"] == sha256(_MANIFEST.read_bytes()).hexdigest()
    files = manifest["files"]
    assert files == {
        path.relative_to(packets).as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in packets.rglob("*")
        if path.is_file() and path.name != "packet-manifest.json"
    }
    assert len(files) == 172
    assert Counter((r["case_id"], r["condition"]) for r in manifest["assignments"]) == {
        (case_id, arm): 1 for case_id in CASE_IDS for arm in _ARMS
    }

    positions = Counter()
    first_arms = Counter()
    for session in SESSIONS:
        rows = [row for row in manifest["assignments"] if row["session"] == session]
        assert len(rows) == len({row["case_id"] for row in rows}) == 8
        assert {path.name for path in (packets / session).iterdir()} == {
            "1",
            "2",
            "schedule.json",
            *_TOOLS,
        }
        schedule = json.loads((packets / session / "schedule.json").read_bytes())
        assert schedule == [
            {
                "period": row["period"],
                "case_id": row["case_id"],
                "folder": f"{row['period']}/{row['case_id']}",
            }
            for row in rows
        ]
        for row, item in zip(rows, schedule):
            assert row["folder"] == f"{session}/{item['folder']}"
        first_arms[rows[0]["condition"]] += 1
        for period in (1, 2):
            group = [row for row in rows if row["period"] == period]
            assert len(group) == 4
            assert len({row["condition"] for row in group}) == 1
            assert sum(row["case_id"] in CASE_IDS[:8] for row in group) == 2
            for index, row in enumerate(group):
                positions[row["case_id"], period, index] += 1

    assert first_arms == {arm: 2 for arm in _ARMS}
    assert len(positions) == 16 and set(positions.values()) == {2}
    for name in _TOOLS:
        assert len({files[f"{session}/{name}"] for session in SESSIONS}) == 1


def test_only_valid_source_pointers_vary_in_matched_packets(packets: Path) -> None:
    assignments = json.loads((packets / "packet-manifest.json").read_bytes())["assignments"]
    for case_id in CASE_IDS:
        paths = {
            row["condition"]: packets / row["folder"]
            for row in assignments
            if row["case_id"] == case_id
        }
        with_nav, without_nav = (paths[arm] for arm in _ARMS)
        for path in paths.values():
            assert {child.name for child in path.iterdir()} == {*_COMMON, "report.json"}
        for filename in _COMMON:
            assert (with_nav / filename).read_bytes() == (without_nav / filename).read_bytes()
        treatment, control = (
            json.loads((path / "report.json").read_bytes()) for path in (with_nav, without_nav)
        )
        links = treatment["changes"].pop("source_pointers")
        assert control["changes"].pop("source_pointers") == []
        assert json.dumps(treatment, sort_keys=True) == json.dumps(control, sort_keys=True)
        events = treatment["changes"]["events"]
        assert [(link["kind"], link["id"]) for link in links] == [
            (event["kind"], event["id"]) for event in events
        ]
        for side in ("before", "after"):
            source = (with_nav / f"{side}.json").read_bytes()
            assert treatment["source_sha256"][side] == sha256(source).hexdigest()
            snapshot = json.loads(source)
            for link in links:
                assert set(link) == {"kind", "id", "before", "after"}
                records = snapshot[KINDS[link["kind"]]]
                pointer = link[side]
                if isinstance(records, dict):
                    assert pointer == ("/framework" if records["id"] == link["id"] else None)
                elif pointer is None:
                    assert all(record["id"] != link["id"] for record in records)
                else:
                    assert pointer.startswith(f"/{KINDS[link['kind']]}/")
                    assert records[int(pointer.split("/")[-1])]["id"] == link["id"]


def test_standalone_ablation_reader_uses_a_ids_and_prior_receipt_schema(
    packets: Path, tmp_path: Path
) -> None:
    session = packets / "S1"
    output = tmp_path / "answers"
    output.mkdir()
    reader = session / "review.py"
    historical = (_ROOT / "src/p3if/citation_review_tool.py").read_bytes()
    assert reader.read_bytes() == historical.replace(
        rb're.compile(r"C[0-9]{2}\Z")', rb're.compile(r"A[0-9]{2}\Z")'
    )
    run = [sys.executable, "-I", "-B", str(reader), "--output", str(output)]
    subprocess.run([*run, "start", "A01"], check=True, capture_output=True)
    cited = subprocess.check_output([*run, "cite", "A01", "before", "/framework"])
    citation = json.loads(cited)
    source = (session / "1/A01/before.json").read_bytes()
    quote = source[citation["start_byte"] : citation["end_byte"]]
    assert json.loads(quote) == json.loads(source)["framework"]
    assert citation["source_sha256"] == sha256(source).hexdigest()
    assert citation["quote_sha256"] == sha256(quote).hexdigest()
    answer = b'{"case_id": "A01", "citations": []}\n'
    receipt = json.loads(subprocess.check_output([*run, "submit", "A01"], input=answer))
    assert receipt == {"case_id": "A01", "answer_sha256": sha256(answer).hexdigest()}
    assert (output / "A01.json").read_bytes() == answer
    actions = [json.loads(line) for line in (output / "actions.jsonl").read_bytes().splitlines()]
    assert [entry["action"] for entry in actions] == ["start", "cite", "submit"]
    assert all(entry["schema_version"] == ACTION_SCHEMA for entry in actions)
    assert all(entry["case_id"] == "A01" for entry in actions)
