"""Run the public held-out P3IF conformance protocol against a frozen manifest."""

import argparse
import json
from pathlib import Path

from p3if.held_out_verify import verify_cases


def main() -> None:
    """Write the deterministic receipt and exit unsuccessfully on any failed case."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir", type=Path, help="Directory of generated input pairs")
    args = parser.parse_args()
    manifest = (
        Path(__file__).resolve().parent.parent / "docs/manuscript/held-out-case-manifest.json"
    )
    try:
        receipt = verify_cases(args.case_dir, manifest)
    except (KeyError, OSError, TypeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2))
    if receipt["passed"] != len(receipt["cases"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
