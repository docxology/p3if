# AGENTS.md — `.github/`

GitHub-side configuration only: `workflows/` holds the repository's CI definition.
Nothing in this folder runs on your machine, and no local command reads it.

- [`workflows/ci.yml`](workflows/ci.yml) is the repository's only automated gate. It
  triggers on pushes to `main`/`develop` and on pull requests to `main`, and runs
  `ruff`, `black --check`, `mypy`, and `pytest` on Python 3.9–3.12. Copy those
  commands rather than inventing a local check.
- Third-party actions are pinned to reviewed commit SHAs (2026-11-02). Keep the pin
  when editing: a floating tag is a supply-chain change, not a convenience.
- There is no deployment, release, docs-build, or scheduled job here, and the
  coverage upload is advisory (`fail_ci_if_error: false`) — a green run proves
  nothing about coverage and publishes nothing.
- Repository settings (branch protection, required checks) live in GitHub settings,
  not in this folder; this guide cannot tell you what they are.

Local conventions are in the [root guide](../AGENTS.md); the workflow file itself is
the authority on what CI runs.
