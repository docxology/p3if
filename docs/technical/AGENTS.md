# AGENTS.md — `docs/technical/`

How the system is built: `architecture.md` (component structure and layering) and
`data_model.md` (patterns, relationships, and how they are stored).

- The code is authoritative. For the data model, the format contract the loaders
  follow is `../../data/README.md`, and the implementation is
  `../../src/p3if/core/models.py` and `src/p3if/data/`; when the prose here disagrees
  with either, fix the prose.
- Nothing validates these documents: no doc build, no doctest, no CI check. They can
  be accurate or years stale, and this guide cannot tell you which.
- Architecture changes that touch the diagrams belong in `../diagrams/` too — update
  both or the pair drifts apart.

Docs-tree guide: [`../AGENTS.md`](../AGENTS.md); repository rules:
[root guide](../../AGENTS.md).
