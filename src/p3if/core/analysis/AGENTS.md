# AGENTS.md — `src/p3if/core/analysis/`

The analysis engines that read a built framework: `basic.py` (descriptive analysis),
`meta.py` (analysis over frameworks or domains), `network.py` (graph-shaped
relationships), and `report.py` (assembling results for output).

- These modules consume the models in `../models.py` and the framework in
  `../framework/`; they do not own pattern semantics. A new metric belongs here only
  if it reads a framework rather than changing one.
- Tests are in `tests/unit/test_analysis_basic.py` and
  `tests/unit/test_analysis_modules.py`; the visualization tests
  exercise the same analyses indirectly, so a green suite there is not a substitute
  for these.
- No analysis test asserts on the committed images or reports under `visualizations/`
  or `outputs/` — those are snapshots, not fixtures.

Repository rules: [root guide](../../../../AGENTS.md).
