# AGENTS.md — `tests/visualization/test_output/data/`

The JSON a generated portal embeds, written by the visualization tests:
`cube_data.json`, `graph_data.json`, and `summary.json`. The portal generator writes
the same three files into every portal's `data/` directory
(`src/p3if/visualization/portals/portal.py`).

- Generated per test run; rerun the suite to refresh. Editing these files changes
  nothing but the committed copy.
- Their schemas are whatever the current portal code emits; this folder records one
  past run and nothing verifies it against today's writer.

Portal code: [`../../../../src/p3if/visualization/portals/`](../../../../src/p3if/visualization/portals/).
