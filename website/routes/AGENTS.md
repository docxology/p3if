# AGENTS.md — `website/routes/`

The portal's HTTP surface: `docs.py` (browsing the `../../docs/` tree), `domains.py`,
`visualizations.py`, `viz_generate.py` (starting a generation from the UI), and
`api/` for the JSON endpoints.

- Blueprints are registered in `../app.py`: a module added here does nothing until it
  is registered there.
- These modules read repository content (Markdown under `docs/`, JSON under
  `data/domains/`) instead of keeping copies of it; a page that looks wrong is often a
  data or documentation problem, not a routing one.
- Tests: `tests/integration/test_website_routes.py` (in-process client). Nothing drives
  a browser, and no test renders every template, so a route can pass its test and still
  fail on a page nobody requests in CI.

API sub-guide: [`api/AGENTS.md`](api/AGENTS.md); application guide:
[`../AGENTS.md`](../AGENTS.md).
