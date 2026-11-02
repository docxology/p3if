# AGENTS.md — `outputs/p3if_output_20260820_194735/visualizations/3d_cube/`

The 3D cube material from the 2026-08-20 (19:47:35 UTC) run: the rendered
`3d-cube.html` plus `test_cube.html` and `test_cube_with_datasets.html`.

- `3d-cube.html` is pipeline output from the interactive visualizer in
  `src/p3if/visualization/interactive/`. The two `test_cube*.html` pages are written
  by [`../../../../tests/visualization/test_interactive.py`](../../../../tests/visualization/test_interactive.py)
  when a test run points its output at this session directory: test output, not
  pipeline output. The folder mixes the two.
- Generated, not hand-maintained: rerunning the pipeline or the tests writes a new
  session directory rather than updating these files.
- Nothing in CI opens or asserts on these pages; their presence says nothing about
  whether the current renderer still produces the same output.
- Not a manifest: the directory listing is the truth for the file set.

Tree rules: [`../../AGENTS.md`](../../AGENTS.md).
