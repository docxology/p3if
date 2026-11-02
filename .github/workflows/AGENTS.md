# AGENTS.md — `.github/workflows/`

CI workflow definitions. `ci.yml` is the only workflow: one `test` job that installs
the package (`pip install -e ".[dev,visualization,web]"`) and runs the lint, type,
and test gate on Python 3.9, 3.10, 3.11, and 3.12.

- The gate, in order: `ruff check src tests`, `black --check src tests`,
  `mypy src/p3if --ignore-missing-imports`, `pytest tests/ -v --cov=p3if`.
- Coverage is uploaded with `fail_ci_if_error: false`: a failed upload, or a drop in
  coverage, does not fail the job.
- Actions are pinned to commit SHAs. Preserve the pin when changing a version.
- The workflow is the truth about what CI runs — this guide is not a substitute and
  is not updated automatically when the file changes.

Conventions and the local equivalents of these checks are in the
[root guide](../../AGENTS.md).
