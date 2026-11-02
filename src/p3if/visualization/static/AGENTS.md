# AGENTS.md — `src/p3if/visualization/static/`

Static rendering: cube, grid, heatmap, hierarchy, list, matrix, network, and
statistical visualizations, plus their older single-purpose entry points
(`matrix.py`, `network.py`). These modules produce the PNGs committed under
[`../../../../visualizations/`](../../../../visualizations/) and inside run folders
under `outputs/`.

- Generated images are regenerated, never edited; the output directory is chosen by
  the caller or by `../utils/output_organizer.py`.
- Tests: `tests/visualization/test_static.py` with the
  remaining checks spread across `test_all_domains.py`. They exercise the generator
  APIs; nothing reviews the rendered image or asserts on the committed PNGs.
- Adding a plot type means adding it to the orchestration the pipeline calls, not only
  a module here — otherwise it never runs.

Repository rules: [root guide](../../../../AGENTS.md); the visualization package
guide is [`../AGENTS.md`](../AGENTS.md).
