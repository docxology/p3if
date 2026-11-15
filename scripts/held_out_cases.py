"""Build the frozen held-out P3IF interchange cases in a new directory."""

import argparse
from pathlib import Path

from p3if.held_out_cases import build_cases


def main() -> None:
    """Generate before/after files and the case manifest from shipped inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    output = parser.parse_args().output_dir
    root = Path(__file__).resolve().parent.parent
    try:
        build_cases(
            root / "data/domains",
            root / "docs/manuscript/held-out-case-spec.json",
            output,
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
