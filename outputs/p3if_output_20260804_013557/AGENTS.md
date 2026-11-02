# AGENTS.md — `outputs/p3if_output_20260804_013557/`

A committed snapshot of one visualization run from 2026-08-04 (01:35 UTC).
`visualizations/` holds the generated HTML — here the 3D cube view. Session
directories are named `p3if_output_<UTC timestamp>` by the output organizer in
`src/p3if/utils/output_organizer.py`, which the visualization pipeline uses when it
writes results under `outputs/`.

- Generated, not hand-maintained. To reproduce or refresh, re-run the pipeline
  (`scripts/run_all.py --viz`, or the visualization orchestrator); it writes a new
  timestamped folder rather than updating this one.
- Nothing in CI builds or verifies these snapshots, and no test asserts on the
  files here: they record what one run produced, not what the current code
  produces. Read the files rather than assuming the site or library still renders
  the same output.
- The code that renders these views is
  [`../../src/p3if/visualization/`](../../src/p3if/visualization/); the rule for the
  `outputs/` tree is in [`../AGENTS.md`](../AGENTS.md).
