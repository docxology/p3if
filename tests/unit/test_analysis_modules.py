"""
Tests for analysis modules: BasicAnalyzer, NetworkAnalyzer, AnalysisReport.
"""

import unittest
import json
import os
import tempfile

from p3if.core.framework import P3IFFramework, FrameworkBuilder
from p3if.core.models import Property, Process, Perspective, Relationship
from p3if.core.analysis.basic import BasicAnalyzer
from p3if.core.analysis.report import AnalysisReport


class TestBasicAnalyzer(unittest.TestCase):
    """Test BasicAnalyzer functionality."""

    def setUp(self):
        self.framework = FrameworkBuilder() \
            .add_property(name="Security", description="Security property", domain="cybersec") \
            .add_property(name="Privacy", description="Privacy property", domain="cybersec") \
            .add_process(name="Auth", description="Authentication process", domain="cybersec") \
            .add_process(name="Encrypt", description="Encryption process", domain="cybersec") \
            .add_perspective(name="Technical", description="Technical perspective", domain="cybersec", viewpoint="dev") \
            .add_perspective(name="Business", description="Business perspective", domain="cybersec", viewpoint="biz") \
            .build()

        # Add relationships
        patterns = {
            "property": self.framework.get_patterns_by_type("property"),
            "process": self.framework.get_patterns_by_type("process"),
            "perspective": self.framework.get_patterns_by_type("perspective"),
        }
        self.framework.add_relationship(Relationship(
            property_id=patterns["property"][0].id,
            process_id=patterns["process"][0].id,
            strength=0.9, confidence=0.95
        ))
        self.framework.add_relationship(Relationship(
            property_id=patterns["property"][1].id,
            process_id=patterns["process"][1].id,
            perspective_id=patterns["perspective"][0].id,
            strength=0.7, confidence=0.8
        ))

        self.analyzer = BasicAnalyzer(self.framework)

    def test_pattern_distribution(self):
        dist = self.analyzer.get_pattern_distribution()
        self.assertEqual(dist["property"], 2)
        self.assertEqual(dist["process"], 2)
        self.assertEqual(dist["perspective"], 2)

    def test_relationship_strength_stats(self):
        stats = self.analyzer.get_relationship_strength_statistics()
        self.assertIn("min", stats)
        self.assertIn("max", stats)
        self.assertIn("mean", stats)
        self.assertIn("median", stats)
        self.assertIn("std", stats)
        self.assertAlmostEqual(stats["min"], 0.7, places=1)
        self.assertAlmostEqual(stats["max"], 0.9, places=1)

    def test_strongest_relationships(self):
        strongest = self.analyzer.get_strongest_relationships(top_n=5)
        self.assertGreater(len(strongest), 0)
        self.assertIn("strength", strongest[0])
        self.assertIn("patterns", strongest[0])

    def test_tag_distribution(self):
        tags = self.analyzer.get_tag_distribution()
        self.assertIsInstance(tags, dict)

    def test_pattern_activity(self):
        activity = self.analyzer.get_pattern_activity()
        self.assertIn("property", activity)
        self.assertIn("process", activity)
        self.assertIn("perspective", activity)

    def test_most_connected_patterns(self):
        connected = self.analyzer.get_most_connected_patterns(top_n=3)
        self.assertIn("property", connected)
        self.assertIn("process", connected)
        self.assertIn("perspective", connected)

    def test_full_analysis(self):
        result = self.analyzer.run_full_analysis()
        self.assertIn("pattern_distribution", result)
        self.assertIn("relationship_strength_stats", result)
        self.assertIn("strongest_relationships", result)
        self.assertIn("tag_distribution", result)
        self.assertIn("most_connected_patterns", result)
        self.assertIn("property_similarity", result)


class TestAnalysisReport(unittest.TestCase):
    """Test AnalysisReport functionality."""

    def setUp(self):
        self.framework = FrameworkBuilder() \
            .add_property(name="P1", description="Property 1", domain="test") \
            .add_process(name="Pr1", description="Process 1", domain="test") \
            .add_perspective(name="Pe1", description="Perspective 1", domain="test", viewpoint="analyst") \
            .build()

        patterns = {
            "property": self.framework.get_patterns_by_type("property"),
            "process": self.framework.get_patterns_by_type("process"),
            "perspective": self.framework.get_patterns_by_type("perspective"),
        }
        self.framework.add_relationship(Relationship(
            property_id=patterns["property"][0].id,
            process_id=patterns["process"][0].id,
            strength=0.8, confidence=0.9
        ))

        self.report = AnalysisReport(self.framework)

    def test_run_basic_analysis(self):
        result = self.report.run_analysis(include_basic=True, include_network=False, include_meta=False)
        self.assertIn("timestamp", result)
        self.assertIn("summary", result)
        self.assertIn("basic", result)

    def test_full_report(self):
        result = self.report.run_analysis(include_basic=True, include_network=True, include_meta=True)
        self.assertIn("timestamp", result)
        self.assertIn("basic", result)

    def test_network_summary_with_params(self):
        result = self.report.run_analysis(include_basic=False, include_network=True, include_meta=False)
        summary = self.report.get_network_summary(top_n_nodes=3, top_n_communities=2)
        self.assertIn("top_central_nodes", summary)

    def test_get_top_patterns(self):
        result = self.report.get_top_patterns(top_n=5)
        self.assertIn("most_connected", result)
        self.assertIn("strongest_relationships", result)

    def test_report_repr(self):
        r = repr(self.report)
        self.assertIn("AnalysisReport", r)


if __name__ == '__main__':
    unittest.main()
