"""
Unit tests for P3IF basic analysis functionality.
"""
import pytest
from typing import Dict, List, Any


class TestBasicMetrics:
    """Test cases for basic framework metrics."""

    def test_pattern_count_metrics(self):
        """Test pattern counting metrics."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process, Perspective

        framework = P3IFFramework()

        # Add patterns
        prop = Property(name="Test Prop", description="Test", domain="test")
        proc = Process(name="Test Proc", description="Test", domain="test")
        persp = Perspective(name="Test Persp", description="Test", domain="test", viewpoint="view")

        framework.add_pattern(prop)
        framework.add_pattern(proc)
        framework.add_pattern(persp)

        # Get metrics
        metrics = framework.get_metrics()

        assert metrics.total_patterns == 3

    def test_relationship_count_metrics(self):
        """Test relationship counting metrics."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process, Relationship

        framework = P3IFFramework()

        # Add patterns
        prop = Property(name="Test Prop", description="Test", domain="test")
        proc = Process(name="Test Proc", description="Test", domain="test")

        framework.add_pattern(prop)
        framework.add_pattern(proc)

        # Add relationship
        rel = Relationship(
            property_id=prop.id,
            process_id=proc.id,
            strength=0.8,
            confidence=0.9
        )
        framework.add_relationship(rel)

        metrics = framework.get_metrics()
        assert metrics.total_relationships == 1

    def test_average_strength_calculation(self):
        """Test average relationship strength calculation."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process, Perspective, Relationship

        framework = P3IFFramework()

        # Add patterns
        prop1 = Property(name="Prop 1", description="Test", domain="test")
        prop2 = Property(name="Prop 2", description="Test", domain="test")
        proc = Process(name="Proc", description="Test", domain="test")
        persp = Perspective(name="Persp", description="Test", domain="test", viewpoint="view")

        framework.add_pattern(prop1)
        framework.add_pattern(prop2)
        framework.add_pattern(proc)
        framework.add_pattern(persp)

        # Add relationships with known strengths
        rel1 = Relationship(property_id=prop1.id, process_id=proc.id, strength=0.6, confidence=0.9)
        rel2 = Relationship(property_id=prop2.id, process_id=proc.id, strength=0.8, confidence=0.9)

        framework.add_relationship(rel1)
        framework.add_relationship(rel2)

        metrics = framework.get_metrics()

        # Average should be (0.6 + 0.8) / 2 = 0.7
        assert abs(metrics.average_relationship_strength - 0.7) < 0.01


class TestDomainAnalysis:
    """Test cases for domain-level analysis."""

    def test_domain_pattern_grouping(self):
        """Test grouping patterns by domain."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process

        framework = P3IFFramework()

        # Add patterns in different domains
        prop1 = Property(name="Domain A Prop", description="Test", domain="domain_a")
        prop2 = Property(name="Domain B Prop", description="Test", domain="domain_b")
        proc1 = Process(name="Domain A Proc", description="Test", domain="domain_a")

        framework.add_pattern(prop1)
        framework.add_pattern(prop2)
        framework.add_pattern(proc1)

        # Get patterns by domain
        domain_a_patterns = framework.get_patterns_by_domain("domain_a")
        domain_b_patterns = framework.get_patterns_by_domain("domain_b")

        assert len(domain_a_patterns) == 2
        assert len(domain_b_patterns) == 1

    def test_domain_count(self):
        """Test counting unique domains."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property

        framework = P3IFFramework()

        # Add patterns in different domains
        domains = ['healthcare', 'finance', 'technology', 'healthcare']
        for i, domain in enumerate(domains):
            prop = Property(name=f"Prop {i}", description="Test", domain=domain)
            framework.add_pattern(prop)

        metrics = framework.get_metrics()
        # Should have 3 unique domains
        assert metrics.domain_count == 3


class TestPatternTypeAnalysis:
    """Test cases for pattern type analysis."""

    def test_pattern_type_counting(self):
        """Test counting patterns by type."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process, Perspective

        framework = P3IFFramework()

        # Add various patterns
        framework.add_pattern(Property(name="P1", description="Test", domain="test"))
        framework.add_pattern(Property(name="P2", description="Test", domain="test"))
        framework.add_pattern(Process(name="Proc1", description="Test", domain="test"))
        framework.add_pattern(Perspective(name="Persp1", description="Test", domain="test", viewpoint="v"))

        # Get patterns by type
        properties = framework.get_patterns_by_type("property")
        processes = framework.get_patterns_by_type("process")
        perspectives = framework.get_patterns_by_type("perspective")

        assert len(properties) == 2
        assert len(processes) == 1
        assert len(perspectives) == 1

    def test_pattern_search(self):
        """Test pattern search functionality."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property

        framework = P3IFFramework()

        # Add patterns with specific names
        framework.add_pattern(Property(name="Security Policy", description="Test", domain="test"))
        framework.add_pattern(Property(name="Privacy Policy", description="Test", domain="test"))
        framework.add_pattern(Property(name="Access Control", description="Test", domain="test"))

        # Search for "Policy"
        results = framework.search_patterns("Policy")

        assert len(results) == 2


class TestRelationshipAnalysis:
    """Test cases for relationship analysis."""

    def test_relationship_strength_filtering(self):
        """Test filtering relationships by strength."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process, Relationship

        framework = P3IFFramework()

        # Add patterns
        props = [Property(name=f"P{i}", description="Test", domain="test") for i in range(3)]
        proc = Process(name="Proc", description="Test", domain="test")

        for prop in props:
            framework.add_pattern(prop)
        framework.add_pattern(proc)

        # Add relationships with different strengths
        strengths = [0.3, 0.6, 0.9]
        for prop, strength in zip(props, strengths):
            rel = Relationship(property_id=prop.id, process_id=proc.id, strength=strength, confidence=0.9)
            framework.add_relationship(rel)

        # Get all relationships and filter by strength
        all_rels = list(framework._relationships.values())
        strong_rels = [r for r in all_rels if r.strength >= 0.5]

        assert len(all_rels) == 3
        assert len(strong_rels) == 2

    def test_relationship_by_pattern(self):
        """Test getting relationships for a specific pattern."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process, Perspective, Relationship

        framework = P3IFFramework()

        # Add patterns
        prop = Property(name="Prop", description="Test", domain="test")
        proc1 = Process(name="Proc1", description="Test", domain="test")
        proc2 = Process(name="Proc2", description="Test", domain="test")

        framework.add_pattern(prop)
        framework.add_pattern(proc1)
        framework.add_pattern(proc2)

        # Add relationships
        rel1 = Relationship(property_id=prop.id, process_id=proc1.id, strength=0.8, confidence=0.9)
        rel2 = Relationship(property_id=prop.id, process_id=proc2.id, strength=0.7, confidence=0.9)

        framework.add_relationship(rel1)
        framework.add_relationship(rel2)

        # Get relationships for property
        prop_rels = framework.get_relationships_by_pattern(prop.id)

        assert len(prop_rels) == 2


class TestFrameworkValidation:
    """Test cases for framework validation."""

    def test_validate_empty_framework(self):
        """Test validation of empty framework."""
        from p3if.core.framework import P3IFFramework

        framework = P3IFFramework()
        result = framework.validate_framework()

        assert 'valid' in result or 'is_valid' in result

    def test_validate_populated_framework(self):
        """Test validation of populated framework."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process, Relationship

        framework = P3IFFramework()

        # Add patterns
        prop = Property(name="Test Prop", description="Test", domain="test")
        proc = Process(name="Test Proc", description="Test", domain="test")

        framework.add_pattern(prop)
        framework.add_pattern(proc)

        # Add valid relationship
        rel = Relationship(property_id=prop.id, process_id=proc.id, strength=0.8, confidence=0.9)
        framework.add_relationship(rel)

        result = framework.validate_framework()

        # Should be valid
        is_valid = result.get('valid', result.get('is_valid', True))
        assert is_valid is True
