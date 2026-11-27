"""Replay the article's two local cases and generate measured evidence."""

import json
from pathlib import Path
import subprocess
import sys

import matplotlib.pyplot as plt

from p3if.interchange import load_interchange
from p3if.interchange_analysis import analyze_interchange, compare_interchange


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"


def main() -> None:
    data = OUTPUT / "data"
    data.mkdir(parents=True, exist_ok=True)
    source_domain = ROOT / "data" / "domains" / "scienceresearch.json"
    snapshot = data / "science-snapshot.json"
    subprocess.run([
        sys.executable, "-m", "p3if", "migrate", str(source_domain),
        "--id", "p3if.science-research", "--name", "Science research",
        "--output", str(snapshot),
    ], cwd=ROOT, check=True)
    science = analyze_interchange(load_interchange(snapshot.read_bytes()))
    triple = science.spaces[-1]
    if (science.relationship_count, triple.observed, triple.possible) != (71, 71, 112500):
        raise ValueError("ScienceResearch did not reproduce the recorded relationship counts.")

    fixture = ROOT / "examples" / "interchange" / "framework-v1.json"
    before_bytes = fixture.read_bytes()
    edited = json.loads(before_bytes)
    changed_process = "process.recheck-intake"
    edited["processes"].append({
        "id": changed_process, "name": "Recheck intake", "domain": "synthetic-archive",
    })
    link = next(row for row in edited["relationships"] if row["id"] == "relationship.fidelity-at-intake")
    link["process_id"] = changed_process
    del link["strength"]
    before = load_interchange(before_bytes)
    after = load_interchange(json.dumps(edited, ensure_ascii=False).encode())
    comparison = compare_interchange(before, after)
    groups = {row.kind: row for row in comparison.groups}
    modified = groups["relationship"].modified
    if groups["process"].added != (changed_process,) or len(modified) != 1:
        raise ValueError("The revision did not reproduce a single added process and modified link.")
    if not modified[0].rewired or set(modified[0].fields) != {"process_id", "strength"}:
        raise ValueError("The revision did not identify the changed endpoint and score presence.")
    before_report = analyze_interchange(before)
    after_report = analyze_interchange(after)
    if (
        before_report.spaces[-1].observed, before_report.spaces[-1].possible,
        after_report.spaces[-1].observed, after_report.spaces[-1].possible,
        before_report.strength.zero, before_report.strength.omitted, after_report.strength.omitted,
    ) != (1, 2, 1, 4, 1, 1, 2):
        raise ValueError("The sparse coverage or strength counts differ from the controlled result.")
    reports = {
        "scienceresearch": science.model_dump(mode="json"),
        "archive_before": before_report.model_dump(mode="json"),
        "archive_after": after_report.model_dump(mode="json"),
        "comparison": comparison.model_dump(mode="json"),
    }
    (data / "interchange-evidence.json").write_text(json.dumps(reports, indent=2) + "\n")

    figures = OUTPUT / "figures"
    figures.mkdir(exist_ok=True)
    labels = [row.axis.capitalize() for row in science.axes]
    linked = [row.linked for row in science.axes]
    unlinked = [row.unlinked for row in science.axes]
    image, axes = plt.subplots(figsize=(7.4, 3.5), layout="constrained")
    axes.barh(labels, linked, color="#245192", label="Linked")
    axes.barh(labels, unlinked, left=linked, color="#d4a142", label="Unlinked")
    axes.invert_yaxis()
    axes.set_xlabel("Declared identities")
    axes.legend()
    image.savefig(figures / "declared-coverage.png", dpi=170)
    plt.close(image)
    registry = {"figures": [{
        "label": "fig:declared-coverage",
        "filename": "declared-coverage.png",
        "caption": "Declared linked and unlinked identities by axis in ScienceResearch.",
        "alt_text": "Every axis has linked and unlinked identities. The perspective axis has the largest unlinked count.",
        "generated_by": "python -m docs.reproduce_interchange",
    }]}
    (figures / "figure_registry.json").write_text(json.dumps(registry, indent=2) + "\n")

    print("Verified the ScienceResearch census and the controlled interchange revision.")


if __name__ == "__main__":
    main()
