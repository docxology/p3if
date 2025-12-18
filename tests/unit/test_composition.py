"""
P3IF Composition Tests

Comprehensive tests for P3IF composition and multiplexing functionality.
"""

import unittest
import pytest
from typing import Dict, List, Any

from p3if.core.composition import (
    CompositionEngine, FrameworkAdapter,
    MultiplexingStrategy, Multiplexer
)
from p3if.core.framework import P3IFFramework
from p3if.core.models import Property, Process, Perspective
from tests.fixtures.helpers import create_test_framework


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

        # Create a simple object that mimics external source structure
        class ExternalElement:
            def __init__(self):
                self.source_name = "Test Property"
                self.source_type = "security"

        external_element = ExternalElement()
        result = adapter.map_element(external_element, "properties")

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
        # Create real frameworks with actual patterns
        framework1 = P3IFFramework()
        prop1 = Property(name="prop1", description="Property 1", domain="test")
        prop2 = Property(name="prop2", description="Property 2", domain="test")
        proc1 = Process(name="proc1", description="Process 1", domain="test")
        persp1 = Perspective(name="persp1", description="Perspective 1", domain="test", viewpoint="test_view")

        framework1.add_pattern(prop1)
        framework1.add_pattern(prop2)
        framework1.add_pattern(proc1)
        framework1.add_pattern(persp1)

        framework2 = P3IFFramework()
        prop3 = Property(name="prop3", description="Property 3", domain="test")
        proc2 = Process(name="proc2", description="Process 2", domain="test")
        persp2 = Perspective(name="persp2", description="Perspective 2", domain="test", viewpoint="test_view")

        framework2.add_pattern(prop2)  # prop2 is common
        framework2.add_pattern(prop3)
        framework2.add_pattern(proc1)  # proc1 is common
        framework2.add_pattern(proc2)
        framework2.add_pattern(persp2)

        # Create simple framework-like objects for composition testing
        class SimpleFramework:
            def __init__(self, properties, processes, perspectives):
                self.properties = properties
                self.processes = processes
                self.perspectives = perspectives

            def copy(self):
                return SimpleFramework(
                    set(self.properties),
                    set(self.processes),
                    set(self.perspectives)
                )

        simple1 = SimpleFramework({prop1.name, prop2.name}, {proc1.name}, {persp1.name})
        simple2 = SimpleFramework({prop2.name, prop3.name}, {proc1.name, proc2.name}, {persp2.name})

        result = self.engine.overlay_frameworks(
            simple1, simple2, MultiplexingStrategy.UNION
        )

        # Check that union was applied correctly
        self.assertEqual(result.properties, {prop1.name, prop2.name, prop3.name})
        self.assertEqual(result.processes, {proc1.name, proc2.name})
        self.assertEqual(result.perspectives, {persp1.name, persp2.name})

    def test_overlay_frameworks_intersection_strategy(self):
        """Test framework overlay with intersection strategy."""
        # Create real frameworks with actual patterns
        framework1 = P3IFFramework()
        prop1 = Property(name="prop1", description="Property 1", domain="test")
        prop2 = Property(name="prop2", description="Property 2", domain="test")
        proc1 = Process(name="proc1", description="Process 1", domain="test")
        persp1 = Perspective(name="persp1", description="Perspective 1", domain="test", viewpoint="test_view")

        framework1.add_pattern(prop1)
        framework1.add_pattern(prop2)
        framework1.add_pattern(proc1)
        framework1.add_pattern(persp1)

        framework2 = P3IFFramework()
        prop3 = Property(name="prop3", description="Property 3", domain="test")
        proc2 = Process(name="proc2", description="Process 2", domain="test")
        persp2 = Perspective(name="persp2", description="Perspective 2", domain="test", viewpoint="test_view")

        framework2.add_pattern(prop2)  # prop2 is common
        framework2.add_pattern(prop3)
        framework2.add_pattern(proc1)  # proc1 is common
        framework2.add_pattern(proc2)
        framework2.add_pattern(persp2)

        # Create simple framework-like objects for composition testing
        class SimpleFramework:
            def __init__(self, properties, processes, perspectives):
                self.properties = properties
                self.processes = processes
                self.perspectives = perspectives

            def copy(self):
                return SimpleFramework(
                    set(self.properties),
                    set(self.processes),
                    set(self.perspectives)
                )

        simple1 = SimpleFramework({prop1.name, prop2.name}, {proc1.name}, {persp1.name})
        simple2 = SimpleFramework({prop2.name, prop3.name}, {proc1.name, proc2.name}, {persp2.name})

        result = self.engine.overlay_frameworks(
            simple1, simple2, MultiplexingStrategy.INTERSECTION
        )

        # Check that intersection was applied correctly
        self.assertEqual(result.properties, {"prop2"})  # Only common element
        self.assertEqual(result.processes, {"proc1"})  # Only common element
        self.assertEqual(result.perspectives, set())   # No common elements

    def test_transform_dimension(self):
        """Test dimension transformation."""
        # Create real framework with actual patterns
        framework = P3IFFramework()
        prop1 = Property(name="property1", description="Property 1", domain="test")
        prop2 = Property(name="property2", description="Property 2", domain="test")
        proc1 = Process(name="process1", description="Process 1", domain="test")
        persp1 = Perspective(name="perspective1", description="Perspective 1", domain="test", viewpoint="test_view")

        framework.add_pattern(prop1)
        framework.add_pattern(prop2)
        framework.add_pattern(proc1)
        framework.add_pattern(persp1)

        # Create simple framework-like object for testing
        class SimpleFramework:
            def __init__(self, properties, processes, perspectives):
                self.properties = properties
                self.processes = processes
                self.perspectives = perspectives

            def copy(self):
                return SimpleFramework(
                    list(self.properties),
                    list(self.processes),
                    list(self.perspectives)
                )

        simple = SimpleFramework(["property1", "property2"], ["process1"], ["perspective1"])

        def transform_func(element):
            return f"transformed_{element}"

        result = self.engine.transform_dimension(simple, "properties", transform_func)

        # Verify transformation was applied
        self.assertEqual(len(result.properties), 2)
        self.assertTrue(all(p.startswith("transformed_") for p in result.properties))

    def test_filter_by_criteria(self):
        """Test filtering by criteria."""
        # Create real framework with actual patterns
        framework = P3IFFramework()
        prop1 = Property(name="Security", description="Security property", domain="security", tags=["security"])
        prop2 = Property(name="Business", description="Business property", domain="business", tags=["business"])
        proc1 = Process(name="process1", description="Process 1", domain="test")
        persp1 = Perspective(name="perspective1", description="Perspective 1", domain="test", viewpoint="test_view")

        framework.add_pattern(prop1)
        framework.add_pattern(prop2)
        framework.add_pattern(proc1)
        framework.add_pattern(persp1)

        # Create simple framework-like object for testing
        class SimpleFramework:
            def __init__(self, properties, processes, perspectives):
                self.properties = properties
                self.processes = processes
                self.perspectives = perspectives

            def copy(self):
                return SimpleFramework(
                    list(self.properties),
                    list(self.processes),
                    list(self.perspectives)
                )

        # Create mock-like objects with domain attributes
        class MockElement:
            def __init__(self, name, domain):
                self.name = name
                self.domain = domain

        simple = SimpleFramework(
            [MockElement("Security", "security"), MockElement("Business", "business")],
            [MockElement("process1", "other")],  # Process in different domain
            [MockElement("perspective1", "other")]  # Perspective in different domain
        )

        # Filter by domain
        criteria = {"domain": "security"}
        result = self.engine.filter_by_criteria(simple, criteria)

        # Should only include security property
        self.assertEqual(len(result.properties), 1)
        self.assertEqual(result.properties[0].name, "Security")
        self.assertEqual(len(result.processes), 0)  # No processes in security domain
        self.assertEqual(len(result.perspectives), 0)  # No perspectives in security domain

    def test_project_dimensions(self):
        """Test dimension projection."""
        # Create real framework with actual patterns
        framework = P3IFFramework()
        prop1 = Property(name="prop1", description="Property 1", domain="test")
        prop2 = Property(name="prop2", description="Property 2", domain="test")
        proc1 = Process(name="proc1", description="Process 1", domain="test")
        proc2 = Process(name="proc2", description="Process 2", domain="test")
        persp1 = Perspective(name="persp1", description="Perspective 1", domain="test", viewpoint="test_view")
        persp2 = Perspective(name="persp2", description="Perspective 2", domain="test", viewpoint="test_view")

        framework.add_pattern(prop1)
        framework.add_pattern(prop2)
        framework.add_pattern(proc1)
        framework.add_pattern(proc2)
        framework.add_pattern(persp1)
        framework.add_pattern(persp2)

        # Create simple framework-like object for testing
        class SimpleFramework:
            def __init__(self, properties, processes, perspectives):
                self.properties = properties
                self.processes = processes
                self.perspectives = perspectives

            def copy(self):
                return SimpleFramework(
                    list(self.properties),
                    list(self.processes),
                    list(self.perspectives)
                )

        simple = SimpleFramework(["prop1", "prop2"], ["proc1", "proc2"], ["persp1", "persp2"])

        dimensions = ["properties", "processes"]
        result = self.engine.project_dimensions(simple, dimensions)

        # Should include properties and processes but not perspectives
        self.assertEqual(len(result.properties), 2)
        self.assertEqual(len(result.processes), 2)
        self.assertEqual(len(result.perspectives), 0)

    def test_composition_history(self):
        """Test that composition operations are recorded."""
        # Create real frameworks
        framework1 = P3IFFramework()
        prop1 = Property(name="prop1", description="Property 1", domain="test")
        proc1 = Process(name="proc1", description="Process 1", domain="test")
        persp1 = Perspective(name="persp1", description="Perspective 1", domain="test", viewpoint="test_view")

        framework1.add_pattern(prop1)
        framework1.add_pattern(proc1)
        framework1.add_pattern(persp1)

        framework2 = P3IFFramework()
        prop2 = Property(name="prop2", description="Property 2", domain="test")
        proc2 = Process(name="proc2", description="Process 2", domain="test")
        persp2 = Perspective(name="persp2", description="Perspective 2", domain="test", viewpoint="test_view")

        framework2.add_pattern(prop2)
        framework2.add_pattern(proc2)
        framework2.add_pattern(persp2)

        # Create simple framework-like objects for testing
        class SimpleFramework:
            def __init__(self, properties, processes, perspectives):
                self.properties = properties
                self.processes = processes
                self.perspectives = perspectives

            def copy(self):
                return SimpleFramework(
                    set(self.properties),
                    set(self.processes),
                    set(self.perspectives)
                )

        simple1 = SimpleFramework({"prop1"}, {"proc1"}, {"persp1"})
        simple2 = SimpleFramework({"prop2"}, {"proc2"}, {"persp2"})

        initial_history_length = len(self.engine.composition_history)

        self.engine.overlay_frameworks(simple1, simple2)

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
        # Create objects with custom attributes for multiplexing test
        class CustomProperty:
            def __init__(self, name, security_level):
                self.name = name
                self.security_level = security_level

        prop1 = CustomProperty("Confidentiality", "high")
        prop2 = CustomProperty("Integrity", "medium")

        properties = [prop1, prop2]

        mapping_rules = {
            "security_processes": "security_level"
        }

        result = self.multiplexer.multiplex_properties_to_processes(properties, mapping_rules)

        self.assertIn("security_processes", result)
        self.assertEqual(len(result["security_processes"]), 2)

    def test_multiplex_processes_to_perspectives(self):
        """Test multiplexing processes to perspectives."""
        # Create objects with custom attributes for multiplexing test
        class CustomProcess:
            def __init__(self, name, complexity):
                self.name = name
                self.complexity = complexity

        proc1 = CustomProcess("Authentication", "high")
        proc2 = CustomProcess("Authorization", "medium")

        processes = [proc1, proc2]

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
        # Create objects with name attributes for testing
        class NamedElement:
            def __init__(self, name):
                self.name = name

        elem1 = NamedElement("Security Property")
        elem2 = NamedElement("Security Process")
        elem3 = NamedElement("Business Process")

        # Security elements should be related
        self.assertTrue(self.multiplexer._potentially_related(elem1, elem2))

        # Security and business elements should not be related
        self.assertFalse(self.multiplexer._potentially_related(elem1, elem3))


if __name__ == '__main__':
    unittest.main()
