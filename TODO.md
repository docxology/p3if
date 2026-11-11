# P3IF TODO — Upcoming Improvements

Items completed in v2.1.0–v2.5.0 are listed in CHANGELOG.md.

---

## Completed in v2.5.0
- **A1**: Split `core/framework.py` into modular package `core/framework/` (`core.py`, `metrics.py`, `builder.py`, `__init__.py`) — DONE
- **Q13 (Core)**: Type annotations across all `p3if.core.*` modules verified and mypy-clean — DONE
- **Q11**: Comprehensive tests for analysis modules — DONE
- **Q12**: Tests for thin orchestrators — DONE

---

## Active & Upcoming Roadmap

### Minor — Polish & Typing
- [x] **P11**: Verify all website template routes return 200 (fix broken `url_for` blueprint endpoint names, e.g. `docs_bp`, `domains_bp`, `viz_bp`, `home` -> `index`).
- [x] **Q14**: Clean up type annotations across visualization, data, utils, and orchestrator modules to pass repo-wide `mypy src`.

### Medium — Quality & Modularity
- [x] **Q10**: Split `website/routes/api.py` into modular submodules under `website/routes/api/` (`health.py`, `domains.py`, `framework.py`, `patterns.py`, `relationships.py`, `analysis.py`, `visualizations.py`, `export.py`, `spec.py`) while retaining re-export compatibility.
- [x] **A2**: Add async storage and framework methods (`save_pattern_async`, `get_pattern_async`, `save_relationship_async`, `add_pattern_async`, `add_relationship_async`) for non-blocking I/O backends.

### Major — Advanced Capabilities & High Performance
- [x] **M1**: Advanced 3D pattern visualization engine (`p3if.visualization.interactive.interactive_3d`) with full dimension projection, cluster visualization, cross-domain relationship overlays, and WebGL/Plotly export.
- [x] **M2**: High-performance Compositional Indexing Engine (`p3if.core.indexing`) supporting multi-attribute inverted indices, fast subset queries, intersection/union operations, and benchmarked sub-millisecond retrieval.
- [x] **M3**: Comprehensive end-to-end framework test suite covering async storage, compositional indexing, 3D visualization, and full website template route coverage without mocks.

## Workflowz review — 2026-11-10

- [ ] **WF-01 (P2): Make the visualization test runner return a failing process status when loading a configured test selector raises.** `tests/visualization/run_all_tests.py:67-73` catches discovery/load exceptions for the base selector and only logs them; the portal, network, and matrix branches repeat this behavior at lines 77-83, 87-93, and 97-103, so an executed script can lose an entire configured test group without a load failure reaching its process outcome. Record discovery exceptions as suite failures and make successful exit conditional on both loading and running all selected groups; preserve the existing logger diagnostics. Observable outcome: the command is nonzero when any selected test module cannot be imported or loaded, instead of continuing to a successful result, while an ordinary passing run remains zero.
  - **Acceptance probe (from repository root):** using Python 3.15.2 (or another supported interpreter if its scientific dependencies require one), first establish a control with `PYTHONPATH=src python tests/visualization/run_all_tests.py` in the intended test environment and record its selected groups and status. Then create an importable temporary directory on `PYTHONPATH` shadowing a module imported by one configured selector with a module whose import raises `RuntimeError("WF01 import sentinel")`; rerun the same command and require nonzero status plus the sentinel in stderr. Run a same-shadowed-module control directly through `python -m unittest` to confirm the injected module is the one being loaded. Finally remove the shadow and verify the original runner's control status is restored. Use unique temporary files outside the repository and do not edit fixtures. This exercises actual discovery/import and process status, not source text. If runner arguments are needed to select a deterministic group, choose the visible CLI option corresponding to `test_base.py` at lines 67-70.
  - **Dependencies/constraints:** Python plus the visualization test dependencies in `tests/visualization/requirements-test.txt`; preserve `unittest` discovery semantics and existing logging. This does not assume every absent historical selector is a defect by itself—the actionable contract is that an exception while loading an actually selected group must affect the exit status. Complete the acceptance probe before claiming behavior on a specific dependency set.
