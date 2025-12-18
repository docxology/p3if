"""
P3IF Core Framework

This module provides the foundational components for the P3IF framework.
"""

from .core import P3IFCore
from .framework import P3IFFramework
from .models import (
    BasePattern, Property, Process, Perspective, Relationship,
    PatternType, PatternCollection
)
from .orchestration import ThinOrchestrator, OrchestrationStep, OrchestratorType
from .composition import CompositionEngine, FrameworkAdapter
from .validation import ValidationEngine, ValidationRule
from .caching import CacheManager, CacheStrategy

__all__ = [
    'P3IFCore', 'P3IFFramework',
    'BasePattern', 'Property', 'Process', 'Perspective', 'Relationship',
    'PatternType', 'PatternCollection',
    'ThinOrchestrator', 'OrchestrationStep', 'OrchestratorType',
    'CompositionEngine', 'FrameworkAdapter',
    'ValidationEngine', 'ValidationRule',
    'CacheManager', 'CacheStrategy'
]





