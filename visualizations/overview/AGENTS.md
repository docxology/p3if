# AGENTS.md — `visualizations/overview/`

Overview-level static plots from one visualization run, committed as a snapshot: the
network and domain-similarity views, the three property/process/perspective matrices,
and `summary_report.json` with the numbers behind them.

- Generated output. Regenerate rather than edit; the generator writes into a
  timestamped session directory under `outputs/` by default, so this folder is
  refreshed only when an output directory is passed explicitly.
- Read `summary_report.json` for the run's numbers. Nothing verifies they still match
  what the code would compute today, and no test or CI job reads this folder.
- Listing first: this guide is not a manifest.

Static rendering code: [`../../src/p3if/visualization/static/`](../../src/p3if/visualization/static/).
