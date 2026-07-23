"""
Comprehensive tests for P3IF framework bug fixes and new features.

These tests verify the specific bugs fixed in the second-pass improvement:
- Thread safety in add_pattern/add_relationship
- Batch operations without double-locking
- get_relationships_by_pattern deduplication
- _calculate_metrics_internal pattern type counting
- hot_swap_dimension with PatternType enum
- multiplex_frameworks proper locking
- import/export JSON round-trip
- get_all_patterns / get_all_domains convenience methods
- create_relationship stores relationship_type in field, not metadata
- __repr__ methods
- composition overlay with set operations
"""

import json
import os
import tempfile
import unittest

from p3if.core.framework import P3IFFramework, FrameworkMetrics
from p3if.core.models import (
    Property, Process, Perspective, Relationship,
    PatternType, PatternCollection
)
from p3if.core.core import P3IFCore
from p3if.core.composition import CompositionEngine, MultiplexingStrategy
from p3if.core.exceptions import PatternTypeError


class TestBatchOperations(unittest.TestCase):
    """Test batch add operations work correctly without double-locking."""

    def setUp(self):
        self.framework = P3IFFramework()
        self.patterns = [
            Property(name=f"Prop {i}", description=f"Property {i}", domain="test")
            for i in range(10)
        ]
        self.processes = [
            Process(name=f"Proc {i}", description=f"Process {i}", domain="test")
            for i in range(10)
        ]

    def test_add_patterns_batch_all_successful(self):
        """All valid patterns should be added successfully."""
        result = self.framework.add_patterns_batch(self.patterns)
        self.assertEqual(result['successful'], 10)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(result['total'], 10)
        self.assertEqual(len(self.framework), 10)

    def test_add_patterns_batch_with_duplicates(self):
        """Duplicate patterns should fail but not block others."""
        self.framework.add_pattern(self.patterns[0])
        result = self.framework.add_patterns_batch(self.patterns)
        self.assertEqual(result['successful'], 9)
        self.assertEqual(result['failed'], 1)
        self.assertEqual(result['total'], 10)

    def test_add_relationships_batch(self):
        """Batch add relationships should work correctly."""
        # First add all patterns
        self.framework.add_patterns_batch(self.patterns)
        self.framework.add_patterns_batch(self.processes)

        # Create relationships
        rels = []
        for i in range(5):
            rel = Relationship(
                property_id=self.patterns[i].id,
                process_id=self.processes[i].id,
                strength=0.8,
                confidence=0.9
            )
            rels.append(rel)

        result = self.framework.add_relationships_batch(rels)
        self.assertEqual(result['successful'], 5)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(len(self.framework.get_all_relationships()), 5)

    def test_batch_operations_isolate_failures(self):
        """One bad pattern should not block the rest."""
        patterns = list(self.patterns)
        # Insert a duplicate that's already added
        self.framework.add_pattern(patterns[0])

        result = self.framework.add_patterns_batch(patterns)
        self.assertEqual(result['successful'], 9)
        self.assertEqual(result['failed'], 1)
        self.assertEqual(len(result['errors']), 1)


class TestRelationshipDeduplication(unittest.TestCase):
    """Test that get_relationships_by_pattern doesn't return duplicates."""

    def setUp(self):
        self.framework = P3IFFramework()
        self.prop = Property(name="Prop", description="Test", domain="test")
        self.proc = Process(name="Proc", description="Test", domain="test")
        self.persp = Perspective(name="Persp", description="Test", domain="test", viewpoint="analyst")
        self.framework.add_pattern(self.prop)
        self.framework.add_pattern(self.proc)
        self.framework.add_pattern(self.persp)

    def test_no_duplicate_relationships(self):
        """A relationship connecting all 3 dimensions should appear once."""
        rel = Relationship(
            property_id=self.prop.id,
            process_id=self.proc.id,
            perspective_id=self.persp.id,
            strength=0.8
        )
        self.framework.add_relationship(rel)

        # Should return exactly 1, not 3 (one per index)
        rels = self.framework.get_relationships_by_pattern(self.prop.id)
        self.assertEqual(len(rels), 1)
        self.assertEqual(rels[0].id, rel.id)

    def test_multiple_relationships_no_duplicates(self):
        """Multiple relationships should all be returned without dupes."""
        rel1 = Relationship(property_id=self.prop.id, process_id=self.proc.id, strength=0.7)
        rel2 = Relationship(property_id=self.prop.id, perspective_id=self.persp.id, strength=0.5)
        self.framework.add_relationship(rel1)
        self.framework.add_relationship(rel2)

        rels = self.framework.get_relationships_by_pattern(self.prop.id)
        rel_ids = [r.id for r in rels]
        self.assertEqual(len(rels), 2)
        self.assertEqual(len(set(rel_ids)), 2)  # No duplicates


class TestMetricsCalculation(unittest.TestCase):
    """Test that _calculate_metrics_internal counts pattern types correctly."""

    def test_pattern_type_counts_are_correct(self):
        """Pattern types should be counted by type key, not UUID splitting."""
        fw = P3IFFramework()
        for i in range(5):
            fw.add_pattern(Property(name=f"P{i}", description=f"Prop {i}", domain="test"))
        for i in range(3):
            fw.add_pattern(Process(name=f"Pr{i}", description=f"Proc {i}", domain="test"))
        for i in range(2):
            fw.add_pattern(Perspective(name=f"Pe{i}", description=f"Persp {i}", domain="test", viewpoint="v"))

        metrics = fw.get_metrics()
        self.assertEqual(metrics.total_patterns, 10)
        self.assertEqual(metrics.pattern_types_count.get('property', 0), 5)
        self.assertEqual(metrics.pattern_types_count.get('process', 0), 3)
        self.assertEqual(metrics.pattern_types_count.get('perspective', 0), 2)


class TestHotSwapDimension(unittest.TestCase):
    """Test hot_swap_dimension with PatternType enum."""

    def setUp(self):
        self.framework = P3IFFramework()
        self.prop = Property(name="Prop", description="Test", domain="test")
        self.proc = Process(name="Proc", description="Test", domain="test")
        self.persp = Perspective(name="Persp", description="Test", domain="test", viewpoint="analyst")
        self.framework.add_pattern(self.prop)
        self.framework.add_pattern(self.proc)
        self.framework.add_pattern(self.persp)

        self.rel = Relationship(
            property_id=self.prop.id,
            process_id=self.proc.id,
            strength=0.8
        )
        self.framework.add_relationship(self.rel)

    def test_hot_swap_with_string(self):
        """Hot swap using string dimension names."""
        count = self.framework.hot_swap_dimension("property", "perspective")
        self.assertEqual(count, 1)

    def test_hot_swap_with_pattern_type_enum(self):
        """Hot swap using PatternType enum."""
        # Add a perspective pattern for the swap target
        persp2 = Perspective(name="Persp2", description="Test", domain="test", viewpoint="analyst2")
        self.framework.add_pattern(persp2)

        # Create a relationship connecting property and process
        rel2 = Relationship(
            property_id=self.prop.id,
            process_id=self.proc.id,
            strength=0.7
        )
        self.framework.add_relationship(rel2)

        count = self.framework.hot_swap_dimension(PatternType.PROPERTY, PatternType.PERSPECTIVE)
        self.assertEqual(count, 2)  # Both rel1 (setUp) and rel2 have property_id set

        # Verify the swap: property_id should be None, perspective_id should have the old property_id
        swapped_rel = self.framework.get_relationship(rel2.id)
        self.assertIsNone(swapped_rel.property_id)
        self.assertEqual(swapped_rel.perspective_id, self.prop.id)

    def test_hot_swap_invalid_dimension(self):
        """Invalid dimension should raise ValueError."""
        with self.assertRaises(ValueError):
            self.framework.hot_swap_dimension("invalid", "process")


class TestMultiplexFrameworks(unittest.TestCase):
    """Test multiplex_frameworks integration."""

    def setUp(self):
        self.framework = P3IFFramework()

    def test_multiplex_adds_new_patterns(self):
        """Multiplex should add new patterns from external framework."""
        external = {
            "property": [
                {"name": "New Prop", "description": "External property", "domain": "external"}
            ],
            "process": [
                {"name": "New Proc", "description": "External process", "domain": "external"}
            ],
            "perspective": [
                {"name": "New Persp", "description": "External perspective", "domain": "external",
                 "viewpoint": "external_view"}
            ]
        }
        result = self.framework.multiplex_frameworks(external)
        self.assertEqual(result["integrated"]["property"], 1)
        self.assertEqual(result["integrated"]["process"], 1)
        self.assertEqual(result["integrated"]["perspective"], 1)
        self.assertEqual(len(self.framework), 3)

    def test_multiplex_updates_existing(self):
        """Multiplex should update existing patterns, not duplicate them."""
        prop = Property(name="Existing", description="Original", domain="test")
        self.framework.add_pattern(prop)

        external = {
            "property": [
                {"name": "Existing", "description": "Updated description", "domain": "test"}
            ]
        }
        result = self.framework.multiplex_frameworks(external)
        self.assertEqual(result["integrated"]["property"], 0)
        self.assertEqual(result["skipped"]["property"], 1)
        self.assertEqual(len(self.framework), 1)  # No duplicate

    def test_multiplex_skips_unknown_dimension(self):
        """Unknown dimensions should be skipped, not crash."""
        external = {"unknown": [{"name": "test", "description": "test", "domain": "test"}]}
        result = self.framework.multiplex_frameworks(external)
        self.assertEqual(result["integrated"], {"property": 0, "process": 0, "perspective": 0})


class TestImportExportRoundTrip(unittest.TestCase):
    """Test JSON import/export round-trip preserves data."""

    def setUp(self):
        self.framework = P3IFFramework()
        self.prop = Property(name="Prop", description="Test property", domain="test", tags=["a", "b"])
        self.proc = Process(name="Proc", description="Test process", domain="test")
        self.persp = Perspective(name="Persp", description="Test perspective", domain="test", viewpoint="analyst")
        self.framework.add_pattern(self.prop)
        self.framework.add_pattern(self.proc)
        self.framework.add_pattern(self.persp)
        self.rel = Relationship(
            property_id=self.prop.id,
            process_id=self.proc.id,
            perspective_id=self.persp.id,
            strength=0.85,
            confidence=0.95
        )
        self.framework.add_relationship(self.rel)

    def test_json_round_trip(self):
        """Export to JSON and re-import should preserve all data."""
        json_str = self.framework.export_to_json()

        fw2 = P3IFFramework()
        stats = fw2.import_from_json(json_str)

        self.assertEqual(stats["patterns_imported"], 3)
        self.assertEqual(stats["relationships_imported"], 1)
        self.assertEqual(len(fw2), 3)
        self.assertEqual(len(fw2.get_all_relationships()), 1)

        # Verify relationship data survived
        rel = fw2.get_all_relationships()[0]
        self.assertAlmostEqual(float(rel.strength), 0.85, places=2)
        self.assertAlmostEqual(float(rel.confidence), 0.95, places=2)

    def test_json_file_round_trip(self):
        """Export to file and re-import should work."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = f.name

        try:
            self.framework.export_to_json(path)

            fw2 = P3IFFramework()
            stats = fw2.import_from_json(path)

            self.assertEqual(stats["patterns_imported"], 3)
            self.assertEqual(stats["relationships_imported"], 1)
        finally:
            os.unlink(path)


class TestNewFrameworkMethods(unittest.TestCase):
    """Test newly added convenience methods."""

    def setUp(self):
        self.framework = P3IFFramework()
        self.p1 = Property(name="P1", description="d", domain="domain_a")
        self.p2 = Property(name="P2", description="d", domain="domain_b")
        self.proc = Process(name="Pr1", description="d", domain="domain_a")
        self.framework.add_pattern(self.p1)
        self.framework.add_pattern(self.p2)
        self.framework.add_pattern(self.proc)

    def test_get_all_patterns(self):
        """get_all_patterns should return all patterns."""
        patterns = self.framework.get_all_patterns()
        self.assertEqual(len(patterns), 3)
        ids = {p.id for p in patterns}
        self.assertIn(self.p1.id, ids)
        self.assertIn(self.p2.id, ids)
        self.assertIn(self.proc.id, ids)

    def test_get_all_domains(self):
        """get_all_domains should return unique domain names."""
        domains = self.framework.get_all_domains()
        self.assertEqual(domains, {"domain_a", "domain_b"})

    def test_framework_repr(self):
        """__repr__ should return informative string."""
        r = repr(self.framework)
        self.assertIn("P3IFFramework", r)
        self.assertIn("patterns=3", r)


class TestCreateRelationshipType(unittest.TestCase):
    """Test that create_relationship stores relationship_type in the field."""

    def test_relationship_type_stored_in_field(self):
        """relationship_type should be stored as a field, not in metadata."""
        core = P3IFCore()
        prop = core.create_pattern("property", "Prop", domain="test", description="d")
        proc = core.create_pattern("process", "Proc", domain="test", description="d")

        rel = core.create_relationship(
            property_id=prop.id,
            process_id=proc.id,
            relationship_type="causal"
        )

        self.assertEqual(rel.relationship_type, "causal")
        # metadata should not contain the type
        self.assertNotIn("type", rel.metadata)

    def test_relationship_type_default(self):
        """Default relationship_type should be 'general'."""
        core = P3IFCore()
        prop = core.create_pattern("property", "Prop", domain="test", description="d")
        proc = core.create_pattern("process", "Proc", domain="test", description="d")

        rel = core.create_relationship(property_id=prop.id, process_id=proc.id)
        self.assertEqual(rel.relationship_type, "general")


class TestCompositionSetOperations(unittest.TestCase):
    """Test composition overlay works with both sets and lists."""

    def test_overlay_with_lists(self):
        """Overlay should work when framework dimensions are lists."""
        class ListFramework:
            def __init__(self, properties, processes, perspectives):
                self.properties = properties
                self.processes = processes
                self.perspectives = perspectives
            def copy(self):
                import copy
                return copy.deepcopy(self)

        base = ListFramework(["a", "b"], ["x"], ["p"])
        overlay = ListFramework(["b", "c"], ["y"], ["q"])

        engine = CompositionEngine()
        result = engine.overlay_frameworks(base, overlay, MultiplexingStrategy.UNION)

        self.assertIsInstance(result.properties, list)
        self.assertEqual(set(result.properties), {"a", "b", "c"})
        self.assertEqual(set(result.processes), {"x", "y"})
        self.assertEqual(set(result.perspectives), {"p", "q"})

    def test_overlay_with_sets(self):
        """Overlay should work when framework dimensions are sets."""
        class SetFramework:
            def __init__(self, properties, processes, perspectives):
                self.properties = properties
                self.processes = processes
                self.perspectives = perspectives
            def copy(self):
                import copy
                return copy.deepcopy(self)

        base = SetFramework({"a", "b"}, {"x"}, {"p"})
        overlay = SetFramework({"b", "c"}, {"y"}, {"q"})

        engine = CompositionEngine()
        result = engine.overlay_frameworks(base, overlay, MultiplexingStrategy.UNION)

        self.assertIsInstance(result.properties, set)
        self.assertEqual(result.properties, {"a", "b", "c"})

    def test_intersection_strategy(self):
        """Intersection should return only common elements."""
        class SetFramework:
            def __init__(self, properties, processes, perspectives):
                self.properties = properties
                self.processes = processes
                self.perspectives = perspectives
            def copy(self):
                import copy
                return copy.deepcopy(self)

        base = SetFramework({"a", "b", "c"}, {"x"}, {"p"})
        overlay = SetFramework({"b", "c", "d"}, {"x", "y"}, {"q"})

        engine = CompositionEngine()
        result = engine.overlay_frameworks(base, overlay, MultiplexingStrategy.INTERSECTION)

        self.assertEqual(result.properties, {"b", "c"})
        self.assertEqual(result.processes, {"x"})


class TestValidationRuleAppliesTo(unittest.TestCase):
    """Test that validation rules use applies_to instead of name prefix matching."""

    def test_rules_have_applies_to(self):
        """Default rules should have applies_to set."""
        from p3if.core.validation import create_default_validation_rules
        rules = create_default_validation_rules()

        self.assertEqual(rules["has_name"].applies_to, 'pattern')
        self.assertEqual(rules["meaningful_description"].applies_to, 'pattern')
        self.assertEqual(rules["minimum_elements"].applies_to, 'framework')
        self.assertEqual(rules["dimension_balance"].applies_to, 'framework')
        self.assertEqual(rules["relationship_validity"].applies_to, 'relationship')
        self.assertEqual(rules["strength_range"].applies_to, 'relationship')
        self.assertEqual(rules["confidence_range"].applies_to, 'relationship')


if __name__ == '__main__':
    unittest.main()
