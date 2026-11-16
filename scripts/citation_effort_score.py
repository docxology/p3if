"""Replay exact citation and effort scores from a frozen study batch."""

import argparse
import json
from pathlib import Path

from p3if.citation_effort_score import score_study


def main() -> None:
    """Print a deterministic study receipt from archived inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_manifest", type=Path)
    parser.add_argument("packet_manifest", type=Path)
    parser.add_argument("submissions", type=Path)
    args = parser.parse_args()
    try:
        result = score_study(args.case_manifest, args.packet_manifest, args.submissions)
    except (OSError, TypeError, ValueError, KeyError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
