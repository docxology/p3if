#!/usr/bin/env python3
"""Generate masked P3IF reviewer study packets or print a pilot score receipt."""

import argparse
import json
from pathlib import Path

from p3if.reviewer_study import prepare_packets, score_pilot


def main() -> None:
    """Dispatch to the reproducible packet generator or pilot scorer."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    packets = commands.add_parser("packets")
    packets.add_argument("cases", type=Path)
    packets.add_argument("output", type=Path)
    score = commands.add_parser("score")
    score.add_argument("manifest", type=Path)
    score.add_argument("responses", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "packets":
            prepare_packets(args.cases, args.output)
        else:
            print(json.dumps(score_pilot(args.manifest, args.responses), sort_keys=True, indent=2))
    except (KeyError, OSError, ValueError) as error:
        parser.exit(2, f"{error}\n")


if __name__ == "__main__":
    main()
