# AGENTS.md — `examples/`

A package marker, not a folder of examples: `__init__.py` carries a docstring and
nothing else. The runnable examples are the thin orchestrators in
`src/p3if/orchestrators/`, and [`README.md`](README.md) here points at them and at
`scripts/run_examples.py`.

- Why it exists: it keeps the historical import path working, so code and docs that
  say `examples` still resolve. There is no code here to test, lint, or run.
- Behavior and conventions for the actual examples live in
  [`../src/p3if/orchestrators/AGENTS.md`](../src/p3if/orchestrators/AGENTS.md) and the
  [root guide](../AGENTS.md); do not add example implementations to this package.

Runner: [`../scripts/run_examples.py`](../scripts/run_examples.py).
