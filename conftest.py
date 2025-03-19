"""
Test configuration for P3IF.

This file contains pytest fixtures and configuration for testing P3IF.
"""
import os
import sys
import pytest
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Create fixtures that can be used by multiple test modules
@pytest.fixture
def sample_data_dir():
    """Return the path to the sample data directory."""
    return project_root / "tests" / "data" / "samples" 