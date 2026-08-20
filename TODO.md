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
