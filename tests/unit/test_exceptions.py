"""
Unit tests for P3IF core exceptions.

Tests the custom exception hierarchy and error handling throughout the framework.
"""

import unittest
from p3if.core.exceptions import (
    P3IFError, PatternError, PatternNotFoundError, PatternValidationError,
    PatternTypeError, RelationshipError, RelationshipValidationError,
    FrameworkError, FrameworkValidationError, OperationError
)


class TestP3IFExceptions(unittest.TestCase):
    """Test cases for P3IF custom exceptions."""

    def test_p3if_error_basic(self):
        """Test basic P3IF error functionality."""
        error = P3IFError("Test error message")
        self.assertEqual(str(error), "Test error message")
        self.assertEqual(error.message, "Test error message")
        self.assertEqual(error.details, {})

    def test_p3if_error_with_details(self):
        """Test P3IF error with additional details."""
        details = {"code": 404, "resource": "pattern"}
        error = P3IFError("Resource not found", details)
        self.assertEqual(error.message, "Resource not found")
        self.assertEqual(error.details, details)
        self.assertIn("code=404", str(error))

    def test_pattern_not_found_error(self):
        """Test pattern not found error."""
        error = PatternNotFoundError("test_pattern_123")
        self.assertEqual(error.pattern_id, "test_pattern_123")
        self.assertIsNone(error.pattern_type)
        self.assertIn("test_pattern_123", str(error))

    def test_pattern_not_found_error_with_type(self):
        """Test pattern not found error with type information."""
        error = PatternNotFoundError("test_pattern_123", "property")
        self.assertEqual(error.pattern_type, "property")
        self.assertIn("property", str(error))

    def test_pattern_validation_error(self):
        """Test pattern validation error."""
        validation_errors = ["Name cannot be empty", "Invalid domain format"]
        error = PatternValidationError("invalid_pattern", validation_errors)
        self.assertEqual(error.details["validation_errors"], validation_errors)
        self.assertIn("Name cannot be empty", str(error))
        self.assertIn("Invalid domain format", str(error))

    def test_pattern_type_error(self):
        """Test pattern type error."""
        error = PatternTypeError("property", "invalid_type")
        self.assertEqual(error.expected_type, "property")
        self.assertEqual(error.actual_type, "invalid_type")
        self.assertIn("Expected pattern type 'property'", str(error))

    def test_relationship_validation_error(self):
        """Test relationship validation error."""
        validation_errors = ["At least two patterns required", "Invalid strength value"]
        pattern_ids = ["prop1", "prop2"]
        error = RelationshipValidationError(validation_errors, pattern_ids)
        self.assertEqual(error.details["validation_errors"], validation_errors)
        self.assertEqual(error.details["pattern_ids"], pattern_ids)
        self.assertIn("At least two patterns required", str(error))

    def test_relationship_validation_error_no_patterns(self):
        """Test relationship validation error without pattern IDs."""
        validation_errors = ["Invalid confidence value"]
        error = RelationshipValidationError(validation_errors)
        self.assertEqual(error.details["validation_errors"], validation_errors)
        self.assertNotIn("pattern_ids", error.details)

    def test_framework_validation_error(self):
        """Test framework validation error."""
        validation_errors = ["Missing required patterns", "Circular dependencies detected"]
        error = FrameworkValidationError(validation_errors)
        self.assertEqual(error.details["validation_errors"], validation_errors)
        self.assertIn("Missing required patterns", str(error))

    def test_operation_error(self):
        """Test operation error."""
        error = OperationError("operation_failed", "op_123", "Database connection failed")
        self.assertEqual(error.details["operation_type"], "operation_failed")
        self.assertEqual(error.details["operation_id"], "op_123")
        self.assertEqual(error.details["error_message"], "Database connection failed")
        self.assertIn("operation_failed", str(error))

    def test_exception_hierarchy(self):
        """Test that exceptions follow proper inheritance hierarchy."""
        # Test that all exceptions inherit from P3IFError
        pattern_error = PatternNotFoundError("test")
        self.assertIsInstance(pattern_error, P3IFError)
        self.assertIsInstance(pattern_error, PatternError)

        relationship_error = RelationshipValidationError(["error"])
        self.assertIsInstance(relationship_error, P3IFError)
        self.assertIsInstance(relationship_error, RelationshipError)

        framework_error = FrameworkError(["error"])
        self.assertIsInstance(framework_error, P3IFError)
        self.assertIsInstance(framework_error, FrameworkError)

        operation_error = OperationError("type", "id", "message")
        self.assertIsInstance(operation_error, P3IFError)
        self.assertIsInstance(operation_error, OperationError)

    def test_error_details_preservation(self):
        """Test that error details are properly preserved and accessible."""
        # Test with complex details
        complex_details = {
            "timestamp": "2024-01-01T12:00:00Z",
            "user_id": "user_123",
            "operation": "create_pattern",
            "parameters": {"name": "test", "type": "property"},
            "stack_trace": ["line1", "line2", "line3"]
        }

        error = P3IFError("Complex error occurred", complex_details)
        self.assertEqual(error.details, complex_details)
        self.assertEqual(error.details["user_id"], "user_123")
        self.assertEqual(len(error.details["stack_trace"]), 3)

    def test_error_string_formatting(self):
        """Test that error string formatting works correctly."""
        # Test error without details
        simple_error = P3IFError("Simple message")
        self.assertEqual(str(simple_error), "Simple message")

        # Test error with single detail
        single_detail_error = P3IFError("Message", {"key": "value"})
        self.assertEqual(str(single_detail_error), "Message (key=value)")

        # Test error with multiple details
        multi_detail_error = P3IFError("Message", {"key1": "value1", "key2": "value2"})
        error_str = str(multi_detail_error)
        self.assertIn("Message", error_str)
        self.assertIn("key1=value1", error_str)
        self.assertIn("key2=value2", error_str)


if __name__ == '__main__':
    unittest.main()