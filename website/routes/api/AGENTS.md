# AGENTS.md — `website/routes/api/`

The JSON API: `domains.py`, `patterns.py`, `relationships.py`, `framework.py`,
`analysis.py`, `visualizations.py`, `export.py`, `health.py`, `spec.py`, and
`common.py` for shared helpers.

- These modules are the API's source of truth. The human-facing description is
  [`../../../docs/api/README.md`](../../../docs/api/README.md), which is written by
  hand and can lag this code.
- Tests: `tests/integration/test_api.py` exercises endpoints in-process. Response
  shapes are asserted only where that file covers them, and there is no schema or
  contract check, so an uncovered response change is a silent breaking change.
- No authentication exists: the API is a local read layer, not a public surface, and
  nothing here should be exposed as one.

Routes guide: [`../AGENTS.md`](../AGENTS.md).
