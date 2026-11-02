# AGENTS.md — `src/p3if/core/framework/`

The framework implementation: `builder.py` (constructing frameworks),
`core.py` (the framework class and its operations), and `metrics.py` (framework-level
measurements).

- `core.py` is the largest behavioural surface in the package: pattern storage,
  indexing, validation hooks, and caching compose here. Change it with the tests in
  `tests/unit/test_framework.py`, `test_core.py`, and `test_builder_and_models.py`
  open, and expect `tests/integration/` to notice cross-package effects.
- Keep measured behaviour measured: `metrics.py` and the performance monitoring in
  `../performance_monitoring.py` exist so claims about speed come from a run
  (`scripts/benchmark_performance.py`), not from reading the code.
- Not a manifest: read the listing and the package README for what is here.

Repository rules: [root guide](../../../../AGENTS.md).
