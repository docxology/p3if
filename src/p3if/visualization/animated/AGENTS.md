# AGENTS.md — `src/p3if/visualization/animated/`

Animated rendering: `animated_dimensions.py` (dimension transitions) and
`animation_visualizations.py` (sequences), built on the base `Visualizer` in
`../base.py`. Use them when a view has to show change over time or dimension rather
than a single state.

- Output is written into a run's session directory under `outputs/` by the
  visualization pipeline; committed snapshots are read-only records — regenerate, do
  not edit.
- Tests: `tests/visualization/test_animated.py`. The suite
  exercises the generator APIs; no job reviews the rendered animation, so a passing
  test is not a visual check.

Repository rules: [root guide](../../../../AGENTS.md); the visualization package
guide is [`../AGENTS.md`](../AGENTS.md).
