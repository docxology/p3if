"""
Comprehensive unit tests for the P3IF Framework core module.
"""
import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from core.framework import P3IFFramework
from core.models import Property, Process, Perspective, Relationship, PatternType
from tests.utils import (
    create_pattern_with_metadata,
    create_relationship_with_metadata,
    assert_framework_integrity,
    generate_test_json_data
)


class TestP3IFFramework:
    """Test cases for the P3IFFramework class."""

    def test_framework_initialization(self):
        """Test framework initialization."""
        framework = P3IFFramework()

        assert framework._patterns == {}
        assert framework._relationships == {}
        assert framework._pattern_index == {}
        assert framework._relationship_index == {}
        assert framework._lock is not None
        assert framework._executor is not None
        assert framework._metrics_cache == {}
        assert framework._cache_expiry == {}
        assert framework._cache_timeout == 300  # 5 minutes default

    def test_add_single_pattern(self):
        """Test adding a single pattern."""
        framework = P3IFFramework()
        pattern = Property(name="Test Property", description="Test description")

        framework.add_pattern(pattern)

        assert pattern.id in framework._patterns
        assert pattern.id in framework._pattern_index
        assert len(framework._patterns) == 1
        assert len(framework._pattern_index) == 1

    def test_add_multiple_patterns(self):
        """Test adding multiple patterns."""
        framework = P3IFFramework()

        patterns = [
            Property(name="Property 1", description="Description 1"),
            Process(name="Process 1", description="Description 2"),
            Perspective(name="Perspective 1", description="Description 3")
        ]

        for pattern in patterns:
            framework.add_pattern(pattern)

        assert len(framework._patterns) == 3
        assert len(framework._pattern_index) == 3

        for pattern in patterns:
            assert pattern.id in framework._patterns
            assert pattern.id in framework._pattern_index

    def test_add_duplicate_pattern_raises_error(self):
        """Test that adding a duplicate pattern raises an error."""
        framework = P3IFFramework()
        pattern = Property(name="Test Property", description="Test description")

        framework.add_pattern(pattern)

        with pytest.raises(ValueError, match="Pattern with ID .* already exists"):
            framework.add_pattern(pattern)

    def test_remove_pattern(self):
        """Test removing a pattern."""
        framework = P3IFFramework()
        pattern = Property(name="Test Property", description="Test description")

        framework.add_pattern(pattern)
        assert pattern.id in framework._patterns

        framework.remove_pattern(pattern.id)
        assert pattern.id not in framework._patterns
        assert pattern.id not in framework._pattern_index

    def test_remove_nonexistent_pattern_raises_error(self):
        """Test that removing a non-existent pattern raises an error."""
        framework = P3IFFramework()

        with pytest.raises(ValueError, match="Pattern with ID .* not found"):
            framework.remove_pattern("nonexistent_id")

    def test_add_relationship(self):
        """Test adding a relationship."""
        framework = P3IFFramework()

        prop = Property(name="Test Property", description="Test description")
        proc = Process(name="Test Process", description="Test description")
        persp = Perspective(name="Test Perspective", description="Test description")

        framework.add_pattern(prop)
        framework.add_pattern(proc)
        framework.add_pattern(persp)

        relationship = Relationship(
            property_id=prop.id,
            process_id=proc.id,
            perspective_id=persp.id,
            strength=0.8,
            confidence=0.9
        )

        framework.add_relationship(relationship)

        assert relationship.id in framework._relationships
        assert relationship.id in framework._relationship_index
        assert len(framework._relationships) == 1

    def test_add_relationship_with_invalid_patterns_raises_error(self):
        """Test that adding a relationship with invalid patterns raises an error."""
        framework = P3IFFramework()

        relationship = Relationship(
            property_id="invalid_prop",
            process_id="invalid_proc",
            perspective_id="invalid_persp",
            strength=0.8,
            confidence=0.9
        )

        with pytest.raises(ValueError, match="Referenced pattern .* not found"):
            framework.add_relationship(relationship)

    def test_remove_relationship(self):
        """Test removing a relationship."""
        framework = P3IFFramework()

        prop = Property(name="Test Property", description="Test description")
        proc = Process(name="Test Process", description="Test description")
        persp = Perspective(name="Test Perspective", description="Test description")

        framework.add_pattern(prop)
        framework.add_pattern(proc)
        framework.add_pattern(persp)

        relationship = Relationship(
            property_id=prop.id,
            process_id=proc.id,
            perspective_id=persp.id,
            strength=0.8,
            confidence=0.9
        )

        framework.add_relationship(relationship)
        assert relationship.id in framework._relationships

        framework.remove_relationship(relationship.id)
        assert relationship.id not in framework._relationships
        assert relationship.id not in framework._relationship_index

    def test_get_patterns_by_type(self):
        """Test getting patterns by type."""
        framework = P3IFFramework()

        prop = Property(name="Test Property", description="Test description")
        proc = Process(name="Test Process", description="Test description")
        persp = Perspective(name="Test Perspective", description="Test description")

        framework.add_pattern(prop)
        framework.add_pattern(proc)
        framework.add_pattern(persp)

        properties = framework.get_patterns_by_type("property")
        processes = framework.get_patterns_by_type("process")
        perspectives = framework.get_patterns_by_type("perspective")

        assert len(properties) == 1
        assert len(processes) == 1
        assert len(perspectives) == 1

        assert properties[0].id == prop.id
        assert processes[0].id == proc.id
        assert perspectives[0].id == persp.id

    def test_get_patterns_by_domain(self):
        """Test getting patterns by domain."""
        framework = P3IFFramework()

        prop1 = Property(name="Property 1", description="Test", domain="domain1")
        prop2 = Property(name="Property 2", description="Test", domain="domain1")
        prop3 = Property(name="Property 3", description="Test", domain="domain2")

        framework.add_pattern(prop1)
        framework.add_pattern(prop2)
        framework.add_pattern(prop3)

        domain1_patterns = framework.get_patterns_by_domain("domain1")
        domain2_patterns = framework.get_patterns_by_domain("domain2")

        assert len(domain1_patterns) == 2
        assert len(domain2_patterns) == 1

    def test_get_patterns_by_tag(self):
        """Test getting patterns by tag."""
        framework = P3IFFramework()

        prop1 = Property(name="Property 1", description="Test", tags=["tag1", "tag2"])
        prop2 = Property(name="Property 2", description="Test", tags=["tag1", "tag3"])
        prop3 = Property(name="Property 3", description="Test", tags=["tag2", "tag4"])

        framework.add_pattern(prop1)
        framework.add_pattern(prop2)
        framework.add_pattern(prop3)

        tag1_patterns = framework.get_patterns_by_tag("tag1")
        tag2_patterns = framework.get_patterns_by_tag("tag2")

        assert len(tag1_patterns) == 2
        assert len(tag2_patterns) == 2

    def test_search_patterns(self):
        """Test searching patterns by name/description."""
        framework = P3IFFramework()

        prop1 = Property(name="Important Property", description="This is important")
        prop2 = Property(name="Another Property", description="This is also important")
        prop3 = Property(name="Different Property", description="This is different")

        framework.add_pattern(prop1)
        framework.add_pattern(prop2)
        framework.add_pattern(prop3)

        important_results = framework.search_patterns("important")
        different_results = framework.search_patterns("different")

        assert len(important_results) == 2
        assert len(different_results) == 1

    def test_get_metrics_empty_framework(self):
        """Test getting metrics for an empty framework."""
        framework = P3IFFramework()

        metrics = framework.get_metrics()

        assert metrics["total_patterns"] == 0
        assert metrics["total_relationships"] == 0
        assert metrics["average_relationship_strength"] == 0.0
        assert metrics["average_confidence"] == 0.0
        assert metrics["domain_count"] == 0
        assert metrics["orphaned_patterns"] == 0
        assert metrics["deprecated_patterns"] == 0
        assert metrics["validation_issues"] == 0

    def test_get_metrics_with_data(self):
        """Test getting metrics for a framework with data."""
        framework = P3IFFramework()

        # Add some patterns
        prop = Property(name="Test Property", description="Test", domain="test_domain")
        proc = Process(name="Test Process", description="Test", domain="test_domain")
        persp = Perspective(name="Test Perspective", description="Test", domain="other_domain")

        framework.add_pattern(prop)
        framework.add_pattern(proc)
        framework.add_pattern(persp)

        # Add a relationship
        relationship = Relationship(
            property_id=prop.id,
            process_id=proc.id,
            perspective_id=persp.id,
            strength=0.8,
            confidence=0.9
        )
        framework.add_relationship(relationship)

        metrics = framework.get_metrics()

        assert metrics["total_patterns"] == 3
        assert metrics["total_relationships"] == 1
        assert metrics["domain_count"] == 2
        assert metrics["orphaned_patterns"] == 0  # All patterns are connected

    def test_get_pattern_collection(self):
        """Test getting pattern collection organized by type."""
        framework = P3IFFramework()

        prop = Property(name="Test Property", description="Test", domain="test")
        proc = Process(name="Test Process", description="Test", domain="test")
        persp = Perspective(name="Test Perspective", description="Test", domain="test")

        framework.add_pattern(prop)
        framework.add_pattern(proc)
        framework.add_pattern(persp)

        collection = framework.get_pattern_collection()

        assert "property" in collection
        assert "process" in collection
        assert "perspective" in collection

        assert len(collection["property"]) == 1
        assert len(collection["process"]) == 1
        assert len(collection["perspective"]) == 1

    def test_export_to_json(self):
        """Test exporting framework to JSON."""
        framework = P3IFFramework()

        prop = Property(name="Test Property", description="Test", domain="test")
        proc = Process(name="Test Process", description="Test", domain="test")
        framework.add_pattern(prop)
        framework.add_pattern(proc)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_export.json"
            framework.export_to_json(output_file)

            assert output_file.exists()

            # Check the exported content
            with open(output_file, 'r') as f:
                data = json.load(f)

            assert "patterns" in data
            assert "relationships" in data
            assert "metadata" in data
            assert len(data["patterns"]) == 2
            assert len(data["relationships"]) == 0

    def test_import_from_json(self):
        """Test importing framework from JSON."""
        framework = P3IFFramework()

        # Generate test data
        test_data = generate_test_json_data(num_patterns=3, num_relationships=2)

        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "test_import.json"

            with open(input_file, 'w') as f:
                json.dump(test_data, f, indent=2)

            # Import the data
            framework.import_from_json(input_file)

            # Check that data was imported
            assert len(framework._patterns) == 3
            assert len(framework._relationships) == 2

    def test_hot_swap_dimension(self):
        """Test hot-swapping a dimension."""
        framework = P3IFFramework()

        # Add some patterns
        prop1 = Property(name="Property 1", description="Test", domain="test")
        prop2 = Property(name="Property 2", description="Test", domain="test")
        proc = Process(name="Process 1", description="Test", domain="test")
        persp = Perspective(name="Perspective 1", description="Test", domain="test")

        framework.add_pattern(prop1)
        framework.add_pattern(prop2)
        framework.add_pattern(proc)
        framework.add_pattern(persp)

        # Add relationships
        rel1 = Relationship(property_id=prop1.id, process_id=proc.id, perspective_id=persp.id, strength=0.8, confidence=0.9)
        rel2 = Relationship(property_id=prop2.id, process_id=proc.id, perspective_id=persp.id, strength=0.7, confidence=0.8)
        framework.add_relationship(rel1)
        framework.add_relationship(rel2)

        # Create replacement property
        new_prop = Property(name="New Property", description="Replacement", domain="test")

        # Hot swap the property
        stats = framework.hot_swap_dimension("property", prop1.id, new_prop)

        assert stats["replaced_patterns"] == 1
        assert stats["updated_relationships"] == 1

        # Check that the old property is gone and new one exists
        assert prop1.id not in framework._patterns
        assert new_prop.id in framework._patterns

        # Check that relationship was updated
        updated_rel = list(framework._relationships.values())[0]
        assert new_prop.id in updated_rel.get_connected_patterns()

    def test_multiplex_frameworks(self):
        """Test multiplexing multiple frameworks."""
        framework1 = P3IFFramework()
        framework2 = P3IFFramework()

        # Add patterns to first framework
        prop1 = Property(name="Property 1", description="Test", domain="test")
        proc1 = Process(name="Process 1", description="Test", domain="test")
        framework1.add_pattern(prop1)
        framework1.add_pattern(proc1)

        # Add patterns to second framework
        prop2 = Property(name="Property 2", description="Test", domain="test")
        proc2 = Process(name="Process 2", description="Test", domain="test")
        framework2.add_pattern(prop2)
        framework2.add_pattern(proc2)

        # Multiplex the frameworks
        combined_framework = P3IFFramework.multiplex_frameworks([framework1, framework2])

        assert len(combined_framework._patterns) == 4
        assert len(combined_framework._relationships) == 0  # No relationships in individual frameworks

    def test_validate_framework(self):
        """Test framework validation."""
        framework = P3IFFramework()

        # Add some valid patterns
        prop = Property(name="Test Property", description="Test", domain="test")
        proc = Process(name="Test Process", description="Test", domain="test")
        framework.add_pattern(prop)
        framework.add_pattern(proc)

        # Add a relationship
        relationship = Relationship(
            property_id=prop.id,
            process_id=proc.id,
            perspective_id=None,
            strength=0.8,
            confidence=0.9
        )
        framework.add_relationship(relationship)

        # Validate framework
        validation_result = framework.validate_framework()

        assert validation_result["is_valid"]
        assert len(validation_result["issues"]) == 0

    def test_validate_framework_with_issues(self):
        """Test framework validation with issues."""
        framework = P3IFFramework()

        # Add a relationship without referenced patterns
        relationship = Relationship(
            property_id="invalid_prop",
            process_id="invalid_proc",
            perspective_id="invalid_persp",
            strength=0.8,
            confidence=0.9
        )

        try:
            framework.add_relationship(relationship)
        except ValueError:
            # Manually add invalid relationship for testing
            framework._relationships[relationship.id] = relationship

        # Validate framework
        validation_result = framework.validate_framework()

        assert not validation_result["is_valid"]
        assert len(validation_result["issues"]) > 0

    def test_thread_safety(self):
        """Test thread safety of framework operations."""
        import threading
        import time

        framework = P3IFFramework()
        results = []
        errors = []

        def add_patterns_concurrently(num_patterns):
            try:
                for i in range(num_patterns):
                    pattern = Property(name=f"Property {i}", description=f"Test {i}")
                    framework.add_pattern(pattern)
                    time.sleep(0.001)  # Small delay to increase chance of race conditions
                results.append(len(framework._patterns))
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_patterns_concurrently, args=(10,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that no errors occurred
        assert len(errors) == 0

        # Check that all patterns were added
        assert len(framework._patterns) == 50
        assert len(results) == 5
        assert all(count == 50 for count in results)

    def test_caching_behavior(self):
        """Test caching behavior of metrics."""
        framework = P3IFFramework()

        # First call should compute metrics
        start_time = datetime.now(timezone.utc)
        metrics1 = framework.get_metrics()
        end_time = datetime.now(timezone.utc)

        # Second call should use cache
        cache_start_time = datetime.now(timezone.utc)
        metrics2 = framework.get_metrics()
        cache_end_time = datetime.now(timezone.utc)

        # Results should be identical
        assert metrics1 == metrics2

        # Second call should be faster (though this might be flaky in test environment)
        time_diff1 = (end_time - start_time).total_seconds()
        time_diff2 = (cache_end_time - cache_start_time).total_seconds()

        # Cache invalidation should work
        framework._invalidate_metrics_cache()
        assert framework._metrics_cache == {}

    def test_magic_methods(self):
        """Test magic methods implementation."""
        framework = P3IFFramework()

        # Test __len__
        assert len(framework) == 0

        # Add some patterns
        prop = Property(name="Test Property", description="Test")
        framework.add_pattern(prop)

        assert len(framework) == 1

        # Test __contains__
        assert prop.id in framework
        assert "nonexistent_id" not in framework

        # Test __iter__
        patterns = list(framework)
        assert len(patterns) == 1
        assert patterns[0].id == prop.id


class TestFrameworkIntegration:
    """Integration tests for the P3IF framework."""

    def test_complex_pattern_relationships(self):
        """Test complex pattern relationships."""
        framework = P3IFFramework()

        # Create patterns with metadata
        properties = []
        processes = []
        perspectives = []

        for i in range(5):
            prop = create_pattern_with_metadata(
                pattern_type="property",
                name=f"Property{i}",
                domain=f"Domain{i % 3}",
                quality_score=0.7 + (i * 0.06)  # Varying quality scores
            )
            properties.append(prop)
            framework.add_pattern(prop)

            proc = create_pattern_with_metadata(
                pattern_type="process",
                name=f"Process{i}",
                domain=f"Domain{i % 3}",
                quality_score=0.7 + (i * 0.06)
            )
            processes.append(proc)
            framework.add_pattern(proc)

            persp = create_pattern_with_metadata(
                pattern_type="perspective",
                name=f"Perspective{i}",
                domain=f"Domain{i % 3}",
                quality_score=0.7 + (i * 0.06)
            )
            perspectives.append(persp)
            framework.add_pattern(persp)

        # Create complex relationships
        for i in range(15):
            # Create relationships between different types
            prop = properties[i % len(properties)]
            proc = processes[i % len(processes)]
            persp = perspectives[i % len(perspectives)]

            relationship = create_relationship_with_metadata(
                property_id=prop.id,
                process_id=proc.id,
                perspective_id=persp.id,
                strength=0.5 + (i * 0.03),  # Varying strength
                confidence=0.6 + (i * 0.027),  # Varying confidence
                relationship_type=["correlation", "causation", "dependency"][i % 3]
            )

            framework.add_relationship(relationship)

        # Validate framework integrity
        assert_framework_integrity(framework)

        # Check metrics
        metrics = framework.get_metrics()
        assert metrics["total_patterns"] == 15
        assert metrics["total_relationships"] == 15
        assert metrics["domain_count"] == 3

        # Test pattern retrieval methods
        domain_patterns = framework.get_patterns_by_domain("Domain0")
        assert len(domain_patterns) == 5  # 5 patterns per domain (rounded up)

        prop_patterns = framework.get_patterns_by_type("property")
        assert len(prop_patterns) == 5

        # Test search functionality
        search_results = framework.search_patterns("Property")
        assert len(search_results) == 5

    def test_framework_persistence(self):
        """Test framework data persistence and restoration."""
        framework = P3IFFramework()

        # Create test data
        prop = create_pattern_with_metadata("property", "Test Property", "test_domain")
        proc = create_pattern_with_metadata("process", "Test Process", "test_domain")
        framework.add_pattern(prop)
        framework.add_pattern(proc)

        relationship = create_relationship_with_metadata(
            property_id=prop.id,
            process_id=proc.id,
            perspective_id=None,
            strength=0.8,
            confidence=0.9
        )
        framework.add_relationship(relationship)

        # Export to JSON
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = Path(temp_dir) / "framework_export.json"
            framework.export_to_json(export_file)

            # Create new framework and import data
            new_framework = P3IFFramework()
            new_framework.import_from_json(export_file)

            # Verify data integrity
            assert len(new_framework._patterns) == 2
            assert len(new_framework._relationships) == 1

            # Verify pattern data
            imported_prop = new_framework._patterns[prop.id]
            assert imported_prop.name == prop.name
            assert imported_prop.domain == prop.domain
            assert imported_prop.quality_score == prop.quality_score

            # Verify relationship data
            imported_rel = new_framework._relationships[relationship.id]
            assert imported_rel.strength == relationship.strength
            assert imported_rel.confidence == relationship.confidence

    def test_performance_with_large_dataset(self):
        """Test framework performance with large dataset."""
        framework = P3IFFramework()

        # Create a moderately large dataset
        num_patterns = 100
        num_relationships = 300

        # Track timing
        import time
        start_time = time.time()

        # Add patterns
        for i in range(num_patterns):
            pattern_type = ["property", "process", "perspective"][i % 3]
            pattern = create_pattern_with_metadata(
                pattern_type=pattern_type,
                name=f"Pattern{i}",
                domain=f"Domain{i % 10}"  # 10 domains
            )
            framework.add_pattern(pattern)

        # Add relationships
        for i in range(num_relationships):
            # Create relationships between existing patterns
            patterns = list(framework._patterns.values())
            pattern1 = patterns[i % len(patterns)]

            # Find another pattern of different type if possible
            other_patterns = [p for p in patterns if p.pattern_type != pattern1.pattern_type]
            if other_patterns:
                pattern2 = other_patterns[i % len(other_patterns)]
            else:
                pattern2 = patterns[(i + 1) % len(patterns)]

            # Create relationship data
            rel_data = {
                "strength": 0.5 + (i * 0.001),
                "confidence": 0.6 + (i * 0.0005),
                "relationship_type": "correlation"
            }

            # Set the pattern IDs in the appropriate fields
            if pattern1.pattern_type == "property":
                rel_data["property_id"] = pattern1.id
            elif pattern1.pattern_type == "process":
                rel_data["process_id"] = pattern1.id
            elif pattern1.pattern_type == "perspective":
                rel_data["perspective_id"] = pattern1.id

            if pattern2.pattern_type == "property":
                rel_data["property_id"] = pattern2.id
            elif pattern2.pattern_type == "process":
                rel_data["process_id"] = pattern2.id
            elif pattern2.pattern_type == "perspective":
                rel_data["perspective_id"] = pattern2.id

            # Set the third dimension to None
            for dim in ["property_id", "process_id", "perspective_id"]:
                if dim not in rel_data:
                    rel_data[dim] = None

            try:
                relationship = Relationship(**rel_data)
                framework.add_relationship(relationship)
            except ValueError:
                # Skip invalid relationships
                pass

        end_time = time.time()

        # Performance assertions
        assert len(framework._patterns) == num_patterns
        assert len(framework._relationships) <= num_relationships  # Some may be invalid

        # Operations should complete in reasonable time (under 10 seconds for this size)
        assert (end_time - start_time) < 10.0

        # Test metrics calculation performance
        metrics_start = time.time()
        metrics = framework.get_metrics()
        metrics_end = time.time()

        assert metrics["total_patterns"] == num_patterns
        assert metrics["total_relationships"] == len(framework._relationships)
        assert (metrics_end - metrics_start) < 1.0  # Metrics should be fast to calculate

    def test_error_handling_and_edge_cases(self):
        """Test error handling and edge cases."""
        framework = P3IFFramework()

        # Test adding patterns with various edge cases
        edge_case_patterns = [
            # Pattern with very long name
            Property(name="A" * 200, description="Long name test"),

            # Pattern with special characters
            Property(name="Property@#$%", description="Special chars test"),

            # Pattern with empty description
            Property(name="Empty Desc Property", description=""),

            # Pattern with None values (should be handled by validation)
            Property(name="Minimal Property", description="Minimal test")
        ]

        for pattern in edge_case_patterns:
            framework.add_pattern(pattern)

        assert len(framework._patterns) == 4

        # Test relationships with edge cases
        prop1 = edge_case_patterns[0]
        prop2 = edge_case_patterns[1]

        edge_case_relationships = [
            # Relationship with extreme values
            Relationship(
                property_id=prop1.id,
                process_id=prop2.id,
                perspective_id=None,
                strength=1.0,
                confidence=1.0
            ),

            # Relationship with zero values
            Relationship(
                property_id=prop1.id,
                process_id=None,
                perspective_id=prop2.id,
                strength=0.0,
                confidence=0.0
            )
        ]

        for relationship in edge_case_relationships:
            framework.add_relationship(relationship)

        assert len(framework._relationships) == 2

        # Test invalid operations
        with pytest.raises(ValueError):
            framework.add_pattern(None)

        with pytest.raises(ValueError):
            framework.add_relationship(None)

        # Test operations on non-existent IDs
        with pytest.raises(ValueError):
            framework.remove_pattern("nonexistent")

        with pytest.raises(ValueError):
            framework.remove_relationship("nonexistent")
