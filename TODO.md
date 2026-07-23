# P3IF TODO — Upcoming Improvements

Items completed in v2.1.0–v2.4.0 are listed in CHANGELOG.md.
Remaining items scoped for future releases:

---

## Architecture & Design (Future)

### A1. Split `framework.py` (~1150 lines) into smaller modules
Potential split: `framework/core.py` (init, repr, len, iter), `framework/patterns.py` (CRUD),
`framework/relationships.py` (CRUD), `framework/metrics.py` (metrics + validation),
`framework/io.py` (import/export), `framework/composition.py` (multiplex, hot_swap).

### A2. Add async versions of add_pattern/add_relationship
The framework is fully synchronous. For I/O-bound storage backends, async methods would help.

---

## Medium — Quality & Maintainability

### Q10. Split `website/routes/api.py` (928 lines) into separate modules
The API routes file handles all endpoints in one file.

### Q11. Add tests for analysis modules (network.py, meta.py, report.py)
The analysis subpackage has no dedicated tests.

### Q12. Add tests for orchestrators (cognitive_security, framework_integration)
The orchestrator examples have no dedicated tests.

### Q13. Extend mypy to remaining core modules
Currently only `models.py`, `framework.py`, `core.py` are mypy-clean. Extend to:
`composition.py`, `orchestration.py`, `validation.py`, `caching.py`, `dimensions.py`,
`exceptions.py`, `performance_monitoring.py`, and the `utils/` and `data/` packages.

---

## Minor — Polish

### P11. Verify all website template routes return 200
Run the Flask app and verify all routes render correctly.

---

## Completed in v2.4.0

- A3: FrameworkBuilder fluent API (method chaining) — DONE
- A4: DomainData Pydantic model for domain JSON validation — DONE
- A5: __eq__ and __hash__ on BasePattern and Relationship — DONE
- P15: __repr__ on ValidationEngine, CacheManager, DomainManager — DONE
- P16: Type stubs (types-requests, types-PyYAML) added — DONE
- Q14: MANIFEST.in modernized — DONE
