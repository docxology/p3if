"""
P3IF Framework Metrics

Data structures for framework performance and usage metrics. Extracted from
the framework module to keep ``framework/core.py`` focused on the core
framework class.
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class FrameworkMetrics:
    """Framework performance and usage metrics."""

    total_patterns: int
    total_relationships: int
    average_relationship_strength: float
    average_confidence: float
    domain_count: int
    pattern_types_count: Dict[str, int]
    relationship_types_count: Dict[str, int]
    orphaned_patterns: int
    deprecated_patterns: int
    validation_issues: int
