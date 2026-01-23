"""
Unit tests for P3IF configuration utilities.
"""
import pytest
import json
import tempfile
from pathlib import Path


class TestConfig:
    """Test cases for the Config class."""

    def test_config_initialization_default(self):
        """Test Config initialization with default values."""
        from p3if.utils.config import Config

        config = Config()

        assert config.get('storage.type') == 'json'
        assert config.get('logging.level') == 'INFO'

    def test_config_get_with_dot_notation(self):
        """Test getting config values using dot notation."""
        from p3if.utils.config import Config

        config = Config()

        # Test nested access
        assert config.get('visualization.default_style') == 'modern'
        assert config.get('visualization.themes.modern.colormap') == 'viridis'

    def test_config_get_default_value(self):
        """Test getting config with default value for missing keys."""
        from p3if.utils.config import Config

        config = Config()

        # Test missing key with default
        result = config.get('nonexistent.key', 'default_value')
        assert result == 'default_value'

        # Test missing key without default
        result = config.get('nonexistent.key')
        assert result is None

    def test_config_set_value(self):
        """Test setting config values."""
        from p3if.utils.config import Config

        config = Config()

        # Set a new value
        config.set('new.nested.key', 'test_value')
        assert config.get('new.nested.key') == 'test_value'

        # Override existing value
        config.set('storage.type', 'sqlite')
        assert config.get('storage.type') == 'sqlite'

    def test_config_get_all(self):
        """Test getting entire configuration."""
        from p3if.utils.config import Config

        config = Config()

        all_config = config.get_all()

        assert isinstance(all_config, dict)
        assert 'storage' in all_config
        assert 'logging' in all_config
        assert 'visualization' in all_config

    def test_config_load_from_file(self):
        """Test loading configuration from file."""
        from p3if.utils.config import Config

        # Create a test config file
        test_config = {
            "storage": {
                "type": "sqlite",
                "path": "test.db"
            },
            "custom": {
                "setting": "value"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            temp_path = Path(f.name)

        try:
            config = Config(config_file=temp_path)

            # Verify loaded values override defaults
            assert config.get('storage.type') == 'sqlite'
            assert config.get('storage.path') == 'test.db'

            # Verify custom values are added
            assert config.get('custom.setting') == 'value'

            # Verify defaults are preserved for non-overridden values
            assert config.get('logging.level') == 'INFO'
        finally:
            temp_path.unlink(missing_ok=True)

    def test_config_save_to_file(self):
        """Test saving configuration to file."""
        from p3if.utils.config import Config

        config = Config()
        config.set('test.value', 'saved')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            config.save_to_file(temp_path)

            # Verify file exists and contains correct data
            with open(temp_path, 'r') as f:
                saved_config = json.load(f)

            assert saved_config['test']['value'] == 'saved'
        finally:
            temp_path.unlink(missing_ok=True)

    def test_config_merge_nested_dicts(self):
        """Test that nested dictionaries are properly merged."""
        from p3if.utils.config import Config

        # Create config with partial override
        test_config = {
            "visualization": {
                "themes": {
                    "modern": {
                        "colormap": "plasma"  # Override only colormap
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            temp_path = Path(f.name)

        try:
            config = Config(config_file=temp_path)

            # Verify overridden value
            assert config.get('visualization.themes.modern.colormap') == 'plasma'

            # Verify non-overridden values are preserved
            assert config.get('visualization.themes.modern.node_size') == 50
            assert config.get('visualization.themes.classic.colormap') == 'coolwarm'
        finally:
            temp_path.unlink(missing_ok=True)

    def test_config_invalid_json_file(self):
        """Test handling of invalid JSON config file."""
        from p3if.utils.config import Config

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json {{{")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Invalid configuration file"):
                Config(config_file=temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_config_creates_missing_file(self):
        """Test that Config creates missing config file with defaults."""
        from p3if.utils.config import Config

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "new_config.json"

            # File shouldn't exist yet
            assert not temp_path.exists()

            # Creating Config should create the file
            config = Config(config_file=temp_path)

            # File should now exist
            assert temp_path.exists()

            # Verify it contains default config
            with open(temp_path, 'r') as f:
                saved_config = json.load(f)

            assert 'storage' in saved_config
            assert 'logging' in saved_config


class TestConfigDefaults:
    """Test cases for configuration default values."""

    def test_default_storage_config(self):
        """Test default storage configuration."""
        from p3if.utils.config import Config

        config = Config()

        assert config.get('storage.type') == 'json'
        assert config.get('storage.path') == 'p3if-data.json'

    def test_default_logging_config(self):
        """Test default logging configuration."""
        from p3if.utils.config import Config

        config = Config()

        assert config.get('logging.level') == 'INFO'
        assert '%(levelname)s' in config.get('logging.format')

    def test_default_visualization_config(self):
        """Test default visualization configuration."""
        from p3if.utils.config import Config

        config = Config()

        assert config.get('visualization.default_style') == 'modern'
        themes = config.get('visualization.themes')
        assert 'modern' in themes
        assert 'classic' in themes

    def test_default_analysis_config(self):
        """Test default analysis configuration."""
        from p3if.utils.config import Config

        config = Config()

        algorithms = config.get('analysis.default_algorithms')
        assert 'basic_stats' in algorithms
        assert 'centrality' in algorithms
        assert 'clustering' in algorithms

    def test_default_export_config(self):
        """Test default export configuration."""
        from p3if.utils.config import Config

        config = Config()

        formats = config.get('export.formats')
        assert 'json' in formats
        assert 'csv' in formats
        assert 'graphml' in formats
