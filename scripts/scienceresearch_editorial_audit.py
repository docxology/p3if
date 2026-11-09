"""Generate three public snapshots for the ScienceResearch editorial audit.

Run from the repository root with P3IF installed and a new output directory.
The worked case documents the proposal and how to audit the generated files.
"""

import argparse
import json
from pathlib import Path

from p3if.cli import main as p3if_main


def main() -> int:
    """Migrate the shipped fixture and write its two controlled variants.

    Returns:
        Zero on success or the P3IF CLI's migration exit status.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path, help="New directory for the snapshots")
    output_dir = parser.parse_args().output_dir
    try:
        output_dir.mkdir()
    except OSError as error:
        parser.error(str(error))
    baseline = output_dir / "baseline.json"
    status = p3if_main(
        [
            "migrate",
            "data/domains/scienceresearch.json",
            "--id",
            "p3if.science-research",
            "--name",
            "Science research",
            "--output",
            str(baseline),
        ]
    )
    if status:
        return status

    document = json.loads(baseline.read_text(encoding="utf-8"))
    with (output_dir / "encoding-only.json").open("x", encoding="utf-8", newline="\n") as output:
        json.dump(document, output, ensure_ascii=False, indent=2)
        output.write("\n")

    relationship = next(
        row
        for row in document["relationships"]
        if row["id"] == "2df34732-0613-4919-adfe-0c871ad9ccd4"
    )
    if relationship["process_id"] != "096bd1eb-52ba-4bde-8396-56814f8da38b":
        parser.error("The shipped relationship no longer points to Sustainability Analysis.")
    relationship["process_id"] = "97e2f3ad-597c-4bc1-bf01-e29105879c50"
    del relationship["strength"]
    del relationship["confidence"]
    relationship["status"] = "proposed"
    relationship["evidence_sources"] = [
        "https://journals.plos.org/plosone/s/data-availability",
        "https://www.springernature.com/gp/authors/research-data-policy/"
        "data-availability-statements",
    ]
    with (output_dir / "proposal.json").open("x", encoding="utf-8", newline="\n") as output:
        json.dump(document, output, ensure_ascii=False, indent=2)
        output.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
