"""Independently verify frozen allocation and matched files."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def main():
    if not __debug__:
        raise RuntimeError("Run this verification with Python assertions enabled")
    root, cases, receipt = map(Path, sys.argv[1:])
    trial = root / "packet-manifest.json"
    key = {row["case_id"]: row for row in load(cases)["cases"]}
    manifest = load(trial)
    assert manifest["schema_version"] == "p3if.navigation-ablation-packets.v1"
    assert manifest["case_manifest_sha256"] == digest(cases)
    tasks = manifest["assignments"]
    assert Counter((row["case_id"], row["condition"]) for row in tasks) == {
        (identity, arm): 1 for identity in key for arm in ("navigation", "no_navigation")
    }
    assert not any(path.is_symlink() for path in root.rglob("*"))
    files = {
        path.relative_to(root).as_posix(): digest(path)
        for path in root.rglob("*")
        if path.is_file() and path != trial
    }
    assert files == manifest["files"]
    assert {path.name for path in root.iterdir()} == {"S1", "S2", "S3", "S4", trial.name}
    common = {}
    positions = defaultdict(list)
    instructions = set()
    readers = set()
    first = Counter()
    report_bytes = defaultdict(list)
    report_bases = {}
    navigation_lists = {}
    for session in ("S1", "S2", "S3", "S4"):
        folder = root / session
        grouped = [row for row in tasks if row["session"] == session]
        schedule = load(folder / "schedule.json")
        assert schedule == [
            {
                "case_id": row["case_id"],
                "period": row["period"],
                "folder": str(Path(row["folder"]).relative_to(session)),
            }
            for row in grouped
        ]
        assert len(grouped) == 8 and len({row["case_id"] for row in grouped}) == 8
        assert [row["period"] for row in grouped] == [1] * 4 + [2] * 4
        assert grouped[0]["condition"] != grouped[4]["condition"]
        first[grouped[0]["condition"]] += 1
        for group in (grouped[:4], grouped[4:]):
            assert len({row["condition"] for row in group}) == 1
            assert Counter(key[row["case_id"]]["domain"] for row in group) == {
                "ScienceResearch": 2,
                "MathEducation": 2,
            }
        instructions.add(digest(folder / "instructions.md"))
        readers.add(digest(folder / "review.py"))
        allowed = {folder / name for name in ("instructions.md", "schedule.json", "review.py")}
        for position, row in enumerate(grouped):
            identity = row["case_id"]
            positions[identity].append((row["period"], position % 4))
            case = root / row["folder"]
            assert case.resolve().is_relative_to(folder.resolve())
            names = ("before.json", "after.json", "lookup.json", "questions.json")
            allowed.update(case / name for name in (*names, "report.json"))
            content = tuple(digest(case / name) for name in names)
            assert content[:2] == tuple(
                key[identity][f"{side}_sha256"] for side in ("before", "after")
            )
            assert common.setdefault(identity, content) == content
            assert load(case / "questions.json") == key[identity]["questions"]
            report = case / "report.json"
            report_bytes[row["condition"]].append(report.stat().st_size)
            document = load(report)
            links = document["changes"].pop("source_pointers")
            arm = row["condition"]
            assert isinstance(links, list)
            if arm == "no_navigation":
                assert not links
            else:
                assert bool(links) == bool(key[identity]["expected"]["events"])
            navigation_lists[identity, arm] = len(links)
            base = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            assert report_bases.setdefault(identity, base) == base
        assert {path for path in folder.rglob("*") if path.is_file()} == allowed
    assert first == {"navigation": 2, "no_navigation": 2}
    assert len(readers) == len(instructions) == 1
    assert all(len(group) == 2 and group[0] == group[1] for group in positions.values())
    result = {
        "schema_version": "p3if.navigation-ablation-packet-check.v1",
        "case_manifest_sha256": digest(cases),
        "packet_manifest_sha256": digest(trial),
        "sessions": 4,
        "assignments": 32,
        "matched_common_cases": len(common),
        "matched_report_bodies": len(report_bases),
        "changed_reports_with_navigation_only": sum(
            bool(count) for (case_id, arm), count in navigation_lists.items() if arm == "navigation"
        ),
        "hashed_packet_files": len(files),
        "common_reader_sha256": next(iter(readers)),
        "workflow_first": dict(first),
        "report_byte_ranges": {
            arm: [min(values), max(values)] for arm, values in report_bytes.items()
        },
    }
    with receipt.open("x", encoding="utf-8") as output:
        json.dump(result, output, indent=2, sort_keys=True)
        output.write("\n")


if __name__ == "__main__":
    main()
