"""Score isolated held-out reviewer responses against the frozen case key."""

import argparse
import json
from pathlib import Path

from p3if.held_out_reviewer_score import score_review


def main() -> None:
    """Write all scheduled case scores and descriptive paired totals as JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_manifest", type=Path)
    parser.add_argument("packet_manifest", type=Path)
    parser.add_argument("responses_dir", type=Path)
    args = parser.parse_args()
    try:
        score = score_review(args.case_manifest, args.packet_manifest, args.responses_dir)
    except (KeyError, OSError, TypeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(score, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
