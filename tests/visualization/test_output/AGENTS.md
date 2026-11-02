# AGENTS.md — `tests/visualization/test_output/`

Committed output from past runs of the visualization tests: per-domain HTML pages,
dashboards and their PNGs, static plots, portal assets, and the JSON data a portal
embeds. `../README.md` describes the suite that writes it.

- Generated, not authored. Rerun the suite (`pytest tests/visualization -v`, or
  `run_visualization_tests.py`) to refresh it; do not edit files here and do not treat
  them as fixtures — no test asserts on them.
- The suite writes wherever its output directory is configured, and this folder is the
  committed instance of that directory. Its contents record one past run, not what the
  current renderer produces.
- Not a manifest: the directory listing is the truth for what is here.

Suite: [`../AGENTS.md`](../AGENTS.md); test rules:
[`../../AGENTS.md`](../../AGENTS.md).
