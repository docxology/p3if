# AGENTS.md — `src/p3if/data/`

Data handling for the framework: `domain_model.py` and `domains.py` (discovering and
loading the domain library), `importers.py` and `exporters.py` (moving frameworks in
and out of the supported formats), and `synthetic.py` (generating test frameworks).

- The files this package loads are the repository's [`../../../data/`](../../../data/)
  tree; the format contract is `data/README.md`. Domain discovery reads
  `data/domains/index.json`, so a new domain must appear there.
- Tests: `tests/data/test_importers.py` and `tests/data/test_exporters.py`, with
  fixtures from `tests/fixtures/`. They cover the code, not the committed domain
  files: invalid domain JSON is found at load time, not in CI.
- Import/export round-trips are the risky surface — when a format changes, extend the
  tests rather than the docstring.

Repository rules: [root guide](../../../AGENTS.md).
