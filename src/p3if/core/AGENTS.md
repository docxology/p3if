# AGENTS.md — `src/p3if/core/`

The framework's semantics: `framework/` (builder, framework core, metrics),
`models.py` (Property, Process, Perspective, relationships), `analysis/` (basic,
meta, network, report), and the supporting machinery — `composition.py`,
`validation.py`, `indexing.py`, `caching.py`, `orchestration.py`, `dimensions.py`,
`exceptions.py`, `performance_monitoring.py`.

- Keep semantics here. `data/` may load and `visualization/` may render, but neither
  should re-implement what a framework, model, or analysis class already decides.
- Tests: `tests/unit/` covers these modules (run with `pytest tests/unit -v`) and
  `tests/integration/test_core_integration.py` crosses the package boundary. CI runs
  the full suite on Python 3.9–3.12 with `ruff`, `black --check`, and `mypy`.
- Caching and indexing change performance without changing the API: measure with
  `scripts/benchmark_performance.py` instead of assuming an improvement.
- Not an inventory: the directory listing and the package `README.md` are current;
  this guide is not updated when modules are added.

Sub-guides: [`analysis/AGENTS.md`](analysis/AGENTS.md),
[`framework/AGENTS.md`](framework/AGENTS.md); repository rules:
[root guide](../../../AGENTS.md).
