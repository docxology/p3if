# P3IF methods

The [interchange methods note](../studies/METHODS.md) defines the measurements and provides commands to reproduce a domain-library census and a controlled revision comparison. The [ScienceResearch editorial audit](../studies/scienceresearch-audit.md) applies those methods to a public worked case and proposes a reviewer study.

The [reviewer study preregistration](../studies/reviewer-study-preregistration.md) freezes the cases and scoring rules and separates the technical pilot from the planned human study.


The [technical reviewer pilot](../studies/reviewer-study-pilot.md) reports the two-domain crossover and provides the raw submissions and reproducible scores.

The [held-out conformance follow-up](../studies/held-out-conformance.md) verifies compound changes, transport identity, and exact citations across 16 new snapshot pairs. Its [registration](../studies/held-out-preregistration.md) and receipts let readers reproduce the technical checks.

The [masked held-out model comparison](../studies/held-out-reviewer.md) archives four independent model submissions, the packet inventory, and the matched results for P3IF audit and transition versus a stable-ID diff.

The [citation accuracy and review effort comparison](../studies/citation-effort-results.md) publishes four masked model sessions on new revisions, their raw reader logs, and exact reproduction commands.

The [source navigation ablation](../studies/navigation-ablation-results.md) isolates the navigation array on fresh held-out revisions and publishes exact citation scores, measured reader effort, and live FOLIO verification.

## Render the manuscript

Use Git, uv, Pandoc with matching pandoc-crossref, and XeLaTeX. The local
replay measures the shipped ScienceResearch example and a controlled
revision of the synthetic intake graph. It produces the measurements consumed
by the numbered article. The study reports and preregistrations
remain available at the links above.

From the P3IF checkout, register a clean worktree in a separate Template checkout.

```sh
template_dir=/absolute/path/to/template
project_dir="$template_dir/projects/working/p3if"
git -C "$template_dir" switch --detach 87704feae0a4490ef7dad9c931d268e8c30273c2
mkdir -p "$template_dir/projects/working"
git worktree add --detach "$project_dir" HEAD
(
  cd "$project_dir"
  uv sync --locked --no-dev --python 3.14
  uv run --no-sync --python 3.14 python -m docs.reproduce_interchange
)
cd "$template_dir"
uv sync --locked --no-dev --python 3.14
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/p3if
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/p3if
```

The PDF, HTML, figure, JSON measurements and validation receipts are under
`projects/working/p3if/output/`. [Template prerequisites](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/RUN_GUIDE.md)
