# AGENTS.md — `tests/data/`

Importer and exporter tests: they build frameworks through the real classes and
round-trip them through the supported formats. They do not read the committed domain
files under `../../data/domains/`.

- Run just these with `pytest tests/data -v`. They are the executable description of
  what import and export accept, so a format change belongs here first.
- These are code-level tests: no fixture file outside `../fixtures/` is required, and
  nothing here depends on a run having been executed.

Repository rules: [root guide](../../AGENTS.md).
