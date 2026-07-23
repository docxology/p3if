# Changelog

All notable changes to P3IF are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.4.0] - 2026-07-22

### Summary

Architecture and operability release. Adds fluent FrameworkBuilder API,
model equality/hash support, typed domain data validation, `__repr__` on
all remaining core classes, type stubs for external packages, and 20 new tests.

### Added

- `FrameworkBuilder` fluent API for constructing frameworks with method chaining:
  `FrameworkBuilder().add_property(...).add_process(...).build()`
- `__eq__` and `__hash__` on `BasePattern` (by name+domain+type) and
  `Relationship` (by connected IDs + type). Enables set-based deduplication.
- `DomainData` Pydantic model for validating domain JSON files at load time.
  Validates structure, strips whitespace, rejects empty entries.
- `__repr__` on `ValidationEngine`, `CacheManager`, `DomainManager`.
- `types-requests` and `types-PyYAML` to dev dependencies.
- 20 new tests: FrameworkBuilder chaining, model equality, DomainData validation.

### Changed

- `MANIFEST.in` updated to include `CHANGELOG.md` and `py.typed`.
- `FrameworkBuilder` exported from top-level `p3if` package.
- `DomainData` exported from `p3if.data` and top-level `p3if`.
- Version 2.3.0 → 2.4.0.

### Tests

361 passed, 4 skipped, 0 failures, 0 deprecation warnings.

## [2.3.0] - 2026-07-22

### Summary

Typing and operability release. Achieves zero mypy errors on core modules
(models, framework, core). Fixes all type annotations, removes dead code,
and improves framework operability with proper `__repr__`, `Optional` params,
and correct `PatternCollection` typing.

### Fixed — Type Annotations (models.py)

- `RelationshipStrength.__get_pydantic_core_schema__`: Added `-> Any` return type,
  `source_type: Any`, `handler: Any` params, inner `validate_strength(v: Any) -> float`.
- `ConfidenceScore.__get_pydantic_core_schema__`: Same annotations.
- `MetadataMixin`: Added class-level `metadata: Dict[str, Any]` and `updated_at: datetime`
  field declarations so mypy can resolve attribute access.
- `PatternCollection.all_patterns()`: Fixed `list[Process|Property] + list[Perspective]`
  type error by using `extend()` into a typed `List[BasePattern]`.
- All `@field_validator` methods: Added `-> str` return types and `: str` param types.
- `add_tag()`: Removed redundant local `logger` creation (already wrapped by `@logged_method()`).

### Fixed — Type Annotations (framework.py)

- `@cached` decorator: Added `# type: ignore[arg-type]` (decorator has dual-mode
  signature that mypy can't resolve).
- `_calculate_metrics_internal`: `pattern_types_count: Counter`, `strengths: List[float]`,
  `confidences: List[float]`, `relationship_types_count: Counter`.
- `get_performance_stats`: `domain_stats: Dict[str, int]`, `all_tags: Counter`.
- `import_from_json`: Added `pattern: BasePattern` annotation before conditional assignment.
- `multiplex_frameworks`: Fixed return type from `Dict[str, int]` to `Dict[str, Dict[str, int]]`.
- `custom_serializer`: Added `obj: Any -> Any` annotation.
- `__del__`: Added `-> None` return type.

### Fixed — Type Annotations (core.py)

- `P3IFCore.__init__`: Added `-> None` return type.
- `create_pattern`: Changed `domain: str = None` to `domain: Optional[str] = None`,
  `description: str = None` to `Optional[str]`, `**attributes` to `**attributes: Any`.
- `create_pattern`: Added `pattern: BasePattern` annotation before conditional assignment.
- `analyze_patterns`: Changed `domain: str = None` to `Optional[str] = None`.
  Added `analysis: Dict[str, Any]` annotation.
- `export_framework`: Fixed return type with explicit `str` cast.
- `create_relationship`: Cast `strength`/`confidence` to `RelationshipStrength`/`ConfidenceScore`.

### Fixed — Configuration

- `mypy.ini`: Updated `python_version` from 3.9 to 3.12 (matches actual runtime).

### Verification

- `mypy src/p3if/core/models.py src/p3if/core/framework.py src/p3if/core/core.py` — **0 errors**
- 341 tests pass, 3 skipped, 0 failures
- 42 visualization tests pass, 4 deselected (slow)
- 0 deprecation warnings

## [2.2.0] - 2026-07-22

### Summary

Quality and correctness release. Fixes all remaining TODO items from the v2.1.0 audit.
Improves Flask security, removes pointless batch slicing, fixes mutation bugs in
orchestration, aligns validation rule usage, adds `__repr__` to 3 more classes,
updates CI config, and untracks 61 output artifacts from git.

### Fixed — Code Quality

- `report.py`: Hardcoded `[:5]` and `[:3]` magic numbers replaced with
  `top_n_nodes` and `top_n_communities` parameters on `get_network_summary()`.
- `framework.py`: Removed pointless batch slicing in `_calculate_metrics_internal`
  — `list(dict.values())[i:i+batch_size]` materialized the entire collection first.
- `framework.py`: `get_performance_stats` only counted the 'property' dimension
  in relationship index size. Fixed to sum across all dimensions.
- `orchestration.py`: `WorkflowEngine.compose_orchestrators` mutated original
  orchestrator step dependencies. Now deep-copies steps before modifying.
- `validation.py`: `_validate_element` did its own hardcoded checks instead of
  using registered rules. Now iterates applicable rules, with fallback to basic
  checks when no rules are registered.
- `composition.py`: `overlay_frameworks` didn't handle `framework.copy()` failing.
  Added try/except with clear error message.
- `storage.py`: `SQLiteStorage.__init__` didn't close the connection on schema
  initialization failure. Added try/except to close on error.
- `website/app.py`: Hardcoded Flask secret key replaced with environment variable
  check + warning when not set in production.
- `framework_integration.py`: `_resolve_conflicts` accessed `conflicts["element_conflicts"]`
  without `.get()`. Fixed to use `.get("element_conflicts", {})`.
- `integration_examples.py`: `strategy="union"` string replaced with
  `MultiplexingStrategy.UNION` enum.
- `integration_examples.py`: Class-level `logger` attribute (shared mutable) moved
  to `__post_init__` instance attribute.
- `cognitive_security.py`: Duplicate module docstring removed.

### Fixed — Documentation

- AGENTS.md: Updated install command, script references, removed 3.8 references.
- `.github/workflows/ci.yml`: Python matrix updated from '3.8' to '3.9'.
- `docs/guides/installation.md`: `python setup.py install` → `pip install -e ".[dev,web]"`.
- `website/app.py`, `website/run.py`: Removed stale `setup.py` from exclude_patterns.
- `examples/README.md`: Added content pointing to actual example locations.
- `dimensions.py`: Added docstring note explaining plain-dict design is intentional.
- `caching.py`: Added docstring note explaining dual cached decorators.

### Added

- `__repr__` on `P3IFCore`, `ThinOrchestrator`, `CompositionEngine`.
- `TODO.md` with 40+ scoped improvements (MAJOR/MEDIUM/MINOR/Architecture).

### Changed

- Untracked 61 output artifacts from git (`git rm --cached -r outputs/`).
- Version 2.1.0 → 2.2.0.

### Tests

341 passed, 3 skipped, 0 failures, 0 deprecation warnings.

## [2.1.0] - 2026-07-22

### Summary

Comprehensive bug-fix and improvement release. Fixes 30+ bugs across thread safety,
Pydantic v2 migration, Python 3.12 compatibility, logic errors, and documentation.
Adds 24 new tests, new API methods, `__repr__` support, and expanded public API exports.

### Fixed — Thread Safety

- `P3IFFramework.add_pattern()` and `add_relationship()` released the RLock before
  writing to internal dicts, allowing race conditions. All mutations now happen
  inside the lock block.
- `add_patterns_batch()` / `add_relationships_batch()` acquired the lock then called
  `add_pattern()` which re-acquires it (RLock allows this but the outer lock was
  pointless). Removed the redundant outer lock.
- `multiplex_frameworks()` exited the `with self._lock` block before entering the
  loop body, and returned inside the loop (only first dimension processed). Fixed
  to run entirely inside the lock and return after the loop.
- `validate_framework()` defined variables inside `with self._lock` but returned
  outside the block, causing `NameError`. Moved return inside the lock.

### Fixed — Pydantic v2 Migration

- Replaced all deprecated `.dict()` calls with `.model_dump()` across 8 source
  files and 1 test file.
- Replaced `.json()` with `.model_dump_json()` in models.
- Replaced `class Config` with `model_config = {...}` dict in `BasePattern` and
  `Relationship`.
- Removed deprecated `validator` and `root_validator` imports.
- Split `Perspective.validate_scope_level` (single validator for two fields with
  different valid values) into separate `validate_scope` and `validate_expertise_level`.
- Updated `P3IFEncoder` to check `model_dump` before `dict`.

### Fixed — Python 3.12 Compatibility

- `async_performance_timer` used `asyncio.coroutine()` (removed in 3.12). Replaced
  with `yield` for proper async context manager.
- `ThinOrchestrator.execute_sync()` used deprecated `asyncio.get_event_loop()`.
  Replaced with `asyncio.get_running_loop()` / `asyncio.run()`.
- `_execute_step_async()` used deprecated `asyncio.get_event_loop()`. Replaced
  with `asyncio.get_running_loop()`.
- `logging.py` imported `functools` at the bottom of the file after decorators
  used it. Moved import to top.

### Fixed — Logic Bugs

- `_calculate_metrics_internal` extracted pattern type by splitting UUID by
  underscore, producing garbage. Fixed to use the dict key directly.
- `get_relationships_by_pattern` returned duplicate relationships (same rel in
  multiple dimension indexes). Added set-based deduplication.
- `multiplex_frameworks` used plural dict keys ("properties") but accessed with
  singular dimension variable ("property"), causing `KeyError`. Fixed to use
  singular keys.
- `create_relationship` stored `relationship_type` in metadata instead of the
  field. Fixed to pass as proper field.
- `import_from_json` called `Path(json_str).exists()` on long JSON strings,
  causing `OSError`. Fixed to check if string starts with `{` or `[` first.
- `overlay_frameworks` used set operations on lists, causing `TypeError`. Fixed
  to convert to sets and preserve original container type.
- `hot_swap_dimension` used `hasattr(str, 'type')` which returns True, causing
  `AttributeError`. Added `isinstance` guard.
- `_execute_step_async` introspected `__code__` three times redundantly.
  Consolidated to a single introspection.
- `log_method_result` had unreachable `elif` branch (>5.0 checked after >1.0).
  Restructured to check >5.0 first.
- `SQLiteStorage.save_pattern` stored enum object instead of its string value.
  Added `.value` extraction.
- `StorageInterface` used undefined `Pattern` type in abstract methods. Changed
  to `BasePattern` with `TYPE_CHECKING` import.
- `domains.py` missing imports for `Property`, `Process`, `Perspective`,
  `Relationship` in `import_domain` and `merge_domains`.
- `merge_domains` didn't pass `viewpoint` when constructing `Perspective`.
- `core.py` `_validate_pattern` compared `pattern.type` with strings instead of
  `PatternType` enum values.
- `performance_monitoring.py` had bare `import psutil` without try/except guard.
- `benchmark_performance.py` had bare `import psutil` without try/except guard.
- `_validate_pattern` category validation restricted to 5 hardcoded categories
  not matching the `Property` model's `category` field (which is `Optional[str]`).

### Fixed — Documentation

- README title corrected from "Patterns" to "Properties, Processes, and Perspectives".
- README clone URL changed from `yourusername` to `danielmiessler`.
- README install command updated to `pip install -e ".[dev,web]"`.
- Removed references to nonexistent scripts: `run_tests.py`,
  `run_complete_p3if_pipeline.py`, `run_multidomain_portal.py`,
  `validate_documentation.py`.
- Fixed broken markdown where directory tree was outside code fences.
- Removed references to nonexistent files: `setup.py`, `PACKAGE_README.md`.
- `docs/README.md` Python badge updated from 3.8+ to 3.9+.
- `docs/README.md` clone URL fixed.
- `.cursorrules` script example updated to existing script.
- `CLAUDE.md` install command updated.
- `.gitignore` added `outputs/` directory.

### Added

- `P3IFFramework.get_all_patterns()` — returns list of all patterns.
- `P3IFFramework.get_all_domains()` — returns set of all domain names.
- `__repr__` methods on `P3IFFramework`, `BasePattern`, `Relationship`.
- `ValidationRule.applies_to` field — replaces brittle rule-name-prefix matching
  with explicit target type ('pattern', 'relationship', 'framework').
- `py.typed` marker file for PEP 561 type information.
- Expanded top-level `__init__.py` exports: `BasePattern`, `PatternType`,
  `PatternCollection`, `ThinOrchestrator`, `OrchestrationStep`,
  `OrchestratorType`, `CompositionEngine`, `FrameworkAdapter`,
  `ValidationEngine`, `ValidationRule`, `CacheManager`, `CacheStrategy`,
  `DomainManager`, `SyntheticDataGenerator`.
- `markdown` added to `web` optional dependencies.
- `networkx` added to `requirements.txt`.
- `pytest-asyncio` added to `requirements.txt`.
- 24 new comprehensive tests in `test_comprehensive_fixes.py`.

### Changed

- Python version floor raised from 3.8 to 3.9 (code uses `list[str]` type hints).
- `requires-python` updated in `pyproject.toml`.
- mypy, black, and ruff `target-version` updated from `py38` to `py39`.
- Python classifiers updated (removed 3.8, added 3.13).
- `requirements.txt` synchronized with `pyproject.toml`.
- `flask` minimum version bumped from 2.3.0 to 3.0.0 in `requirements.txt`.
- `.dict()` → `.model_dump()` in `website/routes/api.py` (8 occurrences).

## [2.0.0] - 2024-01-15

Initial modular architecture release with `src/` layout, Pydantic v2 models,
thin orchestrators, visualization system, and web portal.
