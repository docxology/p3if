"""Build the frozen P3IF citation study snapshots in a new directory."""

import argparse
from pathlib import Path

from p3if.citation_cases import build_cases


def main() -> None:
    """Generate byte-preserving snapshot files and their citation manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        build_cases(
            root / "data/domains",
            root / "docs/manuscript/citation-case-spec.json",
            args.output_dir,
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
