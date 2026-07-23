# P3IF TODO — Upcoming Improvements

Items completed in v2.1.0–v2.5.0 are listed in CHANGELOG.md.
Remaining items scoped for future releases:

---

## Architecture & Design (Future)

### A1. Split `framework.py` (~1170 lines) into smaller modules
Potential split: `framework/core.py`, `framework/patterns.py`, `framework/relationships.py`,
`framework/metrics.py`, `framework/io.py`, `framework/composition.py`.

### A2. Add async versions of add_pattern/add_relationship
The framework is fully synchronous. For I/O-bound storage backends, async methods would help.

---

## Medium — Quality & Maintainability

### Q10. Split `website/routes/api.py` (928 lines) into separate modules

### Q13. Remaining mypy errors in validation.py and caching.py
32 errors remain in constraint-checking code where `constraint.get("attribute")`
returns Optional and is passed to `hasattr`/`getattr`. Needs restructuring to
cast or assert non-None before use.

---

## Minor — Polish

### P11. Verify all website template routes return 200

---

## Completed in v2.5.0

- Q11: Tests for analysis modules (12 tests) — DONE
- Q12: Tests for orchestrators (20 tests) — DONE
- Q13 (partial): mypy extended to 5 more modules, 73 fewer errors — DONE
