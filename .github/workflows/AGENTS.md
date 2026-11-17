# AGENTS.md — `.github/workflows/`

CI workflow definitions. `ci.yml` is the only workflow: one `test` job that checks
`uv.lock`, installs the locked environment (`uv lock --check`, `uv sync --frozen`) and
runs the lint, type, test and build gate on Python 3.13 and 3.14.

- The gate, in order: `ruff check src tests`, `black --check src tests`,
  `mypy src/p3if --ignore-missing-imports`, `pytest tests/ --cov=p3if
  --cov-report=xml`, then `uv build`, each through `uv run --no-sync`.
- Coverage is uploaded with `fail_ci_if_error: false`: a failed upload, or a drop in
  coverage, does not fail the job.
- Actions are pinned to commit SHAs. Preserve the pin when changing a version.
- The workflow is the truth about what CI runs — this guide is not a substitute and
  is not updated automatically when the file changes.

Conventions and the local equivalents of these checks are in the
[root guide](../../AGENTS.md).
