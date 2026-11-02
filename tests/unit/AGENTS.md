# AGENTS.md — `tests/unit/`

The unit suite, one module per area: models, framework, core, composition, validation,
indexing, caching, orchestration, dimensions, exceptions, logging, analysis,
performance monitoring, and the async storage path.

- Run everything with `pytest tests/unit -v`, or one module with
  `pytest tests/unit/test_models.py -v`. CI runs the full suite, not this directory.
- This is where a behavioural change should be covered first: the integration and
  visualization suites are slower and less precise about which change broke what.
- These tests build real objects through `../fixtures/`; the no-mock rule is stated in
  the [root guide](../../AGENTS.md).
- Nothing here asserts on the committed output under `outputs/` or `visualizations/`.

Repository rules: [root guide](../../AGENTS.md).
