"""
P3IF: Properties, Processes, and Perspectives Inter-Framework

A sophisticated meta-framework for integrating, analyzing, and visualizing
complex data relationships across multiple domains.
"""

__version__ = "2.5.0"

from .core import (
    P3IFFramework, P3IFCore, FrameworkBuilder,
    BasePattern, Property, Process, Perspective, Relationship,
    PatternType, PatternCollection,
    ThinOrchestrator, OrchestrationStep, OrchestratorType,
    CompositionEngine, FrameworkAdapter,
    ValidationEngine, ValidationRule,
    CacheManager, CacheStrategy,
)
from .data import DomainManager, SyntheticDataGenerator, DomainData

__all__ = [
    'P3IFFramework', 'P3IFCore', 'FrameworkBuilder',
    'BasePattern', 'Property', 'Process', 'Perspective', 'Relationship',
    'PatternType', 'PatternCollection',
    'ThinOrchestrator', 'OrchestrationStep', 'OrchestratorType',
    'CompositionEngine', 'FrameworkAdapter',
    'ValidationEngine', 'ValidationRule',
    'CacheManager', 'CacheStrategy',
    'DomainManager', 'SyntheticDataGenerator', 'DomainData',
]
