"""
Tests for P3IF core models.

This module contains tests for the core data models in the P3IF framework.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from p3if.core.models import Pattern, Property, Process, Perspective, Relationship


class TestPattern:
    """Tests for the Pattern base class."""
    
    def test_pattern_creation(self):
        """Test creating a valid Pattern instance."""
        pattern = Pattern(name="Test Pattern", type="test")
        assert pattern.name == "Test Pattern"
        assert pattern.type == "test"
        assert pattern.id is not None
        assert isinstance(pattern.created_at, datetime)
        assert pattern.tags == []
        assert pattern.metadata == {}
    
    def test_pattern_validation(self):
        """Test validation on Pattern creation."""
        # Missing required field
        with pytest.raises(ValidationError):
            Pattern(type="test")
        
        # Invalid fields
        with pytest.raises(ValidationError):
            Pattern(name="Test", type="test", tags="not-a-list")


class TestProperty:
    """Tests for the Property class."""
    
    def test_property_creation(self):
        """Test creating a valid Property instance."""
        prop = Property(name="Test Property")
        assert prop.name == "Test Property"
        assert prop.type == "property"
        assert prop.domain is None
    
    def test_property_with_domain(self):
        """Test creating a Property with a domain."""
        prop = Property(name="Test Property", domain="test-domain")
        assert prop.domain == "test-domain"


class TestProcess:
    """Tests for the Process class."""
    
    def test_process_creation(self):
        """Test creating a valid Process instance."""
        proc = Process(name="Test Process")
        assert proc.name == "Test Process"
        assert proc.type == "process"
        assert proc.domain is None
    
    def test_process_with_domain(self):
        """Test creating a Process with a domain."""
        proc = Process(name="Test Process", domain="test-domain")
        assert proc.domain == "test-domain"


class TestPerspective:
    """Tests for the Perspective class."""
    
    def test_perspective_creation(self):
        """Test creating a valid Perspective instance."""
        persp = Perspective(name="Test Perspective")
        assert persp.name == "Test Perspective"
        assert persp.type == "perspective"
        assert persp.domain is None
    
    def test_perspective_with_domain(self):
        """Test creating a Perspective with a domain."""
        persp = Perspective(name="Test Perspective", domain="test-domain")
        assert persp.domain == "test-domain"


class TestRelationship:
    """Tests for the Relationship class."""
    
    def test_relationship_creation(self):
        """Test creating a valid Relationship instance."""
        rel = Relationship(
            property_id="prop-1",
            process_id="proc-1",
            perspective_id="persp-1",
            strength=0.8,
            confidence=0.9
        )
        assert rel.property_id == "prop-1"
        assert rel.process_id == "proc-1"
        assert rel.perspective_id == "persp-1"
        assert rel.strength == 0.8
        assert rel.confidence == 0.9
        assert rel.bidirectional is True
        assert rel.id is not None
    
    def test_strength_validation(self):
        """Test strength value validation."""
        # Valid values
        Relationship(property_id="prop-1", strength=0.0)
        Relationship(property_id="prop-1", strength=1.0)
        Relationship(property_id="prop-1", strength=0.5)
        
        # Invalid values
        with pytest.raises(ValidationError):
            Relationship(property_id="prop-1", strength=-0.1)
        
        with pytest.raises(ValidationError):
            Relationship(property_id="prop-1", strength=1.1)
    
    def test_confidence_validation(self):
        """Test confidence value validation."""
        # Valid values
        Relationship(property_id="prop-1", strength=0.5, confidence=0.0)
        Relationship(property_id="prop-1", strength=0.5, confidence=1.0)
        
        # Should default to 1.0
        rel = Relationship(property_id="prop-1", strength=0.5)
        assert rel.confidence == 1.0
        
        # Invalid values
        with pytest.raises(ValidationError):
            Relationship(property_id="prop-1", strength=0.5, confidence=-0.1)
        
        with pytest.raises(ValidationError):
            Relationship(property_id="prop-1", strength=0.5, confidence=1.1) 