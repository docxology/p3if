# AGENTS.md — `src/`

Source root: one package, `p3if/`, laid out for `src`-based installation. The build
configuration (`pyproject.toml`), the pytest `pythonpath` (`pytest.ini`), and
`MANIFEST.in` all assume this layout.

- Import the package as `p3if`, never by path: the test suite finds it through
  `pytest.ini`, and CI installs it in editable mode before running anything.
- Nothing in `src/` is generated and nothing here is data. Rendering output lives
  under `outputs/` and `visualizations/`; domain JSON lives under `data/`.
- No test module lives under `src/`: the suite is in [`../tests/`](../tests/), and CI
  (`.github/workflows/ci.yml`) runs it together with lint and type checks.

Package-level guidance: [`p3if/AGENTS.md`](p3if/AGENTS.md); repository rules,
including the no-mock rule for tests: [root guide](../AGENTS.md).
