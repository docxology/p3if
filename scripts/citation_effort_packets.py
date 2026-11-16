"""Generate the four frozen packets for the citation and review effort study."""

import argparse
from pathlib import Path

from p3if.citation_effort_packets import prepare_packets


def main() -> None:
    """Write neutral packet folders and their coordinator digest inventory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir", type=Path, help="Directory of generated citation cases")
    parser.add_argument("output_dir", type=Path, help="New output directory for the four packets")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "docs/manuscript/citation-case-manifest.json",
        help="Preregistered citation case manifest",
    )
    args = parser.parse_args()
    try:
        prepare_packets(args.case_dir, args.manifest, args.output_dir)
    except (KeyError, OSError, TypeError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
