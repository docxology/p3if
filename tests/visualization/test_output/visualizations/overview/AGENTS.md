# AGENTS.md — `tests/visualization/test_output/visualizations/overview/`

The overview view's test output: the property/process/perspective matrices, the
network and similarity views, and `summary_report.json`. Written by the
overview-visualization test in `tests/visualization/`.

- Generated per test run; rerun the suite to refresh. Read
  `summary_report.json` for the numbers; the PNGs are their illustrations.
- No test asserts on these files, and nothing compares them with the committed
  snapshots under `visualizations/`.

Static rendering code: [`../../../../../src/p3if/visualization/static/`](../../../../../src/p3if/visualization/static/).
