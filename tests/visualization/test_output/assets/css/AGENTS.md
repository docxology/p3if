# AGENTS.md — `tests/visualization/test_output/assets/css/`

`styles.css`, written by the visualization tests for the portal pages they generate —
the same file `_create_css_file` in `src/p3if/visualization/portals/portal.py` emits
beside every portal.

- Generated output, refreshed by rerunning the test suite; not a hand-maintained
  stylesheet.
- Nothing asserts on it: a stale copy here cannot fail a test.

Portal code: [`../../../../../src/p3if/visualization/portals/`](../../../../../src/p3if/visualization/portals/).
