"""Build the frozen P3IF citation study or navigation ablation snapshots."""

import argparse
from pathlib import Path

from p3if.citation_cases import build_cases


def main() -> None:
    """Generate byte-preserving snapshot files and their citation manifest."""
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument(
        "--specification",
        type=Path,
        default=root / "docs/manuscript/citation-case-spec.json",
        help="case specification JSON (defaults to the citation effort study)",
    )
    args = parser.parse_args()
    try:
        build_cases(root / "data/domains", args.specification, args.output_dir)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
