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
import os
import sys
import unittest
import argparse
import logging
from pathlib import Path

# Add the project root to the path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=Path(__file__).parent / 'visualization_tests.log',
    filemode='w'
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
    
    # Discover tests in the visualization directory
    if pattern:
        logger.info(f"Discovering tests matching pattern: {pattern}")
        test_loader = unittest.TestLoader()
        pattern_suite = test_loader.discover(
            start_dir=Path(__file__).parent,
            pattern=pattern
        )
        test_suite.addTests(pattern_suite)
    else:
        # Add specific test files in the desired order
        logger.info("Loading visualization tests in specified order")
        
        # Basic component tests
        test_loader = unittest.TestLoader()
        
        # Add base visualization tests first
        logger.info("Adding base visualization component tests")
        try:
            base_tests = test_loader.discover(
                start_dir=Path(__file__).parent,
                pattern="test_base.py"
            )
            test_suite.addTests(base_tests)
        except Exception as e:
            logger.error(f"Error loading base tests: {str(e)}")
        
        # Add portal tests
        logger.info("Adding portal visualization tests")
        try:
            portal_tests = test_loader.discover(
                start_dir=Path(__file__).parent,
                pattern="test_portal.py"
            )
            test_suite.addTests(portal_tests)
        except Exception as e:
            logger.error(f"Error loading portal tests: {str(e)}")
        
        # Add network tests
        logger.info("Adding network visualization tests")
        try:
            network_tests = test_loader.discover(
                start_dir=Path(__file__).parent,
                pattern="test_network.py"
            )
            test_suite.addTests(network_tests)
        except Exception as e:
            logger.error(f"Error loading network tests: {str(e)}")
        
        # Add matrix tests
        logger.info("Adding matrix visualization tests")
        try:
            matrix_tests = test_loader.discover(
                start_dir=Path(__file__).parent,
                pattern="test_matrix.py"
            )
            test_suite.addTests(matrix_tests)
        except Exception as e:
            logger.error(f"Error loading matrix tests: {str(e)}")
        
        # Add interactive tests
        logger.info("Adding interactive visualization tests")
        try:
            interactive_tests = test_loader.discover(
                start_dir=Path(__file__).parent,
                pattern="test_interactive.py"
            )
            test_suite.addTests(interactive_tests)
        except Exception as e:
            logger.error(f"Error loading interactive tests: {str(e)}")
        
        # Add dashboard tests
        logger.info("Adding dashboard visualization tests")
        try:
            dashboard_tests = test_loader.discover(
                start_dir=Path(__file__).parent,
                pattern="test_dashboard.py"
            )
            test_suite.addTests(dashboard_tests)
        except Exception as e:
            logger.error(f"Error loading dashboard tests: {str(e)}")
        
        # Add website tests
        logger.info("Adding website reference tests")
        try:
            website_tests = test_loader.discover(
                start_dir=Path(__file__).parent,
                pattern="test_ensure_website_references.py"
            )
            test_suite.addTests(website_tests)
        except Exception as e:
            logger.error(f"Error loading website reference tests: {str(e)}")
        
        try:
            visualization_path_tests = test_loader.discover(
                start_dir=Path(__file__).parent,
                pattern="test_fix_visualization_paths.py"
            )
            test_suite.addTests(visualization_path_tests)
        except Exception as e:
            logger.error(f"Error loading visualization path tests: {str(e)}")
        
        # Add domain tests last (these are slow)
        if not skip_slow:
            logger.info("Adding domain visualization tests")
            try:
                domain_tests = test_loader.discover(
                    start_dir=Path(__file__).parent,
                    pattern="test_all_domains.py"
                )
                test_suite.addTests(domain_tests)
            except Exception as e:
                logger.error(f"Error loading domain tests: {str(e)}")
        else:
            logger.info("Skipping slow domain tests")
        
        # Add any remaining tests that weren't explicitly specified
        logger.info("Adding any remaining visualization tests")
        try:
            remaining_tests = test_loader.discover(
                start_dir=Path(__file__).parent,
                pattern="test_*.py"
            )
            for test in remaining_tests:
                if test not in test_suite:
                    test_suite.addTest(test)
        except Exception as e:
            logger.error(f"Error loading remaining tests: {str(e)}")
    
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
        "--pattern", 
        type=str, 
        help="Pattern for test discovery (e.g. test_base.py)"
    )
    parser.add_argument(
        "--verbosity", 
        type=int, 
        default=2, 
        help="Test runner verbosity (1-3)"
    )
    parser.add_argument(
        "--skip-slow", 
        action="store_true", 
        help="Skip slow tests (like all_domains tests)"
    )
    
    args = parser.parse_args()
    
    # Run tests
    success = run_all_tests(
        verbosity=args.verbosity,
        pattern=args.pattern,
        skip_slow=args.skip_slow
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 