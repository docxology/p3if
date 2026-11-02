# AGENTS.md — `tests/`

The test suite: `unit/`, `integration/`, `data/`, `utils/`, `fixtures/`, and
`visualization/`, plus `conftest.py` and `run_all_tests.py`. `pytest.ini` fixes the
layout (`testpaths = tests`, `pythonpath = src`) and defines the markers `unit`,
`integration`, `visualization`, and `slow`.

- CI runs `pytest tests/ -v --cov=p3if` on Python 3.9–3.12 after `ruff check`,
  `black --check`, and `mypy` (`.github/workflows/ci.yml`). Run the same commands for
  a change; a subset that passes is not the gate.
- The repository rule against mock objects is explicit: use the real P3IF classes and
  `pytest.skip` when an optional dependency is missing. It is stated in the
  [root guide](../AGENTS.md).
- The four markers are declared in `pytest.ini` but effectively unused: as of
  2026-11-02 the only marker applied anywhere under `tests/` is `pytest.mark.asyncio`,
  in one unit module. Select by path (`pytest tests/unit -v`) rather than by `-m`.
- `tests/visualization/test_output/` is committed output from past test runs, not an
  input the suite asserts on.

Shared builders: [`fixtures/AGENTS.md`](fixtures/AGENTS.md).
