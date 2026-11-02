# AGENTS.md — `visualizations/`

A committed snapshot of generated static visualizations: `domain/` and `overview/`
hold PNGs plus a `summary_report.json`, and `force-graph.html` is an interactive
view. They are written by the visualization package in `src/p3if/visualization/`.

- Generated, not hand-maintained. The generators write into a session directory
  (`scripts/generate_final_visualizations.py` defaults to
  `outputs/visualizations_<timestamp>/`; `scripts/run_all.py` uses its own session
  tree), so a rerun does not refresh this folder unless an output directory is passed
  explicitly. Do not edit the images or the JSON by hand.
- Nothing in CI builds or checks this tree, and no test asserts on it: the committed
  images say nothing about what the current renderer produces.
- `tests/visualization/test_output/` holds a separate, test-generated copy of similar
  plots. The two trees are independent snapshots, not versions of one another.
- Not a manifest: read the listing for what is here.

Rendering code: [`../src/p3if/visualization/`](../src/p3if/visualization/); repository
rules: [root guide](../AGENTS.md).
