# AGENTS.md — `docs/examples/`

Documentation for the examples, not the examples themselves: [`README.md`](README.md)
lists the thin orchestrators and how to run them.

- The runnable code lives in [`../../src/p3if/orchestrators/`](../../src/p3if/orchestrators/),
  and the runner is `scripts/run_examples.py`. A snippet added here is prose until it
  exists there.
- Nothing executes or tests the documented examples: no doctest runner is configured
  (`pytest.ini` runs `tests/` only), so an example can drift from the code without
  anything failing.
- Nothing is generated in this folder; it holds Markdown only.

Orchestrator conventions: [`../../src/p3if/orchestrators/AGENTS.md`](../../src/p3if/orchestrators/AGENTS.md).
