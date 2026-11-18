"""Check matched delivery, exact source selection, and reviewer effort logging."""

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys

import pytest

from p3if import citation_review_tool
from p3if.citation_cases import build_cases
from p3if.citation_effort_packets import CASE_IDS, PACKET_SCHEMA, SESSIONS, prepare_packets

_ROOT = Path(__file__).resolve().parents[2]
_DOCS = _ROOT / "docs/manuscript"
_MANIFEST = _DOCS / "citation-case-manifest.json"


@pytest.fixture(scope="module")
def cases(tmp_path_factory: pytest.TempPathFactory) -> Path:
    target = tmp_path_factory.mktemp("study") / "cases"
    build_cases(_ROOT / "data/domains", _DOCS / "citation-case-spec.json", target)
    return target


def test_matched_packet_materials_and_pointer_intervention(cases: Path, tmp_path: Path) -> None:
    packets = tmp_path / "packets"
    prepare_packets(cases, _MANIFEST, packets)
    truth = {row["case_id"]: row for row in json.loads(_MANIFEST.read_bytes())["cases"]}
    inventory = (packets / "packet-manifest.json").read_bytes()
    assert inventory == (_DOCS / "citation-effort" / "packet-manifest.json").read_bytes()
    manifest = json.loads(inventory)
    rows = manifest["assignments"]
    assert manifest["schema_version"] == PACKET_SCHEMA
    assert manifest["case_manifest_sha256"] == sha256(_MANIFEST.read_bytes()).hexdigest()
    assert Counter((row["case_id"], row["condition"]) for row in rows) == {
        (case_id, arm): 1 for case_id in CASE_IDS for arm in ("p3if", "diff")
    }
    files = manifest["files"]
    assert len(files) == 172
    assert set(files) == {
        path.relative_to(packets).as_posix()
        for path in packets.rglob("*")
        if path.is_file() and path.name != "packet-manifest.json"
    }
    for name, digest in files.items():
        assert sha256((packets / name).read_bytes()).hexdigest() == digest

    shared = {}
    positions = defaultdict(list)
    first_arms = Counter()
    instruction_hashes, tool_hashes = set(), set()
    for session in SESSIONS:
        assignment = [row for row in rows if row["session"] == session]
        assert len(assignment) == len({row["case_id"] for row in assignment}) == 8
        schedule = json.loads((packets / session / "schedule.json").read_bytes())
        assert all(set(item) == {"case_id", "period", "folder"} for item in schedule)
        assert [item["case_id"] for item in schedule] == [row["case_id"] for row in assignment]
        assert {path.name for path in (packets / session).iterdir()} == {
            "1",
            "2",
            "instructions.md",
            "review.py",
            "schedule.json",
        }
        instruction_hashes.add(files[f"{session}/instructions.md"])
        tool_hashes.add(files[f"{session}/review.py"])
        first_arms[assignment[0]["condition"]] += 1
        for period in (1, 2):
            group = [row for row in assignment if row["period"] == period]
            assert Counter(truth[row["case_id"]]["domain"] for row in group) == {
                "ScienceResearch": 2,
                "MathEducation": 2,
            }
            assert len({row["condition"] for row in group}) == 1
            for index, row in enumerate(group):
                positions[row["case_id"]].append((period, index))

        for row in assignment:
            case = truth[row["case_id"]]
            folder = packets / row["folder"]
            assert {path.name for path in folder.iterdir()} == {
                "before.json",
                "after.json",
                "lookup.json",
                "questions.json",
                "report.json",
            }
            common = tuple(
                (folder / f"{name}.json").read_bytes()
                for name in ("before", "after", "lookup", "questions")
            )
            assert common == shared.setdefault(case["case_id"], common)
            assert json.loads(common[3]) == case["questions"]
            report = json.loads((folder / "report.json").read_bytes())
            assert "method" not in report["summary"]
            assert ("source_pointers" in report["changes"]) == (row["condition"] == "p3if")
            for link in report["changes"].get("source_pointers", []):
                assert set(link) == {"kind", "id", "before", "after"}
                for side, raw in zip(("before", "after"), common):
                    snapshot = json.loads(raw)
                    pointer = link[side]
                    if pointer is None:
                        name = citation_review_tool.KINDS[link["kind"]]
                        group = snapshot[name]
                        assert all(record["id"] != link["id"] for record in group)
                    else:
                        value = snapshot
                        for segment in pointer.strip("/").split("/"):
                            value = (
                                value[int(segment)] if isinstance(value, list) else value[segment]
                            )
                        assert value["id"] == link["id"]

    assert first_arms == {"p3if": 2, "diff": 2}
    assert all(len(pair) == 2 and pair[0] == pair[1] for pair in positions.values())
    assert len(tool_hashes) == len(instruction_hashes) == 1


def test_standalone_review_actions_log_outcomes_and_preserve_submission(tmp_path: Path) -> None:
    session = tmp_path / "S1"
    case = session / "1/C01"
    output = tmp_path / "responses"
    case.mkdir(parents=True)
    output.mkdir()
    helper = session / "review.py"
    helper.write_bytes(Path(citation_review_tool.__file__).read_bytes())
    (session / "schedule.json").write_text('[{"case_id":"C01", "period":1, "folder":"1/C01"}]')
    declaration = '{"id":"focus","name":"Repeated","description":"\\u03b2 and 🧪"}'
    prefix = '{"metadata":{"decoy":"β focus"},"properties":[{"id":"other","name":"Repeated"},\r\n'
    source = f"{prefix}{declaration}]}}".encode()
    (case / "before.json").write_bytes(source)
    (case / "report.json").write_bytes(b"{}\n")

    def invoke(*args: str, raw: bytes = b"") -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-I", "-B", str(helper), "--output", str(output), *args],
            input=raw,
            capture_output=True,
            check=False,
        )

    assert invoke("start", "C01").returncode == 0
    assert invoke("open", "C01", "report").stdout == b"{}\n"
    found = invoke("find", "C01", "before", "property", "--contains", "focus")
    assert json.loads(found.stdout) == [
        {"id": "focus", "name": "Repeated", "pointer": "/properties/1"}
    ]
    assert invoke("search", "C01", "before", "unmatched private literal").stdout == b"[]\n"
    assert invoke("cite", "C01", "before", "/metadata/decoy").returncode == 2
    cited = invoke("cite", "C01", "before", "/properties/1")
    exact = json.loads(cited.stdout)
    assert exact == {
        "source_sha256": sha256(source).hexdigest(),
        "pointer": "/properties/1",
        "start_char": len(prefix),
        "end_char": len(prefix + declaration),
        "start_byte": len(prefix.encode()),
        "end_byte": len((prefix + declaration).encode()),
        "quote_sha256": sha256(declaration.encode()).hexdigest(),
    }
    submission = b'  {"case_id": "C01", "citations": []}\r\n'
    assert invoke("submit", "C01", raw=submission).returncode == 0
    assert invoke("submit", "C01", raw=submission).returncode == 2
    assert (output / "C01.json").read_bytes() == submission
    log = (output / "actions.jsonl").read_text()
    assert "unmatched private literal" not in log
    rows = [json.loads(line) for line in log.splitlines()]
    assert [(row["action"], row["status"]) for row in rows] == [
        ("start", "ok"),
        ("open", "ok"),
        ("find", "ok"),
        ("search", "no_hits"),
        ("cite", "error"),
        ("cite", "ok"),
        ("submit", "ok"),
        ("submit", "error"),
    ]
    assert rows[-2]["answer_sha256"] == sha256(submission).hexdigest()
    assert all(row["started_monotonic_ns"] <= row["finished_monotonic_ns"] for row in rows)
