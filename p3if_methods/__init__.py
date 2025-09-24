"""
P3IF Modular Methods Package

This package provides the core modular methods for P3IF framework operations,
organized by functionality for maximum composability and flexibility.
"""

# Import core components with error handling
try:
    from p3if_methods.core import P3IFCore, P3IFOperation
    from p3if_methods.composition import CompositionEngine, Multiplexer, AdapterFactory
    from p3if_methods.dimensions import PropertyManager, ProcessManager, PerspectiveManager
    from p3if_methods.orchestration import ThinOrchestrator, WorkflowEngine
    from p3if_methods.validation import ValidationEngine, ConstraintManager
    from p3if_methods.caching import CacheManager, PerformanceOptimizer
    from p3if_methods.models import Property, Process, Perspective, Relationship, BasePattern
    from p3if_methods.framework import P3IFFramework
    from p3if_methods import analysis
except ImportError as e:
    # Some modules may not be available during initialization
    import warnings
    warnings.warn(f"Some p3if_methods modules could not be imported: {e}")

__all__ = [
    'P3IFCore', 'P3IFOperation',
    'CompositionEngine', 'Multiplexer', 'AdapterFactory',
    'PropertyManager', 'ProcessManager', 'PerspectiveManager',
    'ThinOrchestrator', 'WorkflowEngine',
    'ValidationEngine', 'ConstraintManager',
    'CacheManager', 'PerformanceOptimizer',
    'Property', 'Process', 'Perspective', 'Relationship', 'BasePattern',
    'P3IFFramework',
    'analysis'
]
