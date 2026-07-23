"""
Tests for FrameworkBuilder fluent API, __eq__ on models, DomainData validation.
"""

import unittest
import json
import tempfile
import os

from p3if.core.framework import FrameworkBuilder, P3IFFramework
from p3if.core.models import Property, Process, Perspective, Relationship, BasePattern, PatternType
from p3if.data.domain_model import DomainData


class TestFrameworkBuilder(unittest.TestCase):
    """Test the fluent builder API."""

    def test_basic_chaining(self):
        fw = (FrameworkBuilder()
              .add_property(name="Security", description="Sec prop", domain="cybersec")
              .add_process(name="Auth", description="Auth proc", domain="cybersec")
              .add_perspective(name="Technical", description="Tech persp", domain="cybersec", viewpoint="dev")
              .build())

        self.assertIsInstance(fw, P3IFFramework)
        self.assertEqual(len(fw), 3)
        self.assertEqual(len(fw.get_all_relationships()), 0)

    def test_chaining_with_relationships(self):
        builder = FrameworkBuilder()
        builder.add_property(name="P1", description="d", domain="test")
        builder.add_process(name="Pr1", description="d", domain="test")

        fw = builder.build()
        prop = fw.get_patterns_by_type("property")[0]
        proc = fw.get_patterns_by_type("process")[0]

        # Chain relationship
        builder.add_relationship(property_id=prop.id, process_id=proc.id, strength=0.8)
        fw = builder.build()
        self.assertEqual(len(fw.get_all_relationships()), 1)

    def test_add_pattern_directly(self):
        fw = (FrameworkBuilder()
              .add_pattern(Property(name="Direct", description="d", domain="test"))
              .build())
        self.assertEqual(len(fw), 1)

    def test_builder_repr(self):
        builder = FrameworkBuilder()
        r = repr(builder)
        self.assertIn("FrameworkBuilder", r)

    def test_builder_with_existing_framework(self):
        existing = P3IFFramework()
        existing.add_pattern(Property(name="Existing", description="d", domain="test"))
        builder = FrameworkBuilder(existing)
        builder.add_process(name="New", description="d", domain="test")
        fw = builder.build()
        self.assertEqual(len(fw), 2)
        self.assertIs(fw, existing)


class TestModelEquality(unittest.TestCase):
    """Test __eq__ and __hash__ on BasePattern and Relationship."""

    def test_pattern_equality_by_name_domain_type(self):
        """Two patterns with same name+domain+type should be equal."""
        p1 = Property(name="Security", description="d1", domain="cybersec")
        p2 = Property(name="Security", description="d2", domain="cybersec")
        self.assertEqual(p1, p2)

    def test_pattern_inequality_different_name(self):
        p1 = Property(name="Security", description="d", domain="cybersec")
        p2 = Property(name="Privacy", description="d", domain="cybersec")
        self.assertNotEqual(p1, p2)

    def test_pattern_inequality_different_type(self):
        p1 = Property(name="Auth", description="d", domain="test")
        p2 = Process(name="Auth", description="d", domain="test")
        self.assertNotEqual(p1, p2)

    def test_pattern_hash_consistency(self):
        """Equal patterns should have equal hashes."""
        p1 = Property(name="Security", description="d1", domain="cybersec")
        p2 = Property(name="Security", description="d2", domain="cybersec")
        self.assertEqual(hash(p1), hash(p2))

    def test_pattern_in_set(self):
        """Patterns should be deduplicated in a set by name+domain+type."""
        p1 = Property(name="Security", description="d1", domain="cybersec")
        p2 = Property(name="Security", description="d2", domain="cybersec")
        p3 = Property(name="Privacy", description="d3", domain="cybersec")
        s = {p1, p2, p3}
        self.assertEqual(len(s), 2)

    def test_relationship_equality(self):
        """Two relationships with same pattern IDs and type should be equal."""
        r1 = Relationship(property_id="p1", process_id="pr1", strength=0.8)
        r2 = Relationship(property_id="p1", process_id="pr1", strength=0.5)
        self.assertEqual(r1, r2)

    def test_relationship_inequality_different_type(self):
        r1 = Relationship(property_id="p1", process_id="pr1", relationship_type="causal")
        r2 = Relationship(property_id="p1", process_id="pr1", relationship_type="dependency")
        self.assertNotEqual(r1, r2)

    def test_relationship_hash(self):
        r1 = Relationship(property_id="p1", process_id="pr1")
        r2 = Relationship(property_id="p1", process_id="pr1", strength=0.3)
        self.assertEqual(hash(r1), hash(r2))

    def test_pattern_eq_with_non_pattern(self):
        p = Property(name="Test", description="d", domain="test")
        self.assertNotEqual(p, "not a pattern")
        self.assertNotEqual(p, 42)


class TestDomainData(unittest.TestCase):
    """Test DomainData Pydantic model for domain JSON validation."""

    def test_valid_domain_data(self):
        data = {
            "domain": "TestDomain",
            "version": "1.0",
            "properties": ["Prop1", "Prop2"],
            "processes": ["Proc1"],
            "perspectives": ["Persp1"]
        }
        dd = DomainData(**data)
        self.assertEqual(dd.domain, "TestDomain")
        self.assertEqual(len(dd.properties), 2)
        self.assertEqual(dd.total_elements(), 4)

    def test_strips_whitespace(self):
        data = {
            "domain": "  SpacedDomain  ",
            "properties": ["  Prop1  ", "Prop2"],
            "processes": [],
            "perspectives": []
        }
        dd = DomainData(**data)
        self.assertEqual(dd.domain, "SpacedDomain")
        self.assertEqual(dd.properties, ["Prop1", "Prop2"])

    def test_empty_domain_rejected(self):
        with self.assertRaises(Exception):
            DomainData(domain="", properties=[], processes=[], perspectives=[])

    def test_empty_entries_rejected(self):
        with self.assertRaises(Exception):
            DomainData(domain="Test", properties=["Valid", ""])

    def test_extra_fields_ignored(self):
        data = {
            "domain": "Test",
            "properties": [],
            "processes": [],
            "perspectives": [],
            "extra_field": "ignored"
        }
        dd = DomainData(**data)
        self.assertEqual(dd.domain, "Test")

    def test_load_actual_domain_file(self):
        """Load an actual domain JSON from data/domains/."""
        domain_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..",
            "data", "domains", "healthcare.json"
        )
        if not os.path.exists(domain_path):
            self.skipTest("healthcare.json not found")
        with open(domain_path) as f:
            raw = json.load(f)
        dd = DomainData(**raw)
        self.assertEqual(dd.domain, "HealthCare")
        self.assertGreater(len(dd.properties), 0)
        self.assertGreater(len(dd.processes), 0)
        self.assertGreater(len(dd.perspectives), 0)

    def test_repr(self):
        dd = DomainData(domain="Test", properties=["a"], processes=["b"], perspectives=["c"])
        r = repr(dd)
        self.assertIn("DomainData", r)


if __name__ == '__main__':
    unittest.main()
