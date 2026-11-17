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
os.environ["PYTHONPATH"] = src_path_str + os.pathsep + os.environ.get("PYTHONPATH", "")

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
from p3if.core import P3IFFramework  # noqa: E402 - after sys.path verification
from p3if.core.models import (  # noqa: E402 - after sys.path setup
    Property,
    Process,
    Perspective,
)  # noqa: E402 - after sys.path verification


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
    persp = Perspective(
        name="Test Perspective", description="Test perspective", domain="test", viewpoint="test"
    )

    framework.add_pattern(prop)
    framework.add_pattern(proc)
    framework.add_pattern(persp)

    return framework


# Test modules that write fixed paths inside the repository: the committed
# `tests/visualization/test_output/` gallery, `outputs/` (timestamped output-organizer
# sessions and the unified dashboard) and the visualization runner log. Under `pytest -n`
# every such module keeps all of its tests on one worker (its own xdist group), so tests
# within a module never race; modules that write nothing spread freely.
#
# Measured write sets (each module run alone, file mtimes compared): these modules rewrite
# the same gallery files (assets, data/*.json, compare/*.png) or create the timestamped
# `outputs/p3if_output_*` sessions, so they share one group and run in sequence. Every other
# writer touched only paths no other module touches. When a test starts writing a new fixed
# path, add its module here unless that path is private to the module.
_SHARED_GALLERY_MODULES = frozenset(
    {
        "tests/visualization/test_all_domains.py",
        "tests/visualization/test_integrated_website.py",
        "tests/visualization/test_interactive.py",
        "tests/visualization/test_portal.py",
    }
)
_REPOSITORY_OUTPUT_MODULES = frozenset(
    {
        "tests/test_visualization_runner.py",
        "tests/integration/test_api.py",
        "tests/integration/test_website_routes.py",
        "tests/unit/test_interactive_3d.py",
        "tests/unit/test_orchestration.py",
        "tests/unit/test_orchestrator_modules.py",
        "tests/unit/test_orchestrators.py",
    }
)


def _output_group(relative: str) -> str | None:
    """Return the xdist group for a repository-relative test module, if it writes outputs."""
    if relative in _SHARED_GALLERY_MODULES:
        return "repository-gallery"
    if relative.startswith("tests/visualization/") or relative in _REPOSITORY_OUTPUT_MODULES:
        return "repository-outputs:" + relative
    return None


# tryfirst: this conftest loads before xdist's worker plugin registers, so without it xdist
# would read the markers (and suffix node IDs with the group) before they are added.
@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Assign repository-output writers to xdist groups (inert without xdist)."""
    for item in items:
        relative = Path(str(item.path)).resolve().relative_to(project_root).as_posix()
        group = _output_group(relative)
        if group is not None:
            item.add_marker(pytest.mark.xdist_group(group))
