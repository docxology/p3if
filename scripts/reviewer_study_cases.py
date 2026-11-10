"""Generate the frozen two-domain reviewer pilot cases from shipped fixtures."""

import argparse
from pathlib import Path

from p3if.reviewer_study_cases import build_cases


def main() -> None:
    """Generate pilot snapshots and a sealed-answer manifest in a new directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path, help="New directory for pilot inputs")
    output = parser.parse_args().output_dir
    root = Path(__file__).resolve().parent.parent
    try:
        build_cases(
            root / "data/domains",
            root / "docs/manuscript/reviewer-study-case-spec.json",
            output,
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
