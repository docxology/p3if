# P3IF TODO — Upcoming Improvements

Comprehensive scoped improvements identified during the v2.1.0 audit.
Items are prioritized: MAJOR (correctness/security), MEDIUM (quality), MINOR (polish).

---

## MAJOR — Correctness & Security

### M1. Stale `run_multidomain_portal.py` references across 8 docs files
The script `scripts/run_multidomain_portal.py` does not exist. References in:
- `docs/tutorials/multi-domain-analysis.md:27`
- `docs/tutorials/basic-usage.md:160, 269, 350`
- `docs/visualization/README.md:83`
- `docs/visualization/domain_visualizations.md:119, 122`
- `docs/FAQ.md:307`
- `docs/guides/getting-started.md:42, 87`
**Fix:** Replace all with `scripts/generate_final_visualizations.py` or create the script.

### M2. Stale `validate_documentation.py` / `validate_documentation_accuracy.py` references
- `CONTRIBUTING.md:365, 368` references `scripts/validate_documentation.py` (doesn't exist)
- `docs/DOCUMENTATION_IMPROVEMENTS_SUMMARY.md:53` references `validate_documentation_accuracy.py`
**Fix:** Replace with `scripts/validate_system.py`.

### M3. `yourusername` placeholder in 7 files
- `CONTRIBUTING.md:20` — clone URL
- `website/README.md:16` — clone URL
- `docs/guides/getting-started.md:18` — clone URL
- `website/templates/base.html:79, 86` — GitHub links
- `website/templates/about.html:153, 210` — GitHub links
**Fix:** Replace all `yourusername` with `docxology`.

### M4. `setup.py` references in 4 files
- `website/app.py:161` — exclude_patterns references `setup.py`
- `website/run.py:79` — same
- `docs/guides/installation.md:88` — `python setup.py install`
- `src/p3if/utils/output_organizer.py:59` — project root detection
**Fix:** Remove setup.py from exclude patterns; update installation guide to `pip install -e ".[dev,web]"`; the output_organizer fallback is harmless but should prefer pyproject.toml.

### M5. `docs/docs_validation_report.json` references nonexistent scripts
Line 252 lists 10 nonexistent scripts as "missing docstrings."
**Fix:** Delete or regenerate this stale report.

### M6. Duplicate docstring in `cognitive_security.py`
Lines 1-6 and 8-19 have the same module docstring duplicated.
**Fix:** Remove the duplicate.

### M7. `integration_examples.py` hardcoded timestamp
Line 190: `"analysis_timestamp": "2024-01-01T00:00:00Z"` — hardcoded instead of `datetime.now()`.
**Fix:** Use `datetime.now().isoformat()`.

### M8. `integration_examples.py` class-level `logger` assignment
Line 27: `logger = logging.getLogger(__name__)` is a class-level attribute in a `@dataclass`, which creates a shared mutable class variable, not an instance attribute.
**Fix:** Move to `__post_init__` or use `field(default_factory=lambda: logging.getLogger(__name__))`.

### M9. `_resolve_conflicts` accesses `conflicts["element_conflicts"]` without `.get()`
Line 234: `conflicts["element_conflicts"].items()` — KeyError if key missing.
**Fix:** Use `conflicts.get("element_conflicts", {}).items()`.

### M10. Website `app.py` hardcoded secret key
Line 40: `app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'p3if-development-key')`
**Fix:** In production, should raise if no secret key set. Add a warning log at minimum.

---

## MEDIUM — Quality & Maintainability

### Q1. `report.py` hardcoded magic numbers
- Line 182: `measures["degree"][:5]` — should be a `top_n` parameter
- Line 197: `[:3]` — top 3 communities, should be configurable
**Fix:** Add `top_n: int = 5` parameter to `get_network_summary()`.

### Q2. `dimensions.py` uses plain dicts, not Pydantic models
`PropertyManager`, `ProcessManager`, `PerspectiveManager` manage plain dict objects instead of `Property`/`Process`/`Perspective` models. This is by design as a lightweight alternative, but creates an inconsistency in the codebase.
**Fix:** Add a note to the module docstring clarifying this is intentional. Optionally add a `to_patterns()` method that converts dicts to Pydantic models.

### Q3. `caching.py` and `performance.py` have duplicate `CacheEntry` / `cached` definitions
Both modules define `CacheEntry` and `cached` with different signatures. The `caching.py` versions are dead code (nobody imports `cached` from caching.py).
**Fix:** Either remove the dead `cached` from caching.py or document that it's a standalone alternative.

### Q4. `framework.py` `_calculate_metrics_internal` batches are pointless
Lines 648-658: "batch processing" slices `self._relationships.values()` into chunks of 1000, but `list()` materializes the entire dict_values first, then slices. No memory benefit.
**Fix:** Remove the batch slicing; iterate directly.

### Q5. `framework.py` `get_performance_stats` index stats only checks one dimension
Line 583: `sum(len(ids) for ids in self._relationship_index.get('property', {}).values())` — only counts property index, not all dimensions.
**Fix:** Sum across all dimensions.

### Q6. `orchestration.py` `WorkflowEngine.compose_orchestrators` mutates original step dependencies
Line 378: `step.dependencies.append(...)` — mutates the original orchestrator's step objects, not copies.
**Fix:** Deep-copy steps before modifying.

### Q7. `validation.py` `validate_dimension` doesn't use registered rules
The method `_validate_element` does its own hardcoded checks instead of running rules from `self.rules`.
**Fix:** Align with `validate_framework` — iterate applicable rules.

### Q8. `composition.py` `overlay_frameworks` doesn't handle `framework.copy()` failing
If the framework object's `copy()` method fails or returns a shallow copy, the original gets mutated.
**Fix:** Add a try/except around `framework.copy()` and document the requirement.

### Q9. `storage.py` `SQLiteStorage` doesn't close connection on error
The `__del__` method closes the connection, but if an exception occurs during initialization, the connection leaks.
**Fix:** Use a context manager or try/finally in `_initialize_schema`.

### Q10. `website/routes/api.py` is 928 lines in a single file
The API routes file is very large and handles all endpoints.
**Fix:** Consider splitting into `api/patterns.py`, `api/relationships.py`, `api/domains.py`, etc.

---

## MINOR — Polish & Documentation

### P1. `AGENTS.md` is 16K+ and references outdated patterns
The AGENTS.md file still shows `pip install -e .` and old script names. It's very long and could be condensed.
**Fix:** Update install command and script references; condense redundant sections.

### P2. `CONTRIBUTING.md` stale script references
Lines 365-368 reference nonexistent validation scripts.
**Fix:** Replace with `scripts/validate_system.py`.

### P3. `docs/guides/installation.md` references `python setup.py install`
Line 88 — outdated installation method.
**Fix:** Replace with `pip install -e ".[dev,web]"`.

### P4. `MANIFEST.in` may be unnecessary
With `pyproject.toml` using `setuptools` and `package-data`, `MANIFEST.in` may be redundant.
**Fix:** Verify and potentially remove.

### P5. `.github/` directory — check for stale CI config
Need to verify `.github/workflows/` references current scripts.
**Fix:** Update CI to use `scripts/run_all.py` instead of `scripts/run_tests.py`.

### P6. `pytest.ini` and `pyproject.toml` both define pytest config
`pyproject.toml` has `[tool.pytest.ini_options]` and `pytest.ini` exists — pytest warns about the conflict.
**Fix:** Remove `[tool.pytest.ini_options]` from pyproject.toml (keep pytest.ini as the single source).

### P7. `interactive_terminal.sh` — verify all menu options reference existing scripts
**Fix:** Audit and update any stale references.

### P8. `examples/__init__.py` and `examples/README.md` are nearly empty
**Fix:** Add actual usage examples or document where examples live (in `orchestrators/`).

### P9. `data/domains/index.json` — verify all referenced domain files exist
**Fix:** Cross-reference index entries with actual files in `data/domains/`.

### P10. `outputs/` directory has tracked test output files
Git-tracked output files from previous runs should probably be gitignored.
**Fix:** Add `outputs/` to .gitignore (already done) and `git rm --cached` tracked files.

### P11. `website/templates/` — verify all template files exist and render
**Fix:** Run the Flask app and verify all routes return 200.

### P12. Add `__repr__` to `P3IFCore`, `ThinOrchestrator`, `CompositionEngine`
**Fix:** Add informative repr methods.

### P13. `framework.py` still has `import asyncio` but doesn't use it directly
Line 9: `import asyncio` — the framework doesn't use asyncio directly (the ThreadPoolExecutor is used instead).
**Fix:** Remove unused import.

### P14. `framework.py` has `import hashlib` and `from functools import lru_cache` but doesn't use them
Lines 16-17. Dead imports.
**Fix:** Remove.

### P15. `framework.py` has `import sys` and the `if __name__ == "__main__"` path manipulation
Lines 15, 22-24. This pattern is unnecessary in a package module.
**Fix:** Remove.

### P16. `core.py` has `import asyncio` but doesn't use it
Line 9. Dead import.
**Fix:** Remove.

---

## Architecture & Design Notes (Future)

### A1. Consider splitting `framework.py` (1131 lines) into smaller modules
Potential split: `framework/core.py` (init, repr, len, iter), `framework/patterns.py` (CRUD), `framework/relationships.py` (CRUD), `framework/metrics.py` (metrics + validation), `framework/io.py` (import/export), `framework/composition.py` (multiplex, hot_swap).

### A2. Consider adding async versions of add_pattern/add_relationship
The framework is fully synchronous. For I/O-bound storage backends, async methods would help.

### A3. Consider adding a `FrameworkBuilder` fluent API
`P3IFFramework().add_pattern(...).add_pattern(...).add_relationship(...)` pattern.

### A4. Consider typed domain data validation
Domain JSON files are loaded without schema validation. A Pydantic model for domain data would catch malformed files.

### A5. Consider adding `__eq__` to `BasePattern` and `Relationship`
Currently comparison is by identity (Pydantic default). Adding `__eq__` by name+domain+type would be useful for deduplication.
