"""
Pytest configuration and shared fixtures for P3IF tests.
"""

import sys
import os
from pathlib import Path
import pytest

# Add src to path - ensure it's at the beginning
# Use absolute path resolution to avoid issues with pytest's working directory
conftest_file = Path(__file__).resolve()
project_root = conftest_file.parent.parent.resolve()
src_path = project_root / "src"
src_path_str = str(src_path.resolve())

# Remove if already present to avoid duplicates
if src_path_str in sys.path:
    sys.path.remove(src_path_str)

# Insert at beginning
sys.path.insert(0, src_path_str)

# Also set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = src_path_str + os.pathsep + os.environ.get('PYTHONPATH', '')

# Debug: Verify path setup
if not Path(src_path_str).exists():
    raise RuntimeError(f"Source path does not exist: {src_path_str}")
if src_path_str not in sys.path[:3]:
    raise RuntimeError(f"Source path not in sys.path: {sys.path[:3]}")

# Verify p3if package exists
p3if_path = Path(src_path_str) / "p3if"
if not p3if_path.exists():
    raise RuntimeError(f"p3if package not found at: {p3if_path}")

# Try importing step by step
import p3if
from p3if.core import P3IFFramework
from p3if.core.models import Property, Process, Perspective

@pytest.fixture
def empty_framework():
    """Create an empty P3IF framework for testing."""
    return P3IFFramework()

@pytest.fixture
def populated_framework():
    """Create a populated P3IF framework for testing."""
    framework = P3IFFramework()
    # Add test patterns
    prop = Property(name="Test Property", description="Test property", domain="test")
    proc = Process(name="Test Process", description="Test process", domain="test")
    persp = Perspective(name="Test Perspective", description="Test perspective", domain="test", viewpoint="test")
    
    framework.add_pattern(prop)
    framework.add_pattern(proc)
    framework.add_pattern(persp)
    
    return framework
