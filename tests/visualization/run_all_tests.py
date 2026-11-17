#!/usr/bin/env python3
"""
Run all visualization tests for the P3IF framework.

This script discovers and runs all visualization tests, including:
1. Base visualization component tests
2. Portal tests
3. Network visualization tests
4. Matrix visualization tests
5. Domain-specific tests
6. Website reference tests
"""

import argparse
import logging
import sys
import unittest
from pathlib import Path

# Configure matplotlib to use the non-interactive Agg backend to prevent popups during tests
import matplotlib

matplotlib.use("Agg")

# Add the project root to the path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=Path(__file__).parent / "visualization_tests.log",
    filemode="w",
)
logger = logging.getLogger()
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)


def run_all_tests(verbosity=2, pattern=None, skip_slow=False):
    """Run all visualization tests."""
    # Create the test output directory if it doesn't exist
    test_output_dir = Path(__file__).parent / "test_output"
    test_output_dir.mkdir(exist_ok=True)

    # Start with an empty test suite
    test_suite = unittest.TestSuite()

    class DiscoveryFailure(unittest.TestCase):
        """Keep a discovery exception visible in the suite result."""

        def __init__(self, selector, error):
            super().__init__("runTest")
            self.selector = selector
            self.error = error

        def runTest(self):
            raise RuntimeError(f"Error loading {self.selector}: {self.error}") from self.error

    selectors = (
        [pattern]
        if pattern
        else [
            "test_base.py",
            "test_portal.py",
            "test_network.py",
            "test_matrix.py",
            "test_interactive.py",
            "test_dashboard.py",
            "test_ensure_website_references.py",
            "test_fix_visualization_paths.py",
        ]
    )
    if not pattern:
        if not skip_slow:
            selectors.append("test_all_domains.py")
        selectors.append("test_*.py")
    test_loader = unittest.TestLoader()
    for selector in selectors:
        logger.info(f"Discovering tests matching pattern: {selector}")
        try:
            # Keep loader-created _FailedTest instances: their import exceptions
            # become errors when TextTestRunner executes the suite.
            test_suite.addTests(test_loader.discover(start_dir=current_dir, pattern=selector))
        except Exception as error:
            logger.error(f"Error loading {selector}: {error}")
            test_suite.addTest(DiscoveryFailure(selector, error))

    # Run the tests
    logger.info("Running visualization tests...")
    test_runner = unittest.TextTestRunner(verbosity=verbosity)
    test_result = test_runner.run(test_suite)

    # Log the results
    logger.info(f"Tests run: {test_result.testsRun}")
    logger.info(f"Errors: {len(test_result.errors)}")
    logger.info(f"Failures: {len(test_result.failures)}")

    # Return success if there were no errors or failures
    return len(test_result.errors) == 0 and len(test_result.failures) == 0


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Run P3IF visualization tests")
    parser.add_argument(
        "--pattern", type=str, help="Pattern for test discovery (e.g. test_base.py)"
    )
    parser.add_argument("--verbosity", type=int, default=2, help="Test runner verbosity (1-3)")
    parser.add_argument(
        "--skip-slow", action="store_true", help="Skip slow tests (like all_domains tests)"
    )

    args = parser.parse_args()

    # Run tests
    success = run_all_tests(
        verbosity=args.verbosity, pattern=args.pattern, skip_slow=args.skip_slow
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
