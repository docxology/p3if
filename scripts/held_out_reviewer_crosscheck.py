"""Cross-check a complete masked-study result without loading P3IF or scorer code."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys


def read(path):
    source = path.read_bytes()
    return json.loads(source), sha256(source).hexdigest()


def canonical_answer(value):
    events = sorted(
        ({**event, "fields": sorted(event["fields"])} for event in value["events"]),
        key=lambda event: (event["kind"], event["id"]),
    )
    return json.dumps(
        {**value, "events": events}, ensure_ascii=False, sort_keys=True, allow_nan=False
    )


def verify(case_manifest, packet_manifest, responses, score_path):
    key, key_hash = read(case_manifest)
    packet, packet_hash = read(packet_manifest)
    result, result_hash = read(score_path)
    assert key_hash == packet["case_manifest_sha256"] == result["case_manifest_sha256"]
    assert packet_hash == result["packet_manifest_sha256"]

    by_case = {row["case_id"]: row for row in key["cases"]}
    by_arm = defaultdict(dict)
    counts = Counter()
    received = {}
    ordered = defaultdict(list)
    for slot in packet["assignments"]:
        ordered[slot["session"]].append(slot)
    for session, slots in ordered.items():
        raw, digest = read(responses / f"{session}.json")
        assert result["sessions"][session]["sha256"] == digest
        assert result["sessions"][session]["file_status"] == "parsed"
        assert not result["sessions"][session]["unassignable_rows"]
        assert not result["sessions"][session]["duplicate_case_ids"]
        assert len(raw) == len(slots) == 8
        assert [row["case_id"] for row in raw] == [slot["case_id"] for slot in slots]
        for slot, answer in zip(slots, raw):
            case_id, condition = slot["case_id"], slot["condition"]
            case = by_case[case_id]
            assert condition not in by_arm[case_id]
            correct = canonical_answer(case["expected"]) == canonical_answer(answer)
            result_name = "correct" if correct else "incorrect"
            by_arm[case_id][condition] = correct
            counts[case["domain"], condition, result_name] += 1
            received[session, case_id] = result_name

    assert len(received) == len(result["rows"]) == 32
    assert all(received[row["session"], row["case_id"]] == row["result"] for row in result["rows"])
    assert len(by_arm) == 16
    assert all(set(pair) == {"diff", "p3if"} for pair in by_arm.values())
    categories = {
        (True, True): "both_correct",
        (True, False): "p3if_only",
        (False, True): "diff_only",
        (False, False): "neither_correct",
    }
    pairs = Counter(categories[pair["p3if"], pair["diff"]] for pair in by_arm.values())
    assert all(
        result["paired_counts"][category] == pairs[category] for category in categories.values()
    )
    for domain, row in result["domains"].items():
        for condition, totals in row["counts"].items():
            for label in ("correct", "incorrect"):
                assert totals[label] == counts[domain, condition, label]
    return {
        "score_sha256": result_hash,
        "complete_session_arrays": len(ordered),
        "independently_reproduced_cases": len(received),
        "pairs": {category: pairs[category] for category in sorted(categories.values())},
    }


def main():
    """Cross-check a complete comparison using only the standard library."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_manifest", type=Path)
    parser.add_argument("packet_manifest", type=Path)
    parser.add_argument("responses", type=Path)
    parser.add_argument("score", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("Run the cross-check without optimization.")
    try:
        result = verify(args.case_manifest, args.packet_manifest, args.responses, args.score)
    except (AssertionError, KeyError, TypeError, ValueError, OSError) as exc:
        parser.error(f"Independent cross-check failed: {exc}")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
