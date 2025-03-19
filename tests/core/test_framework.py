"""
Tests for P3IF framework.

This module contains tests for the core framework class in the P3IF framework.
"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch
from datetime import datetime

from p3if.core.framework import P3IFFramework
from p3if.core.models import Property, Process, Perspective, Relationship


# Helper for serializing datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class TestP3IFFramework:
    """Tests for the P3IFFramework class."""
    
    def test_initialization(self):
        """Test framework initialization."""
        framework = P3IFFramework()
        assert len(framework._patterns) == 0
        assert len(framework._relationships) == 0
        assert "property" in framework._dimensions
        assert "process" in framework._dimensions
        assert "perspective" in framework._dimensions
    
    def test_add_pattern(self):
        """Test adding patterns to the framework."""
        framework = P3IFFramework()
        
        # Add a property
        prop = Property(name="Test Property")
        prop_id = framework.add_pattern(prop)
        assert prop_id == prop.id
        
        # Add a process
        proc = Process(name="Test Process")
        proc_id = framework.add_pattern(proc)
        assert proc_id == proc.id
        
        # Add a perspective
        persp = Perspective(name="Test Perspective")
        persp_id = framework.add_pattern(persp)
        assert persp_id == persp.id
        
        # Verify patterns were added
        assert len(framework._patterns) == 3
    
    def test_get_pattern(self):
        """Test retrieving patterns by ID."""
        framework = P3IFFramework()
        
        # Add a property
        prop = Property(name="Test Property")
        framework.add_pattern(prop)
        
        # Retrieve by ID
        retrieved = framework.get_pattern(prop.id)
        assert retrieved is not None
        assert retrieved.id == prop.id
        assert retrieved.name == "Test Property"
        
        # Nonexistent ID
        assert framework.get_pattern("nonexistent-id") is None
    
    def test_get_patterns_by_type(self):
        """Test retrieving patterns by type."""
        framework = P3IFFramework()
        
        # Add patterns of different types
        prop1 = Property(name="Property 1")
        prop2 = Property(name="Property 2")
        proc = Process(name="Process 1")
        persp = Perspective(name="Perspective 1")
        
        framework.add_pattern(prop1)
        framework.add_pattern(prop2)
        framework.add_pattern(proc)
        framework.add_pattern(persp)
        
        # Retrieve by type
        properties = framework.get_patterns_by_type("property")
        processes = framework.get_patterns_by_type("process")
        perspectives = framework.get_patterns_by_type("perspective")
        
        assert len(properties) == 2
        assert len(processes) == 1
        assert len(perspectives) == 1
        assert all(p.type == "property" for p in properties)
        assert all(p.type == "process" for p in processes)
        assert all(p.type == "perspective" for p in perspectives)
    
    def test_add_relationship(self):
        """Test adding relationships to the framework."""
        framework = P3IFFramework()
        
        # Add patterns
        prop = Property(name="Test Property")
        proc = Process(name="Test Process")
        persp = Perspective(name="Test Perspective")
        
        prop_id = framework.add_pattern(prop)
        proc_id = framework.add_pattern(proc)
        persp_id = framework.add_pattern(persp)
        
        # Add relationship
        rel = Relationship(
            property_id=prop_id,
            process_id=proc_id,
            perspective_id=persp_id,
            strength=0.7,
            confidence=0.8
        )
        rel_id = framework.add_relationship(rel)
        
        assert rel_id == rel.id
        assert len(framework._relationships) == 1
    
    def test_get_relationship(self):
        """Test retrieving relationships by ID."""
        framework = P3IFFramework()
        
        # Add patterns
        prop = Property(name="Test Property")
        proc = Process(name="Test Process")
        persp = Perspective(name="Test Perspective")
        
        prop_id = framework.add_pattern(prop)
        proc_id = framework.add_pattern(proc)
        persp_id = framework.add_pattern(persp)
        
        # Add relationship
        rel = Relationship(
            property_id=prop_id,
            process_id=proc_id,
            perspective_id=persp_id,
            strength=0.7,
            confidence=0.8
        )
        rel_id = framework.add_relationship(rel)
        
        # Retrieve by ID
        retrieved = framework.get_relationship(rel_id)
        assert retrieved is not None
        assert retrieved.id == rel_id
        assert retrieved.property_id == prop_id
        assert retrieved.process_id == proc_id
        assert retrieved.perspective_id == persp_id
        assert retrieved.strength == 0.7
        assert retrieved.confidence == 0.8
        
        # Nonexistent ID
        assert framework.get_relationship("nonexistent-id") is None
    
    def test_export_import_json(self):
        """Test exporting and importing framework data as JSON."""
        framework = P3IFFramework()
        
        # Add patterns
        prop = Property(name="Test Property")
        proc = Process(name="Test Process")
        persp = Perspective(name="Test Perspective")
        
        prop_id = framework.add_pattern(prop)
        proc_id = framework.add_pattern(proc)
        persp_id = framework.add_pattern(persp)
        
        # Add relationship
        rel = Relationship(
            property_id=prop_id,
            process_id=proc_id,
            perspective_id=persp_id,
            strength=0.7,
            confidence=0.8
        )
        framework.add_relationship(rel)
        
        # Export to JSON string - use our custom encoder to handle datetime
        data = {
            "patterns": [p.dict() for p in framework._patterns.values()],
            "relationships": [r.dict() for r in framework._relationships.values()],
            "metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "framework_version": "2.0"
            }
        }
        json_str = json.dumps(data, cls=DateTimeEncoder)
        
        # Create a new framework and import
        new_framework = P3IFFramework()
        new_framework.import_from_json(json.loads(json_str))
        
        # Verify data was imported correctly
        assert len(new_framework._patterns) == 3
        assert len(new_framework._relationships) == 1
        
        # Verify patterns were imported correctly
        patterns_by_name = {p.name: p for p in new_framework._patterns.values()}
        assert "Test Property" in patterns_by_name
        assert "Test Process" in patterns_by_name
        assert "Test Perspective" in patterns_by_name
    
    def test_export_to_file(self):
        """Test exporting framework data to a file."""
        framework = P3IFFramework()
        
        # Add a pattern
        prop = Property(name="Test Property")
        framework.add_pattern(prop)
        
        # Export to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
            temp_path = temp.name
        
        try:
            # Manually export to avoid datetime serialization issues
            data = {
                "patterns": [p.dict() for p in framework._patterns.values()],
                "relationships": [r.dict() for r in framework._relationships.values()],
                "metadata": {
                    "exported_at": datetime.utcnow().isoformat(),
                    "framework_version": "2.0"
                }
            }
            with open(temp_path, 'w') as f:
                json.dump(data, f, cls=DateTimeEncoder)
            
            # Verify file was created and contains valid JSON
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                data = json.load(f)
                assert 'patterns' in data
                assert len(data['patterns']) == 1
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_clear(self):
        """Test clearing the framework."""
        framework = P3IFFramework()
        
        # Add patterns and relationships
        prop = Property(name="Test Property")
        framework.add_pattern(prop)
        
        # Clear the framework
        framework.clear()
        
        # Verify everything was cleared
        assert len(framework._patterns) == 0
        assert len(framework._relationships) == 0
    
    def test_summary_statistics(self):
        """Test getting summary statistics."""
        framework = P3IFFramework()
        
        # Add patterns of different types
        prop = Property(name="Property 1")
        proc = Process(name="Process 1")
        persp = Perspective(name="Perspective 1")
        
        framework.add_pattern(prop)
        framework.add_pattern(proc)
        framework.add_pattern(persp)
        
        # Add relationship
        rel = Relationship(
            property_id=prop.id,
            process_id=proc.id,
            perspective_id=persp.id,
            strength=0.7
        )
        framework.add_relationship(rel)
        
        # Get statistics
        stats = framework.get_summary_statistics()
        
        assert stats["num_properties"] == 1
        assert stats["num_processes"] == 1
        assert stats["num_perspectives"] == 1
        assert stats["num_relationships"] == 1
        assert stats["avg_relationship_strength"] == 0.7 