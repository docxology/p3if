# AGENTS.md — `src/p3if/visualization/portals/`

Composed web output: `portal.py` (the full portal, its HTML, CSS, and JS assets),
`dashboard.py` (dashboards and their plots), `multi_domain_portal.py`, and
`orchestrator.py` (driving the generation). The `assets/` copies committed at the
repository root and inside run folders come from this code.

- The portal writes a complete directory tree per run: HTML pages, `assets/css`,
  `assets/js`, and a `data/` directory holding `cube_data.json`, `graph_data.json`,
  and `summary.json`. Regenerate to change any of it.
- Tests: `tests/visualization/test_portal.py`, `test_dashboard.py`, and
  `test_integrated_website.py`. They check generation, not
  appearance, and nothing runs the portal in CI.

Repository rules: [root guide](../../../../AGENTS.md); the visualization package
guide is [`../AGENTS.md`](../AGENTS.md).
