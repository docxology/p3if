"""
Integration tests for P3IF core functionality.
"""

import pytest
from p3if.core import P3IFCore
from p3if.core.models import Property, Process, Perspective
from p3if.core.exceptions import (
    PatternNotFoundError, PatternValidationError,
    RelationshipValidationError, PatternTypeError
)


class TestP3IFCoreIntegration:
    """Integration tests for P3IF core operations."""

    def test_full_pattern_lifecycle(self):
        """Test complete pattern creation, update, and deletion lifecycle."""
        core = P3IFCore()

        # Create a pattern
        pattern = core.create_pattern("property", "Test Security", domain="cybersecurity")
        assert pattern.name == "Test Security"
        assert pattern.domain == "cybersecurity"

        # Update the pattern
        updated_pattern = core.update_pattern(pattern.id, {"description": "Updated description"})
        assert updated_pattern.description == "Updated description"

        # Delete the pattern
        result = core.delete_pattern(pattern.id)
        assert result is True

        # Verify pattern is gone
        assert core.framework.get_pattern(pattern.id) is None

    def test_relationship_creation_with_pattern_objects(self):
        """Test relationship creation using pattern objects."""
        core = P3IFCore()

        # Create patterns
        prop = core.create_pattern("property", "Security Property", domain="test")
        proc = core.create_pattern("process", "Authentication Process", domain="test")
        persp = core.create_pattern("perspective", "Technical View", domain="test")

        # Create relationship using pattern objects
        relationship = core.create_relationship(prop, proc, persp, strength=0.8, confidence=0.9)

        assert relationship.property_id == prop.id
        assert relationship.process_id == proc.id
        assert relationship.perspective_id == persp.id
        assert relationship.strength == 0.8
        assert relationship.confidence == 0.9

    def test_relationship_creation_with_ids(self):
        """Test relationship creation using pattern IDs."""
        core = P3IFCore()

        # Create patterns
        prop = core.create_pattern("property", "Security Property", domain="test")
        proc = core.create_pattern("process", "Authentication Process", domain="test")
        persp = core.create_pattern("perspective", "Technical View", domain="test")

        # Create relationship using IDs
        relationship = core.create_relationship(
            prop.id, proc.id, persp.id,
            strength=0.7, confidence=0.8
        )

        assert relationship.property_id == prop.id
        assert relationship.process_id == proc.id
        assert relationship.perspective_id == persp.id
        assert relationship.strength == 0.7
        assert relationship.confidence == 0.8

    def test_relationship_validation_errors(self):
        """Test relationship validation error handling."""
        core = P3IFCore()

        # Test: Not enough patterns
        with pytest.raises(RelationshipValidationError) as exc_info:
            core.create_relationship("prop1", None, None)
        assert "At least two pattern IDs must be provided" in str(exc_info.value)

        # Test: Invalid strength
        prop = core.create_pattern("property", "Test Property")
        proc = core.create_pattern("process", "Test Process")

        with pytest.raises(RelationshipValidationError) as exc_info:
            core.create_relationship(prop.id, proc.id, None, strength=1.5)
        assert "Strength must be between 0.0 and 1.0" in str(exc_info.value)

        # Test: Pattern not found
        with pytest.raises(RelationshipValidationError) as exc_info:
            core.create_relationship("nonexistent_id", proc.id, None)
        assert "Property with ID nonexistent_id not found" in str(exc_info.value)

    def test_pattern_validation_errors(self):
        """Test pattern validation error handling."""
        core = P3IFCore()

        # Test: Empty name
        with pytest.raises(PatternValidationError) as exc_info:
            core.create_pattern("property", "")
        assert "Pattern name cannot be empty" in str(exc_info.value)

        # Test: Invalid type
        with pytest.raises(PatternTypeError) as exc_info:
            core.create_pattern("invalid_type", "Test Pattern")
        assert "property, process, perspective" in str(exc_info.value)

    def test_bulk_pattern_operations(self):
        """Test bulk pattern creation operations."""
        core = P3IFCore()

        # Create multiple patterns in bulk
        pattern_data = [
            {"type": "property", "name": "Property 1", "domain": "test"},
            {"type": "process", "name": "Process 1", "domain": "test"},
            {"type": "perspective", "name": "Perspective 1", "domain": "test"},
        ]

        created_patterns = core.create_pattern_bulk(pattern_data)

        assert len(created_patterns) == 3
        assert all(pattern is not None for pattern in created_patterns)
        assert len(core.framework._patterns) == 3

    def test_operation_history_tracking(self):
        """Test that operations are properly tracked."""
        core = P3IFCore()

        # Perform some operations
        pattern = core.create_pattern("property", "Test Property")
        updated_pattern = core.update_pattern(pattern.id, {"description": "Updated"})
        core.delete_pattern(pattern.id)

        # Check operation history
        operations = core.get_operation_history()
        assert len(operations) == 3

        # Check operation types
        operation_types = [op.operation_type.value for op in operations]
        assert "create" in operation_types
        assert "update" in operation_types
        assert "delete" in operation_types

    def test_pattern_search_functionality(self):
        """Test pattern search and filtering."""
        core = P3IFCore()

        # Create test patterns
        core.create_pattern("property", "Security Property", domain="cyber")
        core.create_pattern("property", "Quality Property", domain="business")
        core.create_pattern("process", "Authentication Process", domain="cyber")

        # Search by type
        properties = core.find_patterns({"type": "property"})
        assert len(properties) == 2

        # Search by domain
        cyber_patterns = core.find_patterns({"domain": "cyber"})
        assert len(cyber_patterns) == 2

        # Search by name substring
        security_patterns = core.find_patterns({"name": "Security"})
        assert len(security_patterns) == 1
        assert "Security" in security_patterns[0].name

    def test_framework_analysis(self):
        """Test framework analysis functionality."""
        core = P3IFCore()

        # Create test data
        core.create_pattern("property", "Prop1", domain="domain1")
        core.create_pattern("property", "Prop2", domain="domain1")
        core.create_pattern("process", "Proc1", domain="domain2")

        # Analyze framework
        analysis = core.analyze_patterns()

        assert analysis["total_patterns"] == 3
        assert analysis["pattern_types"]["property"] == 2
        assert analysis["pattern_types"]["process"] == 1
        assert "domain1" in analysis["domains"]
        assert analysis["domains"]["domain1"]["count"] == 2
