"""
Unit tests for P3IF data importers.
"""
import pytest
import json
import csv
import tempfile
from pathlib import Path


class TestImportFromJSON:
    """Test cases for JSON import functionality."""

    def test_import_from_json_basic(self):
        """Test basic JSON import."""
        from p3if.data.importers import import_from_json

        # Create test JSON data
        test_data = {
            "properties": [
                {"name": "Test Property", "description": "Test description", "domain": "test"}
            ],
            "processes": [
                {"name": "Test Process", "description": "Test description", "domain": "test"}
            ],
            "perspectives": [
                {"name": "Test Perspective", "description": "Test description", "domain": "test", "viewpoint": "test_view"}
            ],
            "relationships": []
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            framework = import_from_json(temp_path)

            assert len(framework._patterns) == 3
        finally:
            temp_path.unlink(missing_ok=True)

    def test_import_from_json_with_relationships(self):
        """Test JSON import with relationships."""
        from p3if.data.importers import import_from_json
        from p3if.core.models import Property, Process

        # First, we need to create patterns with known IDs
        prop = Property(name="Test Property", description="Test", domain="test")
        proc = Process(name="Test Process", description="Test", domain="test")

        # Create test JSON data with the actual IDs
        test_data = {
            "properties": [
                {"id": prop.id, "name": prop.name, "description": prop.description, "domain": prop.domain}
            ],
            "processes": [
                {"id": proc.id, "name": proc.name, "description": proc.description, "domain": proc.domain}
            ],
            "perspectives": [],
            "relationships": [
                {
                    "property_id": prop.id,
                    "process_id": proc.id,
                    "strength": 0.8,
                    "confidence": 0.9
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            framework = import_from_json(temp_path)

            assert len(framework._patterns) == 2
            assert len(framework._relationships) == 1
        finally:
            temp_path.unlink(missing_ok=True)

    def test_import_into_existing_framework(self):
        """Test importing into an existing framework."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property
        from p3if.data.importers import import_from_json

        # Create existing framework with data
        existing_framework = P3IFFramework()
        existing_prop = Property(name="Existing Property", description="Test", domain="test")
        existing_framework.add_pattern(existing_prop)

        # Create test JSON data
        test_data = {
            "properties": [
                {"name": "New Property", "description": "Test", "domain": "test"}
            ],
            "processes": [],
            "perspectives": [],
            "relationships": []
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            framework = import_from_json(temp_path, framework=existing_framework)

            # Should have both patterns
            assert len(framework._patterns) == 2
        finally:
            temp_path.unlink(missing_ok=True)

    def test_import_empty_json(self):
        """Test importing empty JSON file."""
        from p3if.data.importers import import_from_json

        test_data = {
            "properties": [],
            "processes": [],
            "perspectives": [],
            "relationships": []
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            framework = import_from_json(temp_path)

            assert len(framework._patterns) == 0
            assert len(framework._relationships) == 0
        finally:
            temp_path.unlink(missing_ok=True)


class TestImportFromCSV:
    """Test cases for CSV import functionality."""

    def test_import_from_csv_basic(self):
        """Test basic CSV import."""
        from p3if.data.importers import import_from_csv

        # Create patterns CSV
        patterns_data = [
            ['id', 'type', 'name', 'description', 'domain', 'tags'],
            ['p1', 'property', 'Test Property', 'Test description', 'test', 'tag1,tag2'],
            ['p2', 'process', 'Test Process', 'Test description', 'test', 'tag1'],
        ]

        # Create relationships CSV
        relationships_data = [
            ['id', 'property_id', 'process_id', 'perspective_id', 'strength', 'confidence'],
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerows(patterns_data)
            patterns_path = Path(f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerows(relationships_data)
            relationships_path = Path(f.name)

        try:
            framework = import_from_csv(patterns_path, relationships_path)

            assert len(framework._patterns) == 2
        finally:
            patterns_path.unlink(missing_ok=True)
            relationships_path.unlink(missing_ok=True)

    def test_import_from_csv_with_relationships(self):
        """Test CSV import with relationships."""
        from p3if.data.importers import import_from_csv
        from p3if.core.models import Property, Process

        # Create patterns with known IDs
        prop = Property(name="Test Property", description="Test", domain="test")
        proc = Process(name="Test Process", description="Test", domain="test")

        # Create patterns CSV
        patterns_data = [
            ['id', 'type', 'name', 'description', 'domain', 'tags'],
            [prop.id, 'property', prop.name, prop.description, prop.domain, ''],
            [proc.id, 'process', proc.name, proc.description, proc.domain, ''],
        ]

        # Create relationships CSV
        relationships_data = [
            ['id', 'property_id', 'process_id', 'perspective_id', 'strength', 'confidence'],
            ['r1', prop.id, proc.id, '', '0.8', '0.9'],
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerows(patterns_data)
            patterns_path = Path(f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerows(relationships_data)
            relationships_path = Path(f.name)

        try:
            framework = import_from_csv(patterns_path, relationships_path)

            assert len(framework._patterns) == 2
            assert len(framework._relationships) == 1
        finally:
            patterns_path.unlink(missing_ok=True)
            relationships_path.unlink(missing_ok=True)

    def test_import_empty_csv(self):
        """Test importing empty CSV files."""
        from p3if.data.importers import import_from_csv

        # Create empty patterns CSV (header only)
        patterns_data = [
            ['id', 'type', 'name', 'description', 'domain', 'tags'],
        ]

        # Create empty relationships CSV (header only)
        relationships_data = [
            ['id', 'property_id', 'process_id', 'perspective_id', 'strength', 'confidence'],
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerows(patterns_data)
            patterns_path = Path(f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerows(relationships_data)
            relationships_path = Path(f.name)

        try:
            framework = import_from_csv(patterns_path, relationships_path)

            assert len(framework._patterns) == 0
            assert len(framework._relationships) == 0
        finally:
            patterns_path.unlink(missing_ok=True)
            relationships_path.unlink(missing_ok=True)


class TestImportExportRoundTrip:
    """Test cases for import/export round-trip consistency."""

    def test_json_round_trip(self):
        """Test that JSON export then import preserves data."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process, Relationship
        from p3if.data.exporters import export_to_json
        from p3if.data.importers import import_from_json

        # Create original framework
        original = P3IFFramework()
        prop = Property(name="Round Trip Property", description="Test", domain="test")
        proc = Process(name="Round Trip Process", description="Test", domain="test")

        original.add_pattern(prop)
        original.add_pattern(proc)

        rel = Relationship(property_id=prop.id, process_id=proc.id, strength=0.75, confidence=0.85)
        original.add_relationship(rel)

        # Export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            export_to_json(original, temp_path)

            # Import
            imported = import_from_json(temp_path)

            # Verify
            assert len(imported._patterns) == len(original._patterns)
            assert len(imported._relationships) == len(original._relationships)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_csv_round_trip(self):
        """Test that CSV export then import preserves data."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process, Relationship
        from p3if.data.exporters import export_to_csv
        from p3if.data.importers import import_from_csv

        # Create original framework
        original = P3IFFramework()
        prop = Property(name="Round Trip Property", description="Test", domain="test")
        proc = Process(name="Round Trip Process", description="Test", domain="test")

        original.add_pattern(prop)
        original.add_pattern(proc)

        rel = Relationship(property_id=prop.id, process_id=proc.id, strength=0.75, confidence=0.85)
        original.add_relationship(rel)

        # Export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            patterns_path = Path(f.name)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            rels_path = Path(f.name)

        try:
            export_to_csv(original, patterns_path, rels_path)

            # Import
            imported = import_from_csv(patterns_path, rels_path)

            # Verify
            assert len(imported._patterns) == len(original._patterns)
            assert len(imported._relationships) == len(original._relationships)
        finally:
            patterns_path.unlink(missing_ok=True)
            rels_path.unlink(missing_ok=True)
