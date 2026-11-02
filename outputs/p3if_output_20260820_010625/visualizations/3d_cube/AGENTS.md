# AGENTS.md — `outputs/p3if_output_20260820_010625/visualizations/3d_cube/`

The interactive 3D cube from the 2026-08-20 (01:06:25 UTC) run: one page,
`3d-cube.html`, rendered by the interactive visualizer in
`src/p3if/visualization/interactive/`.

- Generated output. Rerun the pipeline to get a fresh page in a new session
  directory; do not edit this HTML by hand.
- Nothing in CI opens, renders, or asserts on this file. A committed page records one
  render; it is not a check of the current renderer.
- This run holds the cube page alone. Other runs in this tree also hold
  `test_cube.html` and `test_cube_with_datasets.html`, written by
  [`../../../../tests/visualization/test_interactive.py`](../../../../tests/visualization/test_interactive.py)
  when a test run points its output at a session directory — test output, not
  pipeline output.
- Read the directory listing for the exact file set; this guide is not a manifest.

Tree rules: [`../../AGENTS.md`](../../AGENTS.md).
