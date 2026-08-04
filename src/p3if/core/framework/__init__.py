"""
P3IF Core Framework

The framework package exposes :class:`P3IFFramework` and its supporting
components. The monolith was split into focused modules to improve
navigability and maintainability:

- ``core``: the :class:`P3IFFramework` class (patterns, relationships,
  metrics, import/export, hot-swapping, multiplexing).
- ``metrics``: the :class:`FrameworkMetrics` data structure.
- ``builder``: the fluent :class:`FrameworkBuilder` API.
"""
from .core import P3IFFramework
from .metrics import FrameworkMetrics
from .builder import FrameworkBuilder

__all__ = ["P3IFFramework", "FrameworkMetrics", "FrameworkBuilder"]
