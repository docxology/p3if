"""
Shared P3IF fixture/data builders.

This module provides reusable builders for constructing P3IF frameworks and
patterns with realistic metadata. It is the canonical, importable home for
these builders; tests/fixtures/helpers.py re-exports them for backward
compatibility (2026-09 audit: production tooling must not import the test
fixture package).

Usage:
    from p3if.utils.fixtures import create_test_patterns_with_relationships

    framework = create_test_patterns_with_relationships(
        num_patterns=5, num_relationships=10
    )
"""
import random
import uuid
from typing import Any, List, Optional
from datetime import datetime, timezone

from p3if.core.framework import P3IFFramework
from p3if.core.models import Property, Process, Perspective, Relationship


def create_pattern_with_metadata(
    pattern_type: str = "property",
    name: Optional[str] = None,
    domain: str = "test",
    tags: Optional[List[str]] = None,
    quality_score: float = 0.8,
    confidence: float = 0.9,
) -> Any:
    """
    Create a pattern with comprehensive metadata for testing.

    Args:
        pattern_type: Type of pattern to create ('property', 'process', 'perspective')
        name: Name for the pattern (auto-generated if None)
        domain: Domain for the pattern
        tags: Tags for the pattern
        quality_score: Quality score for the pattern
        confidence: Confidence score for the pattern

    Returns:
        Pattern instance with metadata
    """
    if name is None:
        name = f"Test {pattern_type.title()} {uuid.uuid4().hex[:8]}"

    if tags is None:
        tags = ["test", pattern_type, "metadata-test"]

    pattern_classes = {"property": Property, "process": Process, "perspective": Perspective}

    pattern_class = pattern_classes.get(pattern_type.lower())
    if not pattern_class:
        raise ValueError(f"Unknown pattern type: {pattern_type}")

    # Create base pattern data
    pattern_data = {
        "name": name,
        "description": f"Test {pattern_type} with metadata",
        "domain": domain,
        "tags": tags,
        "quality_score": quality_score,
        "confidence": confidence,
        "version": "1.0.0",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    # Add pattern-specific fields
    if pattern_type.lower() == "perspective":
        pattern_data["viewpoint"] = "Test viewpoint"

    return pattern_class(**pattern_data)


def create_test_patterns_with_relationships(
    num_patterns: int = 10, num_relationships: int = 25
) -> P3IFFramework:
    """
    Create test patterns and relationships with realistic metadata.

    Args:
        num_patterns: Number of patterns to create per type
        num_relationships: Number of relationships to create

    Returns:
        P3IFFramework instance with test data
    """
    framework = P3IFFramework()

    # Create properties
    properties = []
    for i in range(num_patterns):
        prop = create_pattern_with_metadata(
            pattern_type="property",
            name=f"TestProperty{i:03d}",
            domain=f"Domain{i % 3 + 1}",
            quality_score=0.7 + random.random() * 0.3,
        )
        properties.append(prop)
        framework.add_pattern(prop)

    # Create processes
    processes = []
    for i in range(num_patterns):
        proc = create_pattern_with_metadata(
            pattern_type="process",
            name=f"TestProcess{i:03d}",
            domain=f"Domain{i % 3 + 1}",
            quality_score=0.7 + random.random() * 0.3,
        )
        processes.append(proc)
        framework.add_pattern(proc)

    # Create perspectives
    perspectives = []
    for i in range(num_patterns):
        persp = create_pattern_with_metadata(
            pattern_type="perspective",
            name=f"TestPerspective{i:03d}",
            domain=f"Domain{i % 3 + 1}",
            quality_score=0.7 + random.random() * 0.3,
        )
        perspectives.append(persp)
        framework.add_pattern(persp)

    # Create relationships
    # Mapping for correct pluralization of pattern types
    pattern_lists = {"property": properties, "process": processes, "perspective": perspectives}

    for i in range(num_relationships):
        # Randomly select pattern types to connect
        pattern_types = random.sample(["property", "process", "perspective"], 2)
        type1, type2 = pattern_types

        # Randomly select patterns using the mapping
        pattern1 = random.choice(pattern_lists[type1])
        pattern2 = random.choice(pattern_lists[type2])

        # Create relationship data
        rel_data = {
            f"{type1}_id": pattern1.id,
            f"{type2}_id": pattern2.id,
            "strength": random.random(),
            "confidence": random.random(),
            "relationship_type": random.choice(
                ["correlation", "causation", "dependency", "influence"]
            ),
            "quality_score": 0.7 + random.random() * 0.3,
        }

        # Set third dimension to None
        third_type = next(
            t for t in ["property", "process", "perspective"] if t not in [type1, type2]
        )
        rel_data[f"{third_type}_id"] = None

        try:
            relationship = Relationship(**rel_data)
            framework.add_relationship(relationship)
        except ValueError:
            # Skip invalid relationships
            pass

    return framework
