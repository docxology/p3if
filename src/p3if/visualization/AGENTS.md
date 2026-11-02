# AGENTS.md — `src/p3if/visualization/`

The rendering layer of the P3IF framework. `base.py` defines the `Visualizer`
base class; `static/` renders heatmaps, networks, matrices, hierarchies, grids,
lists, and statistics; `interactive/` builds the 3D cube and force-graph views;
`animated/` renders dimension transitions and sequences; and `portals/` composes
dashboards and the multi-domain portal. Framework semantics live in `../core/`,
not here; [`README.md`](README.md) documents each visualization type.

- Output lands in a timestamped session directory under `outputs/`, driven by
  `scripts/run_all.py --viz` or `scripts/generate_final_visualizations.py
  --output-dir DIR`. Committed run snapshots are not hand-edited; regenerate
  instead.
- Behavior changes need tests under `tests/visualization/` (layout described in
  `tests/visualization/README.md`). CI
  (`.github/workflows/ci.yml`) runs `pytest tests/ -v` on Python 3.9–3.12 along
  with `ruff check`, `black --check`, and `mypy`. The suite exercises the generator
  APIs; no job reviews rendered appearance, so a green run is not a visual review.
- Package rules, typing, and docstring conventions are in
  [`../AGENTS.md`](../AGENTS.md) and the [root guide](../../../AGENTS.md).

This package depends on `../core/` (frameworks and models) and `../utils/`
(configuration, output organization, performance). Keep framework semantics in
`../core/` and session-path policy in `../utils/output_organizer.py` rather than
duplicating either here.
