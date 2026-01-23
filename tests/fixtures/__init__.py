"""
Test fixtures package for P3IF tests.

Provides helper functions and pytest fixtures for creating test data.
"""
from tests.fixtures.helpers import (
    create_test_framework,
    create_multi_domain_test_framework,
    create_large_test_framework,
    create_pattern_with_metadata,
    create_relationship_with_metadata,
    create_test_patterns_with_relationships,
    assert_framework_integrity,
    generate_test_json_data,
    # Pytest fixtures
    empty_framework,
    small_framework,
    medium_framework,
    large_framework,
    multi_domain_framework,
)

__all__ = [
    "create_test_framework",
    "create_multi_domain_test_framework",
    "create_large_test_framework",
    "create_pattern_with_metadata",
    "create_relationship_with_metadata",
    "create_test_patterns_with_relationships",
    "assert_framework_integrity",
    "generate_test_json_data",
    "empty_framework",
    "small_framework",
    "medium_framework",
    "large_framework",
    "multi_domain_framework",
]
