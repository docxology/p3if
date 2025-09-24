"""
P3IF Composition Tests

Comprehensive tests for P3IF composition and multiplexing functionality.
"""

import unittest
import pytest
from typing import Dict, List, Any
from unittest.mock import Mock, MagicMock

try:
    # Try relative imports first (when run as part of package)
    from ..p3if_methods.composition import (
        CompositionEngine, Multiplexer, FrameworkAdapter,
        MultiplexingStrategy, CompositionType
    )
except ImportError:
    try:
        # Fall back to absolute imports (when run directly)
        from p3if_methods.composition import (
            CompositionEngine, Multiplexer, FrameworkAdapter,
            MultiplexingStrategy, CompositionType
        )
    except ImportError as e:
        # If both fail, try importing from parent directory
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from p3if_methods.composition import (
            CompositionEngine, Multiplexer, FrameworkAdapter,
            MultiplexingStrategy, CompositionType
        )


class TestFrameworkAdapter(unittest.TestCase):
    """Test cases for FrameworkAdapter."""

    def test_adapter_creation(self):
        """Test creating a framework adapter."""
        adapter = FrameworkAdapter(
            name="test_adapter",
            version="1.0",
            source_framework="Test Framework",
            mapping_rules={
                "properties": {"name": "name", "type": "type"},
                "processes": {"name": "process_name", "type": "process_type"}
            },
            transformation_functions={
                "test_transform": lambda x: x.name.upper()
            }
        )

        self.assertEqual(adapter.name, "test_adapter")
        self.assertEqual(adapter.version, "1.0")
        self.assertEqual(adapter.source_framework, "Test Framework")
        self.assertIn("properties", adapter.mapping_rules)
        self.assertIn("test_transform", adapter.transformation_functions)

    def test_map_element(self):
        """Test mapping elements through adapter."""
        adapter = FrameworkAdapter(
            name="test_adapter",
            version="1.0",
            source_framework="Test Framework",
            mapping_rules={
                "properties": {"p3if_name": "source_name", "p3if_type": "source_type"}
            },
            transformation_functions={}
        )

        # Mock element
        mock_element = Mock()
        mock_element.source_name = "Test Property"
        mock_element.source_type = "security"

        result = adapter.map_element(mock_element, "properties")

        self.assertEqual(result["p3if_name"], "Test Property")
        self.assertEqual(result["p3if_type"], "security")


class TestCompositionEngine(unittest.TestCase):
    """Test cases for CompositionEngine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = CompositionEngine()

    def test_register_adapter(self):
        """Test registering a framework adapter."""
        adapter = FrameworkAdapter(
            name="test_adapter",
            version="1.0",
            source_framework="Test Framework",
            mapping_rules={},
            transformation_functions={}
        )

        self.engine.register_adapter(adapter)
        self.assertIn("test_adapter", self.engine.adapters)

    def test_overlay_frameworks_union_strategy(self):
        """Test framework overlay with union strategy."""
        # Create mock frameworks
        framework1 = Mock()
        framework1.properties = {"prop1", "prop2"}
        framework1.processes = {"proc1"}
        framework1.perspectives = {"pers1"}

        framework2 = Mock()
        framework2.properties = {"prop2", "prop3"}
        framework2.processes = {"proc1", "proc2"}
        framework2.perspectives = {"pers2"}

        result = self.engine.overlay_frameworks(
            framework1, framework2, MultiplexingStrategy.UNION
        )

        # Check that union was applied correctly
        self.assertEqual(result.properties, {"prop1", "prop2", "prop3"})
        self.assertEqual(result.processes, {"proc1", "proc2"})
        self.assertEqual(result.perspectives, {"pers1", "pers2"})

    def test_overlay_frameworks_intersection_strategy(self):
        """Test framework overlay with intersection strategy."""
        framework1 = Mock()
        framework1.properties = {"prop1", "prop2"}
        framework1.processes = {"proc1"}
        framework1.perspectives = {"pers1"}

        framework2 = Mock()
        framework2.properties = {"prop2", "prop3"}
        framework2.processes = {"proc1", "proc2"}
        framework2.perspectives = {"pers2"}

        result = self.engine.overlay_frameworks(
            framework1, framework2, MultiplexingStrategy.INTERSECTION
        )

        # Check that intersection was applied correctly
        self.assertEqual(result.properties, {"prop2"})  # Only common element
        self.assertEqual(result.processes, {"proc1"})  # Only common element
        self.assertEqual(result.perspectives, set())   # No common elements

    def test_transform_dimension(self):
        """Test dimension transformation."""
        framework = Mock()
        framework.properties = ["property1", "property2"]
        framework.processes = ["process1"]
        framework.perspectives = ["perspective1"]

        # Create a copy method for the mock
        framework.copy = Mock(return_value=Mock(properties=[], processes=[], perspectives=[]))

        def transform_func(element):
            return f"transformed_{element}"

        result = self.engine.transform_dimension(framework, "properties", transform_func)

        # Verify transformation was applied
        self.assertTrue(framework.copy.called)

    def test_filter_by_criteria(self):
        """Test filtering by criteria."""
        framework = Mock()
        framework.properties = [
            Mock(name="Security", type="security"),
            Mock(name="Business", type="business")
        ]
        framework.processes = ["process1"]
        framework.perspectives = ["perspective1"]

        framework.copy = Mock(return_value=Mock(properties=[], processes=[], perspectives=[]))

        criteria = {"type": "security"}
        result = self.engine.filter_by_criteria(framework, criteria)

        self.assertTrue(framework.copy.called)

    def test_project_dimensions(self):
        """Test dimension projection."""
        framework = Mock()
        framework.properties = ["prop1", "prop2"]
        framework.processes = ["proc1", "proc2"]
        framework.perspectives = ["pers1", "pers2"]

        framework.copy = Mock(return_value=Mock(properties=[], processes=[], perspectives=[]))

        dimensions = ["properties", "processes"]
        result = self.engine.project_dimensions(framework, dimensions)

        self.assertTrue(framework.copy.called)

    def test_composition_history(self):
        """Test that composition operations are recorded."""
        framework1 = Mock()
        framework1.properties = {"prop1"}
        framework1.processes = {"proc1"}
        framework1.perspectives = {"pers1"}
        framework1.copy = Mock(return_value=framework1)

        framework2 = Mock()
        framework2.properties = {"prop2"}
        framework2.processes = {"proc2"}
        framework2.perspectives = {"pers2"}

        initial_history_length = len(self.engine.composition_history)

        self.engine.overlay_frameworks(framework1, framework2)

        self.assertEqual(len(self.engine.composition_history), initial_history_length + 1)
        self.assertEqual(self.engine.composition_history[-1]["operation"], "overlay")


class TestMultiplexer(unittest.TestCase):
    """Test cases for Multiplexer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.multiplexer = Multiplexer()

    def test_add_multiplexing_rule(self):
        """Test adding a multiplexing rule."""
        rule_config = {
            "source_dimension": "properties",
            "target_dimension": "processes",
            "mapping": {"name": "process_name", "type": "process_type"}
        }

        self.multiplexer.add_multiplexing_rule("prop_to_proc", rule_config)
        self.assertIn("prop_to_proc", self.multiplexer.multiplexing_rules)

    def test_multiplex_properties_to_processes(self):
        """Test multiplexing properties to processes."""
        # Create mock properties
        properties = [
            Mock(name="Confidentiality", security_level="high"),
            Mock(name="Integrity", security_level="medium")
        ]

        mapping_rules = {
            "security_processes": "security_level"
        }

        result = self.multiplexer.multiplex_properties_to_processes(properties, mapping_rules)

        self.assertIn("security_processes", result)
        self.assertEqual(len(result["security_processes"]), 2)

    def test_multiplex_processes_to_perspectives(self):
        """Test multiplexing processes to perspectives."""
        # Create mock processes
        processes = [
            Mock(name="Authentication", complexity="high"),
            Mock(name="Authorization", complexity="medium")
        ]

        mapping_rules = {
            "technical_perspective": "complexity"
        }

        result = self.multiplexer.multiplex_processes_to_perspectives(processes, mapping_rules)

        self.assertIn("technical_perspective", result)
        self.assertEqual(len(result["technical_perspective"]), 2)

    def test_create_cross_dimensional_links(self):
        """Test creating cross-dimensional links."""
        # Create a simple framework-like object
        class SimpleFramework:
            def __init__(self):
                self.properties = []
                self.processes = []
                self.perspectives = []

        framework = SimpleFramework()
        multiplexer = Multiplexer()

        # Test with empty framework
        links = multiplexer.create_cross_dimensional_links(framework)

        self.assertIsInstance(links, list)
        # Should return empty list for empty framework
        self.assertEqual(len(links), 0)

    def test_potentially_related_heuristic(self):
        """Test the potentially related heuristic."""
        elem1 = Mock()
        elem1.name = "Security Property"

        elem2 = Mock()
        elem2.name = "Security Process"

        elem3 = Mock()
        elem3.name = "Business Process"

        # Security elements should be related
        self.assertTrue(self.multiplexer._potentially_related(elem1, elem2))

        # Security and business elements should not be related
        self.assertFalse(self.multiplexer._potentially_related(elem1, elem3))


if __name__ == '__main__':
    unittest.main()
