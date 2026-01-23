"""
Unit tests for P3IF storage utilities.
"""
import pytest
import json
import tempfile
from pathlib import Path


class TestJSONStorage:
    """Test cases for JSONStorage class."""

    def test_json_storage_initialization(self):
        """Test JSONStorage initialization."""
        from p3if.utils.storage import JSONStorage

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            storage = JSONStorage(temp_path)

            assert storage.file_path == temp_path
            assert storage._data == {"patterns": {}, "relationships": {}}
        finally:
            temp_path.unlink(missing_ok=True)

    def test_json_storage_save_pattern(self):
        """Test saving a pattern to JSONStorage."""
        from p3if.utils.storage import JSONStorage
        from p3if.core.models import Property

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            storage = JSONStorage(temp_path)

            pattern = Property(name="Test Pattern", description="Test", domain="test")
            storage.save_pattern(pattern)

            assert pattern.id in storage._data["patterns"]

            # Verify persistence
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)

            assert pattern.id in saved_data["patterns"]
        finally:
            temp_path.unlink(missing_ok=True)

    def test_json_storage_get_pattern(self):
        """Test retrieving a pattern from JSONStorage."""
        from p3if.utils.storage import JSONStorage
        from p3if.core.models import Property

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            storage = JSONStorage(temp_path)

            pattern = Property(name="Test Pattern", description="Test", domain="test")
            storage.save_pattern(pattern)

            retrieved = storage.get_pattern(pattern.id)

            assert retrieved is not None
            assert retrieved.name == pattern.name
        finally:
            temp_path.unlink(missing_ok=True)

    def test_json_storage_get_nonexistent_pattern(self):
        """Test retrieving non-existent pattern returns None."""
        from p3if.utils.storage import JSONStorage

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            storage = JSONStorage(temp_path)

            retrieved = storage.get_pattern("nonexistent_id")
            assert retrieved is None
        finally:
            temp_path.unlink(missing_ok=True)

    def test_json_storage_delete_pattern(self):
        """Test deleting a pattern from JSONStorage."""
        from p3if.utils.storage import JSONStorage
        from p3if.core.models import Property

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            storage = JSONStorage(temp_path)

            pattern = Property(name="Test Pattern", description="Test", domain="test")
            storage.save_pattern(pattern)

            assert storage.delete_pattern(pattern.id) is True
            assert storage.get_pattern(pattern.id) is None

            # Delete non-existent returns False
            assert storage.delete_pattern("nonexistent") is False
        finally:
            temp_path.unlink(missing_ok=True)

    def test_json_storage_patterns_by_type(self):
        """Test getting patterns by type."""
        from p3if.utils.storage import JSONStorage
        from p3if.core.models import Property, Process

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            storage = JSONStorage(temp_path)

            prop1 = Property(name="Prop 1", description="Test", domain="test")
            prop2 = Property(name="Prop 2", description="Test", domain="test")
            proc1 = Process(name="Proc 1", description="Test", domain="test")

            storage.save_pattern(prop1)
            storage.save_pattern(prop2)
            storage.save_pattern(proc1)

            properties = storage.get_patterns_by_type("property")
            processes = storage.get_patterns_by_type("process")

            assert len(properties) == 2
            assert len(processes) == 1
        finally:
            temp_path.unlink(missing_ok=True)

    def test_json_storage_save_relationship(self):
        """Test saving a relationship to JSONStorage."""
        from p3if.utils.storage import JSONStorage
        from p3if.core.models import Property, Process, Relationship

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            storage = JSONStorage(temp_path)

            prop = Property(name="Test Prop", description="Test", domain="test")
            proc = Process(name="Test Proc", description="Test", domain="test")

            storage.save_pattern(prop)
            storage.save_pattern(proc)

            rel = Relationship(property_id=prop.id, process_id=proc.id, strength=0.8, confidence=0.9)
            storage.save_relationship(rel)

            assert rel.id in storage._data["relationships"]
        finally:
            temp_path.unlink(missing_ok=True)

    def test_json_storage_clear(self):
        """Test clearing all data from JSONStorage."""
        from p3if.utils.storage import JSONStorage
        from p3if.core.models import Property

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            storage = JSONStorage(temp_path)

            pattern = Property(name="Test", description="Test", domain="test")
            storage.save_pattern(pattern)

            assert len(storage._data["patterns"]) == 1

            storage.clear()

            assert len(storage._data["patterns"]) == 0
            assert len(storage._data["relationships"]) == 0
        finally:
            temp_path.unlink(missing_ok=True)

    def test_json_storage_loads_existing_file(self):
        """Test that JSONStorage loads data from existing file."""
        from p3if.utils.storage import JSONStorage

        # Create a pre-populated JSON file
        existing_data = {
            "patterns": {
                "test_id": {
                    "id": "test_id",
                    "name": "Existing Pattern",
                    "description": "Test",
                    "type": "property",
                    "domain": "test"
                }
            },
            "relationships": {}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(existing_data, f)
            temp_path = Path(f.name)

        try:
            storage = JSONStorage(temp_path)

            assert "test_id" in storage._data["patterns"]
        finally:
            temp_path.unlink(missing_ok=True)


class TestSQLiteStorage:
    """Test cases for SQLiteStorage class."""

    def test_sqlite_storage_initialization(self):
        """Test SQLiteStorage initialization."""
        from p3if.utils.storage import SQLiteStorage

        with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
            temp_path = Path(f.name)

        try:
            storage = SQLiteStorage(temp_path)

            assert storage.db_path == temp_path
            assert storage.conn is not None
        finally:
            storage.conn.close()
            temp_path.unlink(missing_ok=True)

    def test_sqlite_storage_save_and_get_pattern(self):
        """Test saving and retrieving a pattern from SQLiteStorage."""
        from p3if.utils.storage import SQLiteStorage
        from p3if.core.models import Property

        with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
            temp_path = Path(f.name)

        try:
            storage = SQLiteStorage(temp_path)

            pattern = Property(name="Test Pattern", description="Test", domain="test")
            storage.save_pattern(pattern)

            retrieved = storage.get_pattern(pattern.id)

            assert retrieved is not None
            assert retrieved.name == pattern.name
        finally:
            storage.conn.close()
            temp_path.unlink(missing_ok=True)

    def test_sqlite_storage_delete_pattern(self):
        """Test deleting a pattern from SQLiteStorage."""
        from p3if.utils.storage import SQLiteStorage
        from p3if.core.models import Property

        with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
            temp_path = Path(f.name)

        try:
            storage = SQLiteStorage(temp_path)

            pattern = Property(name="Test", description="Test", domain="test")
            storage.save_pattern(pattern)

            assert storage.delete_pattern(pattern.id) is True
            assert storage.get_pattern(pattern.id) is None
        finally:
            storage.conn.close()
            temp_path.unlink(missing_ok=True)


class TestVisualizationStorage:
    """Test cases for VisualizationStorage class."""

    def test_visualization_storage_initialization(self):
        """Test VisualizationStorage initialization."""
        from p3if.utils.storage import VisualizationStorage

        storage = VisualizationStorage()

        assert storage._visualizations == {}

    def test_visualization_storage_save_and_get_status(self):
        """Test saving and getting visualization status."""
        from p3if.utils.storage import VisualizationStorage

        storage = VisualizationStorage()

        viz_data = {
            "status": "completed",
            "type": "cube_3d",
            "progress": 100
        }

        storage.save_visualization("test_viz_id", viz_data)

        status = storage.get_visualization_status("test_viz_id")

        assert status is not None
        assert status["status"] == "completed"
        assert status["type"] == "cube_3d"

    def test_visualization_storage_get_default_status(self):
        """Test getting default status for unknown visualization ID."""
        from p3if.utils.storage import VisualizationStorage

        storage = VisualizationStorage()

        # Should return default completed status
        status = storage.get_visualization_status("unknown_id")

        assert status is not None
        assert status["status"] == "completed"

    def test_visualization_storage_delete(self):
        """Test deleting a visualization."""
        from p3if.utils.storage import VisualizationStorage

        storage = VisualizationStorage()

        storage.save_visualization("test_id", {"status": "completed"})
        assert "test_id" in storage._visualizations

        result = storage.delete_visualization("test_id")
        assert result is True
        assert "test_id" not in storage._visualizations

        # Delete non-existent returns False
        result = storage.delete_visualization("nonexistent")
        assert result is False

    def test_visualization_storage_list(self):
        """Test listing all visualizations."""
        from p3if.utils.storage import VisualizationStorage

        storage = VisualizationStorage()

        storage.save_visualization("viz1", {"status": "completed"})
        storage.save_visualization("viz2", {"status": "generating"})

        visualizations = storage.list_visualizations()

        assert len(visualizations) == 2
        ids = [v["id"] for v in visualizations]
        assert "viz1" in ids
        assert "viz2" in ids

    def test_visualization_storage_get_files(self):
        """Test getting visualization files."""
        from p3if.utils.storage import VisualizationStorage

        storage = VisualizationStorage()

        # Without stored files, should return default
        files = storage.get_visualization_files("test_id")

        assert len(files) == 2
        assert any("html" in f["type"] for f in files)
        assert any("json" in f["type"] for f in files)

        # With stored files
        storage.save_visualization("test_id", {
            "status": "completed",
            "files": [
                {"url": "/output/custom.html", "type": "html"}
            ]
        })

        files = storage.get_visualization_files("test_id")
        assert len(files) == 1
        assert files[0]["url"] == "/output/custom.html"
