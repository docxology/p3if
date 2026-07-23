# P3IF TODO — Upcoming Improvements

All items from the v2.1.0–v2.3.0 audits have been completed.
This file tracks remaining improvements for future releases.

---

## Architecture & Design (Future)

### A1. Split `framework.py` (~1100 lines) into smaller modules
Potential split: `framework/core.py` (init, repr, len, iter), `framework/patterns.py` (CRUD),
`framework/relationships.py` (CRUD), `framework/metrics.py` (metrics + validation),
`framework/io.py` (import/export), `framework/composition.py` (multiplex, hot_swap).

### A2. Add async versions of add_pattern/add_relationship
The framework is fully synchronous. For I/O-bound storage backends, async methods would help.

### A3. Add a `FrameworkBuilder` fluent API
`P3IFFramework().add_pattern(...).add_pattern(...).add_relationship(...)` chaining pattern.

### A4. Add typed domain data validation
Domain JSON files are loaded without schema validation. A Pydantic model for domain data
would catch malformed files at load time.

### A5. Add `__eq__` to `BasePattern` and `Relationship`
Currently comparison is by identity (Pydantic default). Adding `__eq__` by name+domain+type
would be useful for deduplication.

---

## Medium — Quality & Maintainability

### Q10. Split `website/routes/api.py` (928 lines) into separate modules
The API routes file handles all endpoints in one file.
Consider splitting into `api/patterns.py`, `api/relationships.py`, `api/domains.py`.

### Q11. Add tests for analysis modules (network.py, meta.py, report.py)
The analysis subpackage has no dedicated tests. NetworkAnalyzer, MetaAnalyzer, and
AnalysisReport need test coverage.

### Q12. Add tests for orchestrators (cognitive_security, framework_integration)
The orchestrator examples have no dedicated tests. CognitiveSecurityOrchestrator and
FrameworkIntegrationOrchestrator need test coverage.

### Q13. Extend mypy to remaining core modules
Currently only `models.py`, `framework.py`, `core.py` are mypy-clean. Extend to:
`composition.py`, `orchestration.py`, `validation.py`, `caching.py`, `dimensions.py`,
`exceptions.py`, `performance_monitoring.py`, and the `utils/` and `data/` packages.

### Q14. Remove or modernize `MANIFEST.in`
With `pyproject.toml` using `setuptools` and `package-data`, `MANIFEST.in` may be
redundant. Verify and potentially remove.

---

## Minor — Polish

### P11. Verify all website template routes return 200
Run the Flask app and verify all routes render correctly.

### P15. Add `__repr__` to `ValidationEngine`, `CacheManager`, `DomainManager`
For consistency with the other core classes that already have `__repr__`.

### P16. Consider adding type stubs for external packages
The project uses `networkx`, `plotly`, `matplotlib` which lack type stubs.
Adding `types-networkx` etc. would improve mypy coverage.

---

## Completed (v2.1.0–v2.3.0)

All MAJOR (M1–M10), MEDIUM (Q1–Q9), and MINOR (P1–P10, P12–P16) items from the
original audit are complete. See CHANGELOG.md for v2.1.0, v2.2.0, and v2.3.0 releases
for full details of what was fixed.
