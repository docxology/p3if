# AGENTS.md — `tests/`

The test suite: `unit/`, `integration/`, `data/`, `utils/`, `fixtures/`, and
`visualization/`, plus `conftest.py` and `run_all_tests.py`. `pytest.ini` fixes the
layout (`testpaths = tests`, `pythonpath = src`) and defines the markers `unit`,
`integration`, `visualization`, and `slow`.

- The [tracked CI workflow](../.github/workflows/ci.yml) configures Python 3.13
  and 3.14. Use its full local qualification commands for a change.

  - **Install dependencies** runs `uv lock --check` and `uv sync --frozen`.
  - **Run linting** runs `uv run --no-sync ruff check src tests` and
    `uv run --no-sync black --check src tests`.
  - **Run type checking** runs `uv run --no-sync mypy src/p3if --ignore-missing-imports`.
  - **Run tests** runs `uv run --no-sync pytest tests/ --cov=p3if --cov-report=xml`.
  - **Build package** runs `uv build`.

- The repository rule against mock objects is explicit: use the real P3IF classes and
  `pytest.skip` when an optional dependency is missing. It is stated in the
  [root guide](../AGENTS.md).
- Select unit, integration, and visualization tests by directory. Their registered
  category markers currently select zero tests. See [the test guide](README.md).
- `tests/visualization/test_output/` is committed output from past test runs, not an
  input the suite asserts on.

Shared builders: [`fixtures/AGENTS.md`](fixtures/AGENTS.md).
