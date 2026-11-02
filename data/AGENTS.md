# AGENTS.md — `data/`

The repository's domain data and the contract that describes it. `domains/` holds one
JSON file per domain; the loose files at this level (`cube_data.json`,
`graph_data.json`, `summary.json`) are the dataset exports the portal generator
writes into a run's `data/` directory.

- [`README.md`](README.md) is the format contract: field names, the domain index, and
  how loaders read these files. Read it before adding a domain or changing a field;
  this guide deliberately does not restate it.
- Domain JSON is content, not code. The loaders (`src/p3if/data/domains.py`,
  `importers.py`) have tests under `tests/data/`, but nothing validates the committed
  domain files: a malformed domain surfaces when a run loads it, not in CI.
- The three loose files are generated exports, not sources — regenerate them through
  the portal rather than editing them by hand.
- Not an inventory: the listing is the truth for which files exist.

Loader and generator code: [`../src/p3if/data/`](../src/p3if/data/); repository rules:
[root guide](../AGENTS.md).
