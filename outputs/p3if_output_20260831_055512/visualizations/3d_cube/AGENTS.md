# AGENTS.md — `outputs/p3if_output_20260831_055512/visualizations/3d_cube/`

The interactive 3D cube from the 2026-08-31 (05:55:12 UTC) run: `3d-cube.html`, titled
`P3IF 3D Cube` in the page itself, beside two pages a test run wrote into the same
session directory.

- Generated output. Rerun the pipeline to get a fresh page in a new session directory; do
  not edit this HTML by hand.
- Cube pages come from the interactive visualizer: `generate_3d_cube_html` in
  `src/p3if/visualization/interactive/interactive.py` writes one into the organizer's
  `3d_cube` path, which is where this folder's name comes from. A committed page records
  one render; it is not a check of the current renderer.
- `test_cube.html` and `test_cube_with_datasets.html` are test output, not pipeline
  output: `tests/visualization/test_interactive.py` writes them into whatever output path
  it is configured with, and this session directory is one such path.
- Nothing in CI opens, renders, or asserts on these files.
- Read the directory listing for the exact file set; this guide is not a manifest.

Tree rules: [`../../AGENTS.md`](../../AGENTS.md).
