# AGENTS.md — `tests/fixtures/`

Shared test builders: `helpers.py` and its package `__init__.py` expose the
constructors that other test modules import to get a framework, a set of patterns, or
a multi-domain setup. They build real framework objects — the repository's rule
against mocks is in the [root guide](../../AGENTS.md).

- Fixtures have no tests of their own: a broken helper shows up as failures across the
  suite, not as a failure beside it. When you change one, run the whole suite.
- Keep them generic. A helper only one module needs belongs in that module, where it
  can be read with its only caller.

Repository rules: [root guide](../../AGENTS.md).
