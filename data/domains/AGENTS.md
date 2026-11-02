# AGENTS.md — `data/domains/`

The domain library: one JSON file per domain (healthcare, climate change, quantum
computing, and so on), `index.json` naming them, and `template_domain.json` as the
starting point for a new one.

- The format is defined in [`../README.md`](../README.md); domain discovery reads
  `index.json` (`src/p3if/data/synthetic.py`), and the website routes skip both
  `index.json` and `template_domain.json` when listing domains, so a new domain must
  be registered in the index rather than only added as a file.
- No test asserts on these files. The suite covers the loader and exporter code with
  its own fixtures; an invalid domain file is discovered at load time, not in CI.
- Do not treat the file list here as stable: read the listing and `index.json` for the
  current set, and keep the two in step.

Loader code: [`../../src/p3if/data/`](../../src/p3if/data/).
