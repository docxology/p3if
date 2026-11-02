# AGENTS.md — `tests/utils/`

Tests for the utility package: configuration loading (`test_config.py`) and the
storage layer (`test_storage.py`).

- Run with `pytest tests/utils -v`.
- Output-path policy is not tested here. Session naming and directory layout come from
  `../../src/p3if/utils/output_organizer.py` and are exercised indirectly by the
  visualization tests, so a change to where runs write is more likely to surface
  there; the async storage path is covered in `../unit/test_async_storage.py`.

Repository rules: [root guide](../../AGENTS.md).
