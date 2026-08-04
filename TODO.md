# P3IF TODO — Upcoming Improvements

Items completed in v2.1.0–v2.5.0 are listed in CHANGELOG.md.
Remaining items scoped for future releases:

---

## Architecture & Design (Future)

### A1. Split `framework.py` (~1170 lines) into smaller modules
DONE in this release: `core/framework.py` is now a `core/framework/` package
(`core.py`, `metrics.py`, `builder.py`, `__init__.py` re-exporting the public
API). All `from p3if.core.framework import ...` imports remain source-compatible.

### A2. Add async versions of add_pattern/add_relationship
The framework is fully synchronous. For I/O-bound storage backends, async methods would help.

---

## Medium — Quality & Maintainability

### Q10. Split `website/routes/api.py` (928 lines) into separate modules

### Q13. Remaining mypy errors in validation.py and caching.py
DONE: all `p3if.core.*` modules are now mypy-clean (validation, caching, and the
analysis/composition/dimensions/orchestration/performance_monitoring modules).
Remaining repo-wide mypy debt (239 errors) is in visualization/data/orchestrator
modules, mostly untyped defs plus numpy-`_Array` stub noise outside the core
strict-typing contract.

---

## Minor — Polish

### P11. Verify all website template routes return 200

---

## Completed in v2.5.0

- Q11: Tests for analysis modules (12 tests) — DONE
- Q12: Tests for orchestrators (20 tests) — DONE
- Q13 (partial): mypy extended to 5 more modules, 73 fewer errors — DONE
