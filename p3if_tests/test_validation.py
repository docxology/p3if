"""
Test cases for P3IF validation framework.
"""

import unittest
from p3if_methods.validation import ValidationEngine, ValidationRule, ValidationSeverity, ConstraintManager
from p3if_methods.models import Property, Process, Perspective, Relationship
from p3if_methods.framework import P3IFFramework


class TestValidationEngine(unittest.TestCase):
    """Test cases for ValidationEngine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = ValidationEngine()
        # Add default validation rules
        from p3if_methods.validation import create_default_validation_rules
        default_rules = create_default_validation_rules()
        for rule in default_rules.values():
            self.engine.add_rule(rule)
        self.framework = P3IFFramework()

    def test_add_validation_rule(self):
        """Test adding validation rules."""
        def dummy_check(obj):
            return {"valid": True}

        rule = ValidationRule("test_rule", dummy_check, ValidationSeverity.INFO, "Test rule")
        self.engine.add_rule(rule)

        self.assertIn("test_rule", self.engine.rules)
        self.assertEqual(self.engine.rules["test_rule"], rule)

    def test_validate_framework_empty(self):
        """Test validation of empty framework."""
        result = self.engine.validate_framework(self.framework)

        self.assertIn("framework", result)
        self.assertIn("timestamp", result)
        self.assertIn("issues", result)
        self.assertIn("summary", result)

    def test_validate_framework_with_patterns(self):
        """Test validation of framework with patterns."""
        # Add some patterns with proper descriptions
        prop = Property(name="Test Property", domain="test", description="A test property for validation")
        proc = Process(name="Test Process", domain="test", description="A test process for validation")
        pers = Perspective(name="Test Perspective", domain="test", viewpoint="test", description="A test perspective for validation")

        self.framework.add_pattern(prop)
        self.framework.add_pattern(proc)
        self.framework.add_pattern(pers)

        result = self.engine.validate_framework(self.framework)

        # Should be valid since all patterns have proper descriptions
        self.assertTrue(result["overall_valid"])

    def test_validate_dimension(self):
        """Test validation of specific dimensions."""
        # Create some patterns
        properties = [
            Property(name="Prop1", domain="test"),
            Property(name="Prop2", domain="test")
        ]

        result = self.engine.validate_dimension("properties", properties)

        self.assertIn("dimension", result)
        self.assertIn("element_count", result)
        self.assertEqual(result["element_count"], 2)


class TestConstraintManager(unittest.TestCase):
    """Test cases for ConstraintManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = ConstraintManager()

    def test_add_constraint(self):
        """Test adding constraints."""
        constraint = {
            "name": "required_description",
            "type": "required_attribute",
            "attribute": "description",
            "severity": "warning"
        }

        self.manager.add_constraint("property", constraint)
        self.assertIn("property", self.manager.constraints)
        self.assertIn(constraint, self.manager.constraints["property"])

    def test_check_constraints(self):
        """Test constraint checking."""
        # Add a constraint
        constraint = {
            "name": "required_description",
            "type": "required_attribute",
            "attribute": "description",
            "severity": "warning"
        }
        self.manager.add_constraint("property", constraint)

        # Test with pattern that has description
        prop_with_desc = Property(name="Test", domain="test", description="Has description")
        violations = self.manager.check_constraints(prop_with_desc)
        self.assertEqual(len(violations), 0)

        # Test with pattern without description
        prop_without_desc = Property(name="Test", domain="test")
        violations = self.manager.check_constraints(prop_without_desc)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["constraint"], "required_description")

    def test_check_single_constraint_required_attribute(self):
        """Test required attribute constraint checking."""
        constraint = {
            "type": "required_attribute",
            "attribute": "description"
        }

        # Object with attribute
        class TestObj:
            def __init__(self):
                self.description = "test"

        obj_with_attr = TestObj()
        result = self.manager._check_single_constraint(obj_with_attr, constraint)
        self.assertTrue(result)

        # Object without attribute
        obj_without_attr = TestObj()
        delattr(obj_without_attr, 'description')
        result = self.manager._check_single_constraint(obj_without_attr, constraint)
        self.assertFalse(result)


class TestValidationRules(unittest.TestCase):
    """Test cases for built-in validation rules."""

    def setUp(self):
        """Set up test fixtures."""
        self.framework = P3IFFramework()
        self.engine = ValidationEngine()
        # Add default validation rules
        from p3if_methods.validation import create_default_validation_rules
        default_rules = create_default_validation_rules()
        for rule in default_rules.values():
            self.engine.add_rule(rule)

    def test_relationship_validity_rule(self):
        """Test relationship validity validation."""
        # Create patterns
        prop = Property(name="Test Property", domain="test")
        proc = Process(name="Test Process", domain="test")
        pers = Perspective(name="Test Perspective", domain="test", viewpoint="test")

        self.framework.add_pattern(prop)
        self.framework.add_pattern(proc)
        self.framework.add_pattern(pers)

        # Valid relationship
        rel = Relationship(property_id=prop.id, process_id=proc.id, perspective_id=pers.id)
        self.framework.add_relationship(rel)

        # Test validation
        engine = ValidationEngine()
        result = engine.validate_framework(self.framework)

        # Should be valid
        self.assertTrue(result["overall_valid"])

    def test_strength_range_rule(self):
        """Test relationship strength range validation."""
        # Create patterns
        prop = Property(name="Test Property", domain="test")
        proc = Process(name="Test Process", domain="test")

        self.framework.add_pattern(prop)
        self.framework.add_pattern(proc)

        # Valid strength
        rel = Relationship(property_id=prop.id, process_id=proc.id, strength=0.8)
        self.framework.add_relationship(rel)

        # Test validation - should pass
        result = self.engine.validate_framework(self.framework)
        self.assertTrue(result["overall_valid"])

        # Try to update to invalid strength (this should fail)
        try:
            rel_invalid = Relationship(property_id=prop.id, process_id=proc.id, strength=1.5)
            # If we get here, the validation should have prevented this
            self.fail("Should not be able to create relationship with invalid strength")
        except Exception:
            # Expected - validation should prevent invalid strength
            pass

    def test_dimension_balance_rule(self):
        """Test dimension balance validation."""
        # Add many properties but few processes and perspectives
        for i in range(10):
            prop = Property(name=f"Property {i}", domain="test")
            self.framework.add_pattern(prop)

        proc = Process(name="Single Process", domain="test")
        pers = Perspective(name="Single Perspective", domain="test", viewpoint="test")

        self.framework.add_pattern(proc)
        self.framework.add_pattern(pers)

        # Test validation
        result = self.engine.validate_framework(self.framework)

        # Should flag dimension imbalance
        self.assertIn("dimension_balance", [issue.get("rule", "") for issue in result["issues"]])


if __name__ == '__main__':
    unittest.main()

