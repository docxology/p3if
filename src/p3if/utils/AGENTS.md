# AGENTS.md — `src/p3if/utils/`

Shared support code: `config.py` (configuration), `logging.py`, `json.py` (P3IF-aware
serialization), `storage.py` (including async persistence), `performance.py` and
`benchmark.py` (timing), `command_runner.py`, `fixtures.py`, and
`output_organizer.py`.

- `output_organizer.py` decides where runs write: session directories named
  `p3if_output_<UTC timestamp>` under `outputs/`. Several folder guides and
  `scripts/*.py` depend on that naming, so changing it changes the shape of
  everything committed under `outputs/`.
- Tests: `tests/utils/test_config.py` and `tests/utils/test_storage.py`, plus
  `tests/unit/test_async_storage.py`, `test_logging.py`, and
  `test_performance_monitoring.py`.
- A utility that starts knowing about frameworks or visualization belongs in another
  package; these modules stay usable by both.

Repository rules: [root guide](../../../AGENTS.md).
