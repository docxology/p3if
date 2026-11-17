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


# Modules whose tests write fixed paths inside the repository: the committed
# `tests/visualization/test_output/` gallery, `outputs/` (output organizer sessions and the
# unified dashboard) and the website's output folders. Under `pytest -n` they share one xdist
# group, so they run in order on a single worker and never race on the same file, while every
# other test spreads across the remaining workers.
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


def _writes_repository_outputs(relative: str) -> bool:
    """Return whether a repository-relative test module writes fixed repository paths."""
    return relative.startswith("tests/visualization/") or relative in _REPOSITORY_OUTPUT_MODULES


# tryfirst: this conftest loads before xdist's worker plugin registers, so without it xdist
# would read the markers (and suffix node IDs with the group) before they are added.
@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Serialize repository-output writers into one xdist group (inert without xdist)."""
    for item in items:
        relative = Path(str(item.path)).resolve().relative_to(project_root).as_posix()
        if _writes_repository_outputs(relative):
            item.add_marker(pytest.mark.xdist_group("repository-outputs"))
