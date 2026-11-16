"""Generate the frozen four-session held-out reviewer packets."""

import argparse
from pathlib import Path

from p3if.held_out_reviewer_packets import prepare_packets


def main() -> None:
    """Write neutral reviewer materials into new, separate session folders."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir", type=Path, help="Directory of generated frozen cases")
    parser.add_argument("output_dir", type=Path, help="New directory for the four packets")
    args = parser.parse_args()
    manifest = (
        Path(__file__).resolve().parent.parent / "docs/manuscript/held-out-case-manifest.json"
    )
    try:
        prepare_packets(args.case_dir, manifest, args.output_dir)
    except (KeyError, OSError, TypeError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
