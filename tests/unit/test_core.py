"""
P3IF Core Tests

Comprehensive tests for P3IF core functionality, ensuring modular methods work correctly.
"""

import unittest
import pytest
from datetime import datetime
from typing import Dict, List, Any
import tempfile
import json
import os

from p3if.core.core import P3IFCore, P3IFOperation, OperationType
from p3if.core.models import Property, Process, Perspective, Relationship
from p3if.core.exceptions import PatternTypeError, PatternNotFoundError, RelationshipValidationError, PatternValidationError


class TestP3IFCore(unittest.TestCase):
    """Test cases for P3IFCore functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.core = P3IFCore()

    def test_create_property(self):
        """Test creating a property."""
        prop = self.core.create_pattern("property", "Test Property", "test_domain", "A test property")

        self.assertIsNotNone(prop)
        self.assertEqual(prop.name, "Test Property")
        self.assertEqual(prop.domain, "test_domain")
        self.assertEqual(prop.description, "A test property")
        self.assertIsInstance(prop, Property)

    def test_create_process(self):
        """Test creating a process."""
        proc = self.core.create_pattern("process", "Test Process", "test_domain", "A test process")

        self.assertIsNotNone(proc)
        self.assertEqual(proc.name, "Test Process")
        self.assertEqual(proc.domain, "test_domain")
        self.assertEqual(proc.description, "A test process")
        self.assertIsInstance(proc, Process)

    def test_create_perspective(self):
        """Test creating a perspective."""
        pers = self.core.create_pattern("perspective", "Test Perspective", "test_domain",
                                      "A test perspective", viewpoint="test_view")

        self.assertIsNotNone(pers)
        self.assertEqual(pers.name, "Test Perspective")
        self.assertEqual(pers.domain, "test_domain")
        self.assertEqual(pers.description, "A test perspective")
        self.assertEqual(pers.viewpoint, "test_view")
        self.assertIsInstance(pers, Perspective)

    def test_find_patterns(self):
        """Test finding patterns with criteria."""
        # Create test patterns
        self.core.create_pattern("property", "Security Property", "cybersecurity")
        self.core.create_pattern("process", "Security Process", "cybersecurity")
        self.core.create_pattern("property", "Business Property", "business")

        # Test finding by domain
        cyber_patterns = self.core.find_patterns({"domain": "cybersecurity"})
        self.assertEqual(len(cyber_patterns), 2)

        # Test finding by name
        business_patterns = self.core.find_patterns({"name": "Business Property"})
        self.assertEqual(len(business_patterns), 1)

    def test_create_relationship(self):
        """Test creating relationships between patterns."""
        # Create patterns
        prop = self.core.create_pattern("property", "Confidentiality", "security")
        proc = self.core.create_pattern("process", "Encryption", "security")

        # Create relationship
        rel = self.core.create_relationship(prop, proc, strength=0.9, confidence=0.95)

        self.assertIsNotNone(rel)
        self.assertEqual(rel.strength, 0.9)
        self.assertEqual(rel.confidence, 0.95)
        self.assertIsInstance(rel, Relationship)

    def test_analyze_patterns(self):
        """Test pattern analysis functionality."""
        # Create test data
        self.core.create_pattern("property", "Confidentiality", "security")
        self.core.create_pattern("property", "Integrity", "security")
        self.core.create_pattern("process", "Encryption", "security")
        self.core.create_pattern("property", "Availability", "business")

        analysis = self.core.analyze_patterns()

        self.assertIn("total_patterns", analysis)
        self.assertIn("total_relationships", analysis)
        self.assertIn("domains", analysis)
        self.assertIn("pattern_types", analysis)

        self.assertGreaterEqual(analysis["total_patterns"], 4)

    def test_operation_history(self):
        """Test operation history tracking."""
        # Perform operations
        self.core.create_pattern("property", "Test Property", "test")
        self.core.create_pattern("process", "Test Process", "test")

        history = self.core.get_operation_history()

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].operation_type, OperationType.CREATE)
        self.assertEqual(history[0].description, "Create property: Test Property")

    def test_create_relationship_with_strength_and_confidence(self):
        """Test creating a relationship with custom strength and confidence."""
        prop = self.core.create_pattern("property", "Test Property", "test_domain")
        proc = self.core.create_pattern("process", "Test Process", "test_domain")

        rel = self.core.create_relationship(
            prop.id, proc.id, None,
            strength=0.8,
            confidence=0.9
        )
        self.assertEqual(rel.strength, 0.8)
        self.assertEqual(rel.confidence, 0.9)

    def test_create_relationship_invalid_patterns(self):
        """Test creating a relationship with invalid pattern IDs."""
        from p3if.core.exceptions import RelationshipValidationError
        with self.assertRaises(RelationshipValidationError):
            self.core.create_relationship("invalid_prop", "invalid_proc", "invalid_pers")

    def test_create_pattern_bulk(self):
        """Test creating multiple patterns in bulk."""
        patterns_data = [
            {"pattern_type": "property", "name": "Prop1", "domain": "test"},
            {"pattern_type": "property", "name": "Prop2", "domain": "test"},
            {"pattern_type": "process", "name": "Proc1", "domain": "test"}
        ]

        patterns = self.core.create_pattern_bulk(patterns_data)
        self.assertEqual(len(patterns), 3)
        self.assertEqual(patterns[0].name, "Prop1")
        self.assertEqual(patterns[1].name, "Prop2")
        self.assertEqual(patterns[2].name, "Proc1")

    def test_update_pattern(self):
        """Test updating an existing pattern."""
        pattern = self.core.create_pattern("property", "Original Name", "test_domain")

        updated = self.core.update_pattern(pattern.id, {"name": "Updated Name"})
        self.assertEqual(updated.name, "Updated Name")
        self.assertEqual(updated.id, pattern.id)  # ID should remain the same

    def test_update_pattern_not_found(self):
        """Test updating a non-existent pattern."""
        with self.assertRaises(PatternNotFoundError):
            self.core.update_pattern("nonexistent_id", {"name": "New Name"})

    def test_delete_pattern(self):
        """Test deleting a pattern."""
        pattern = self.core.create_pattern("property", "To Delete", "test_domain")

        result = self.core.delete_pattern(pattern.id)
        self.assertTrue(result)

        # Verify pattern is gone
        deleted_pattern = self.core.framework.get_pattern(pattern.id)
        self.assertIsNone(deleted_pattern)

    def test_delete_pattern_with_relationships(self):
        """Test deleting a pattern that has relationships."""
        prop = self.core.create_pattern("property", "Property", "test_domain")
        proc = self.core.create_pattern("process", "Process", "test_domain")
        pers = self.core.create_pattern("perspective", "Perspective", "test_domain")

        rel = self.core.create_relationship(prop.id, proc.id, pers.id)

        # Delete the property pattern
        result = self.core.delete_pattern(prop.id)
        self.assertTrue(result)

        # Verify relationship is also removed
        deleted_rel = self.core.framework.get_relationship(rel.id)
        self.assertIsNone(deleted_rel)

    def test_pattern_validation(self):
        """Test pattern validation functionality."""
        # Valid pattern
        valid_pattern = self.core.create_pattern("property", "Valid Property", "test_domain")
        self.assertIsNotNone(valid_pattern)

        # Invalid pattern type
        with self.assertRaises(PatternTypeError):
            self.core.create_pattern("invalid_type", "Test", "test_domain")

        # Empty name
        with self.assertRaises(PatternValidationError):
            self.core.create_pattern("property", "", "test_domain")

        # Invalid domain length
        with self.assertRaises(PatternValidationError):
            long_domain = "a" * 101  # Too long
            self.core.create_pattern("property", "Test", long_domain)

    def test_relationship_validation(self):
        """Test relationship validation."""
        prop = self.core.create_pattern("property", "Property", "test_domain")
        proc = self.core.create_pattern("process", "Process", "test_domain")

        # Valid relationship
        rel = self.core.create_relationship(prop.id, proc.id, None)
        self.assertIsNotNone(rel)

        # Invalid strength
        with self.assertRaises(RelationshipValidationError):
            self.core.create_relationship(prop.id, proc.id, None, strength=1.5)

        # Invalid confidence
        with self.assertRaises(RelationshipValidationError):
            self.core.create_relationship(prop.id, proc.id, None, confidence=-0.1)

    def test_framework_analysis(self):
        """Test framework analysis capabilities."""
        # Create test framework with multiple patterns and relationships
        prop1 = self.core.create_pattern("property", "Confidentiality", "security")
        prop2 = self.core.create_pattern("property", "Integrity", "security")
        proc = self.core.create_pattern("process", "Encryption", "security")

        rel1 = self.core.create_relationship(prop1.id, proc.id, None, strength=0.9)
        rel2 = self.core.create_relationship(prop2.id, proc.id, None, strength=0.8)

        analysis = self.core.analyze_patterns()

        self.assertIn("total_patterns", analysis)
        self.assertIn("total_relationships", analysis)
        self.assertIn("domains", analysis)
        self.assertEqual(analysis["total_patterns"], 3)
        self.assertEqual(analysis["total_relationships"], 2)

    def test_pattern_search(self):
        """Test pattern search functionality."""
        # Create patterns with different attributes
        prop1 = self.core.create_pattern("property", "Data Security", "cybersecurity")
        prop2 = self.core.create_pattern("property", "Access Control", "security")
        proc = self.core.create_pattern("process", "Authentication", "security")

        # Test search by name
        security_patterns = self.core.find_patterns({"name": "Security"})
        self.assertTrue(any("Security" in p.name for p in security_patterns))

        # Test search by domain
        cyber_patterns = self.core.find_patterns({"domain": "cybersecurity"})
        self.assertEqual(len(cyber_patterns), 1)
        self.assertEqual(cyber_patterns[0].id, prop1.id)

    def test_export_framework(self):
        """Test framework export functionality."""
        # Create test data
        self.core.create_pattern("property", "Test Property", "test")
        self.core.create_pattern("process", "Test Process", "test")

        # Export to JSON
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name

        try:
            result = self.core.export_framework(format="json", path=temp_file)

            # Check file was created
            self.assertTrue(os.path.exists(temp_file))

            # Check file contents
            with open(temp_file, 'r') as f:
                data = json.load(f)

            self.assertIn("patterns", data)
            self.assertIn("relationships", data)
            self.assertIn("metadata", data)

            # Test in-memory export
            json_data = self.core.export_framework(format="json")
            self.assertIsInstance(json_data, str)

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_invalid_pattern_type(self):
        """Test error handling for invalid pattern types."""
        with self.assertRaises(PatternTypeError):
            self.core.create_pattern("invalid_type", "Test", "test")

    def test_relationship_with_invalid_patterns(self):
        """Test error handling for relationships with invalid patterns."""
        from p3if.core.exceptions import RelationshipValidationError
        with self.assertRaises(RelationshipValidationError):
            self.core.create_relationship("invalid_source", "invalid_target")


class TestP3IFOperation(unittest.TestCase):
    """Test cases for P3IFOperation class."""

    def test_operation_creation(self):
        """Test creating a P3IF operation."""
        operation = P3IFOperation(
            operation_type=OperationType.CREATE,
            description="Test operation",
            parameters={"test": "value"}
        )

        self.assertEqual(operation.operation_type, OperationType.CREATE)
        self.assertEqual(operation.description, "Test operation")
        self.assertEqual(operation.parameters, {"test": "value"})
        self.assertEqual(operation.status, "pending")
        self.assertIsNone(operation.result)

    def test_operation_timestamp(self):
        """Test operation timestamp handling."""
        before = datetime.now()
        operation = P3IFOperation()
        after = datetime.now()

        self.assertGreaterEqual(operation.timestamp, before)
        self.assertLessEqual(operation.timestamp, after)


if __name__ == '__main__':
    unittest.main()
