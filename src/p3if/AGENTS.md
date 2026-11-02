# AGENTS.md — `src/p3if/`

The importable package, in five parts: `core/` (models, frameworks, analysis,
validation, caching), `data/` (domain management, importers, exporters, synthetic
data), `orchestrators/` (thin orchestrator examples), `utils/` (configuration,
logging, storage, performance, output organization), and `visualization/` (static,
interactive, animated, portals). `py.typed` marks the package as typed.

- Keep the layering: `core/` owns semantics, `data/` loads and writes, `utils/`
  supports both, `visualization/` renders, and `orchestrators/` composes. A module
  that needs another layer's job is a design change, not a local convenience.
- Conventions that CI and review enforce — complete type hints, Google-style
  docstrings, absolute `from p3if...` imports, no mock objects in tests — are stated
  in the [root guide](../../AGENTS.md). Follow that, not a local variant.
- Subpackage guides: [`core/AGENTS.md`](core/AGENTS.md), [`data/AGENTS.md`](data/AGENTS.md),
  [`orchestrators/AGENTS.md`](orchestrators/AGENTS.md), [`utils/AGENTS.md`](utils/AGENTS.md),
  [`visualization/AGENTS.md`](visualization/AGENTS.md).
- Tests live under `tests/`, never inside the package; CI runs them on Python
  3.9–3.12.
