# AGENTS.md — `src/p3if/visualization/interactive/`

Interactive rendering: `interactive.py` (the 3D cube and force-graph views, including
the HTML page writer) and `interactive_3d.py`. This is the code behind the committed
`3d-cube.html` pages under [`../../../../outputs/`](../../../../outputs/).

- Output landing in `outputs/<session>/visualizations/3d_cube/` comes from here; the
  session directory itself is decided by `../utils/output_organizer.py`. Snapshots
  are regenerated, never hand-edited.
- `tests/visualization/test_interactive.py` writes its own `test_cube.html` and
  `test_cube_with_datasets.html` into whatever output path it is configured with —
  several committed run folders hold those two pages beside the pipeline's, which is
  why a folder can mix run output and test output.
- No CI job opens the rendered pages, so a green suite does not mean the views render
  correctly in a browser.

Tests: [`../../../../tests/visualization/`](../../../../tests/visualization/);
repository rules: [root guide](../../../../AGENTS.md).
