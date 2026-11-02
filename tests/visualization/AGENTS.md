# AGENTS.md — `tests/visualization/`

Visualization tests and their runners: `test_static.py`, `test_interactive.py`,
`test_animated.py`, `test_dashboard.py`, `test_portal.py`,
`test_integrated_website.py`, `test_all_domains.py`, `test_base.py`, `test_config.py`,
and the `run_*` scripts. Run them with `pytest tests/visualization -v`.

- These tests write files, including `test_cube.html` and
  `test_cube_with_datasets.html`, into whichever output directory they are configured
  with — normally `test_output/`, and in some committed run folders a session
  directory under `outputs/`.
- They check that generation runs and produces artefacts. Nothing opens or reviews the
  rendered page, so a green run is not a visual review and CI cannot see a broken
  layout.
- `test_output/` is committed output from past runs of this suite; see
  [`test_output/AGENTS.md`](test_output/AGENTS.md). Do not edit it — rerun the suite.

Rendering code: [`../../src/p3if/visualization/`](../../src/p3if/visualization/);
repository rules: [root guide](../../AGENTS.md).
