"""
Unit tests for P3IF data exporters.
"""
import pytest
import json
import tempfile
from pathlib import Path


class TestDataExporter:
    """Test cases for the DataExporter class."""

    def test_exporter_initialization(self):
        """Test DataExporter initialization."""
        from p3if.core.framework import P3IFFramework
        from p3if.data.exporters import DataExporter

        framework = P3IFFramework()
        exporter = DataExporter(framework)

        assert exporter.framework is framework

    def test_export_to_json(self):
        """Test exporting framework data to JSON."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process, Relationship
        from p3if.data.exporters import DataExporter

        framework = P3IFFramework()

        # Add test data
        prop = Property(name="Test Property", description="Test description", domain="test")
        proc = Process(name="Test Process", description="Test description", domain="test")

        framework.add_pattern(prop)
        framework.add_pattern(proc)

        rel = Relationship(property_id=prop.id, process_id=proc.id, strength=0.8, confidence=0.9)
        framework.add_relationship(rel)

        # Export to JSON
        exporter = DataExporter(framework)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)

        try:
            result_path = exporter.export_to_json(output_path)

            assert result_path.exists()

            # Verify JSON content
            with open(result_path, 'r') as f:
                data = json.load(f)

            assert 'properties' in data
            assert 'processes' in data
            assert 'relationships' in data
        finally:
            output_path.unlink(missing_ok=True)

    def test_export_to_csv(self):
        """Test exporting framework data to CSV."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process, Relationship
        from p3if.data.exporters import DataExporter

        framework = P3IFFramework()

        # Add test data
        prop = Property(name="Test Property", description="Test description", domain="test")
        proc = Process(name="Test Process", description="Test description", domain="test")

        framework.add_pattern(prop)
        framework.add_pattern(proc)

        rel = Relationship(property_id=prop.id, process_id=proc.id, strength=0.8, confidence=0.9)
        framework.add_relationship(rel)

        # Export to CSV
        exporter = DataExporter(framework)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            patterns_path = Path(f.name)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            rels_path = Path(f.name)

        try:
            result = exporter.export_to_csv(patterns_path, rels_path)

            assert 'patterns' in result
            assert 'relationships' in result
            assert result['patterns'].exists()
            assert result['relationships'].exists()

            # Verify patterns CSV has header
            with open(result['patterns'], 'r') as f:
                header = f.readline()
                assert 'id' in header
                assert 'name' in header
        finally:
            patterns_path.unlink(missing_ok=True)
            rels_path.unlink(missing_ok=True)

    def test_export_to_graphml(self):
        """Test exporting framework data to GraphML."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process, Relationship
        from p3if.data.exporters import DataExporter

        framework = P3IFFramework()

        # Add test data
        prop = Property(name="Test Property", description="Test description", domain="test")
        proc = Process(name="Test Process", description="Test description", domain="test")

        framework.add_pattern(prop)
        framework.add_pattern(proc)

        rel = Relationship(property_id=prop.id, process_id=proc.id, strength=0.8, confidence=0.9)
        framework.add_relationship(rel)

        # Export to GraphML
        exporter = DataExporter(framework)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
            output_path = Path(f.name)

        try:
            result_path = exporter.export_to_graphml(output_path)

            assert result_path.exists()

            # Verify GraphML content
            with open(result_path, 'r') as f:
                content = f.read()

            assert 'graphml' in content.lower()
            assert 'node' in content.lower()
        finally:
            output_path.unlink(missing_ok=True)


class TestExportFunctions:
    """Test cases for standalone export functions."""

    def test_export_to_json_function(self):
        """Test the export_to_json standalone function."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property
        from p3if.data.exporters import export_to_json

        framework = P3IFFramework()
        prop = Property(name="Test", description="Test", domain="test")
        framework.add_pattern(prop)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)

        try:
            result = export_to_json(framework, output_path)
            assert result.exists()
        finally:
            output_path.unlink(missing_ok=True)

    def test_export_to_csv_function(self):
        """Test the export_to_csv standalone function."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property
        from p3if.data.exporters import export_to_csv

        framework = P3IFFramework()
        prop = Property(name="Test", description="Test", domain="test")
        framework.add_pattern(prop)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            patterns_path = Path(f.name)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            rels_path = Path(f.name)

        try:
            result = export_to_csv(framework, patterns_path, rels_path)
            assert result['patterns'].exists()
            assert result['relationships'].exists()
        finally:
            patterns_path.unlink(missing_ok=True)
            rels_path.unlink(missing_ok=True)

    def test_export_to_graphml_function(self):
        """Test the export_to_graphml standalone function."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property
        from p3if.data.exporters import export_to_graphml

        framework = P3IFFramework()
        prop = Property(name="Test", description="Test", domain="test")
        framework.add_pattern(prop)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
            output_path = Path(f.name)

        try:
            result = export_to_graphml(framework, output_path)
            assert result.exists()
        finally:
            output_path.unlink(missing_ok=True)


class TestExportEmptyFramework:
    """Test cases for exporting empty frameworks."""

    def test_export_empty_framework_json(self):
        """Test exporting empty framework to JSON."""
        from p3if.core.framework import P3IFFramework
        from p3if.data.exporters import export_to_json

        framework = P3IFFramework()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)

        try:
            result = export_to_json(framework, output_path)

            with open(result, 'r') as f:
                data = json.load(f)

            assert data['properties'] == []
            assert data['processes'] == []
            assert data['perspectives'] == []
            assert data['relationships'] == []
        finally:
            output_path.unlink(missing_ok=True)

    def test_export_empty_framework_csv(self):
        """Test exporting empty framework to CSV."""
        from p3if.core.framework import P3IFFramework
        from p3if.data.exporters import export_to_csv

        framework = P3IFFramework()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            patterns_path = Path(f.name)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            rels_path = Path(f.name)

        try:
            result = export_to_csv(framework, patterns_path, rels_path)

            # Should have header but no data rows
            with open(result['patterns'], 'r') as f:
                lines = f.readlines()
                assert len(lines) == 1  # Just header
        finally:
            patterns_path.unlink(missing_ok=True)
            rels_path.unlink(missing_ok=True)
