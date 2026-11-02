# AGENTS.md — `src/p3if/orchestrators/`

Thin-orchestrator examples: `cognitive_security.py`, `framework_integration.py`,
`healthcare_domain.py`, and `integration_examples.py`. Each composes framework
operations into a workflow without becoming a second framework — the pattern is
defined in `../core/orchestration.py`.

- These are examples that run: `scripts/run_examples.py` executes them, and
  `scripts/run_all.py` includes that step in the full pipeline. Their output belongs
  under a session directory in `outputs/`, not beside the modules.
- Tests: `tests/unit/test_orchestrators.py` and
  `tests/unit/test_orchestrator_modules.py`. When adding an orchestrator, mirror their
  fixture style — the repository rule against mock objects is stated in the
  [root guide](../../../AGENTS.md).
- An orchestrator that grows business logic belongs in `../core/`; keep these thin, or
  the example stops demonstrating the pattern.

Runner: [`../../../scripts/run_examples.py`](../../../scripts/run_examples.py).
