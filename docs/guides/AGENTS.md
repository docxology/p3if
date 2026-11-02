# AGENTS.md — `docs/guides/`

Task-oriented setup guides: `installation.md`, `getting-started.md`, and
`configuration.md`.

- Installation facts that can rot are owned elsewhere: the extras (`dev`,
  `visualization`, `web`) are declared in `../../pyproject.toml`, and the CI workflow
  installs `.[dev,visualization,web]`. Check the packaging metadata before trusting a
  command, and update the guide when an extra changes.
- These guides are prose; nothing executes them. No CI job installs from the guide,
  and no test asserts on the commands it gives.
- Read `configuration.md` for settings, but configuration defaults are decided in
  `../../src/p3if/utils/config.py` — that code wins over the document.

Repository rules: [root guide](../../AGENTS.md); docs-tree guide:
[`../AGENTS.md`](../AGENTS.md).
