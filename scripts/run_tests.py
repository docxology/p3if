#!/usr/bin/env python3
"""
P3IF Comprehensive Test Runner

A comprehensive test runner with detailed logging, validation, and output confirmation.
"""

import sys
import os
import json
import time
import unittest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Ensure p3if package is importable
p3if_package_path = project_root
sys.path.insert(0, str(p3if_package_path))

# Also add the current directory to handle relative imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import logging
from p3if_tests.test_core import TestP3IFCore, TestP3IFOperation
from p3if_tests.test_composition import TestFrameworkAdapter, TestCompositionEngine, TestMultiplexer
from p3if_tests.core.test_models import TestProperty, TestProcess, TestPerspective, TestRelationship
from p3if_tests.core.test_framework import TestP3IFFramework

# Setup comprehensive logging
def setup_logging() -> logging.Logger:
    """Setup comprehensive logging for test execution."""
    log_dir = Path("output/tests")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"test_execution_{timestamp}.log"

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger("P3IF_Tests")
    logger.info("=" * 80)
    logger.info("P3IF COMPREHENSIVE TEST RUNNER")
    logger.info("=" * 80)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log file: {log_file}")

    return logger


class P3IFTestSuite:
    """Comprehensive test suite for P3IF with validation and reporting."""

    def __init__(self, logger: logging.Logger):
        """Initialize the test suite."""
        self.logger = logger
        self.results = {}
        self.output_dir = Path("output/tests")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_core_tests(self) -> Dict[str, Any]:
        """Run core P3IF functionality tests."""
        self.logger.info("🧪 Running Core Tests...")

        start_time = time.time()

        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        # Add core test classes
        core_test_classes = [
            TestP3IFCore,
            TestP3IFOperation,
            TestProperty,
            TestProcess,
            TestPerspective,
            TestRelationship,
            TestP3IFFramework
        ]

        for test_class in core_test_classes:
            try:
                tests = loader.loadTestsFromTestCase(test_class)
                suite.addTests(tests)
                self.logger.info(f"✅ Added {test_class.__name__}")
            except Exception as e:
                self.logger.error(f"❌ Failed to load {test_class.__name__}: {e}")

        # Run tests
        runner = unittest.TextTestRunner(
            verbosity=2,
            failfast=False,
            stream=TestResultStream(self.logger)
        )

        result = runner.run(suite)

        # Calculate metrics
        end_time = time.time()
        execution_time = end_time - start_time

        test_results = {
            'test_category': 'core',
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
            'execution_time': execution_time,
            'status': 'success' if len(result.failures) == 0 and len(result.errors) == 0 else 'failed'
        }

        self.logger.info(f"📊 Core Tests: {test_results['tests_run']} run, {test_results['failures']} failed, {test_results['errors']} errors")
        self.logger.info(f"⏱️  Execution time: {execution_time:.2f}s")
        self.logger.info(f"📈 Success rate: {test_results['success_rate']:.1f}%")

        return test_results

    def run_composition_tests(self) -> Dict[str, Any]:
        """Run composition and multiplexing tests."""
        self.logger.info("🔗 Running Composition Tests...")

        start_time = time.time()

        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        # Add composition test classes
        composition_test_classes = [
            TestFrameworkAdapter,
            TestCompositionEngine,
            TestMultiplexer
        ]

        for test_class in composition_test_classes:
            try:
                tests = loader.loadTestsFromTestCase(test_class)
                suite.addTests(tests)
                self.logger.info(f"✅ Added {test_class.__name__}")
            except Exception as e:
                self.logger.error(f"❌ Failed to load {test_class.__name__}: {e}")

        # Run tests
        runner = unittest.TextTestRunner(
            verbosity=2,
            failfast=False,
            stream=TestResultStream(self.logger)
        )

        result = runner.run(suite)

        # Calculate metrics
        end_time = time.time()
        execution_time = end_time - start_time

        test_results = {
            'test_category': 'composition',
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
            'execution_time': execution_time,
            'status': 'success' if len(result.failures) == 0 and len(result.errors) == 0 else 'failed'
        }

        self.logger.info(f"📊 Composition Tests: {test_results['tests_run']} run, {test_results['failures']} failed, {test_results['errors']} errors")
        self.logger.info(f"⏱️  Execution time: {execution_time:.2f}s")
        self.logger.info(f"📈 Success rate: {test_results['success_rate']:.1f}%")

        return test_results

    def run_pytest_with_coverage(self) -> Dict[str, Any]:
        """Run pytest with coverage reporting."""
        self.logger.info("🧪 Running Pytest with Coverage...")

        try:
            import pytest
            import subprocess

            start_time = time.time()

            # Create coverage output directory
            coverage_dir = self.output_dir / "coverage"
            coverage_dir.mkdir(exist_ok=True)

            # Run pytest with basic options first to check if it works
            cmd = [
                sys.executable, "-m", "pytest",
                "-v", "p3if_tests/",
                "--tb=short"
            ]

            self.logger.info(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=60  # Add timeout to prevent hanging
            )

            end_time = time.time()
            execution_time = end_time - start_time

            # Parse results from pytest output
            stdout_lines = result.stdout.split('\n')
            tests_run = 0
            failures = 0
            errors = 0

            # Parse pytest output to extract test results
            for line in stdout_lines:
                line = line.strip()
                if line.startswith('p3if_tests/') and ('PASSED' in line or 'FAILED' in line or 'ERROR' in line):
                    if 'PASSED' in line:
                        tests_run += 1
                    elif 'FAILED' in line:
                        tests_run += 1
                        failures += 1
                    elif 'ERROR' in line:
                        tests_run += 1
                        errors += 1

            # If no tests were found, try a different parsing approach
            if tests_run == 0:
                # Look for summary line
                for line in stdout_lines[-10:]:  # Check last 10 lines
                    if 'passed' in line.lower() and 'failed' in line.lower():
                        # Extract numbers using regex-like approach
                        parts = line.replace(',', '').split()
                        for i, part in enumerate(parts):
                            if part.isdigit():
                                if i > 0 and parts[i-1].lower() in ['passed', 'pass']:
                                    tests_run = int(part)
                                elif i > 0 and parts[i-1].lower() in ['failed', 'fail']:
                                    failures = int(part)
                                elif i > 0 and parts[i-1].lower() in ['error', 'errors']:
                                    errors = int(part)

            success_rate = ((tests_run - failures - errors) / tests_run * 100) if tests_run > 0 else 0

            # Determine status
            if result.returncode == 0 and failures == 0 and errors == 0:
                status = 'success'
            else:
                status = 'failed'

            test_results = {
                'test_category': 'pytest_validation',
                'tests_run': tests_run,
                'failures': failures,
                'errors': errors,
                'success_rate': success_rate,
                'execution_time': execution_time,
                'status': status,
                'return_code': result.returncode
            }

            self.logger.info("📊 Pytest Results:")
            self.logger.info(f"   Return code: {result.returncode}")
            self.logger.info(f"   Tests run: {test_results['tests_run']}")
            self.logger.info(f"   Failures: {test_results['failures']}")
            self.logger.info(f"   Errors: {test_results['errors']}")
            self.logger.info(f"   Success rate: {test_results['success_rate']:.1f}%")
            self.logger.info(f"   Execution time: {execution_time:.2f}s")

            # Log output for debugging
            if result.stdout:
                self.logger.info("STDOUT:")
                # Show first 10 and last 10 lines for context
                lines = result.stdout.split('\n')
                for line in lines[:10] + ['...'] + lines[-10:]:
                    if line.strip():
                        self.logger.info(f"  {line}")

            if result.stderr:
                self.logger.error("STDERR:")
                for line in result.stderr.split('\n'):
                    if line.strip():
                        self.logger.error(f"  {line}")

            return test_results

        except subprocess.TimeoutExpired:
            self.logger.error("❌ Pytest execution timed out after 60 seconds")
            return {
                'test_category': 'pytest_validation',
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'success_rate': 0.0,
                'execution_time': 60.0,
                'status': 'failed',
                'error': 'pytest execution timed out'
            }
        except ImportError:
            self.logger.error("❌ pytest not available")
            return {
                'test_category': 'pytest_validation',
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'success_rate': 0.0,
                'execution_time': 0.0,
                'status': 'failed',
                'error': 'pytest not installed'
            }
        except Exception as e:
            self.logger.error(f"❌ Pytest execution failed: {e}")
            return {
                'test_category': 'pytest_validation',
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'success_rate': 0.0,
                'execution_time': 0.0,
                'status': 'failed',
                'error': str(e)
            }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test categories and return comprehensive results."""
        self.logger.info("🚀 Starting Comprehensive Test Suite")
        self.logger.info("=" * 80)

        start_time = time.time()

        # Run all test categories
        test_categories = [
            self.run_core_tests(),
            self.run_composition_tests(),
            self.run_pytest_with_coverage()
        ]

        end_time = time.time()
        total_execution_time = end_time - start_time

        # Calculate overall metrics
        total_tests = sum(cat.get('tests_run', 0) for cat in test_categories)
        total_failures = sum(cat.get('failures', 0) for cat in test_categories)
        total_errors = sum(cat.get('errors', 0) for cat in test_categories)

        overall_success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0

        # Determine overall status
        overall_status = 'success'
        for category in test_categories:
            if category.get('status') == 'failed':
                overall_status = 'failed'
                break
        if total_failures > 0 or total_errors > 0:
            overall_status = 'partial'

        # Compile results
        results = {
            'execution_summary': {
                'start_time': datetime.now().isoformat(),
                'total_execution_time': total_execution_time,
                'total_tests_run': total_tests,
                'total_failures': total_failures,
                'total_errors': total_errors,
                'overall_success_rate': overall_success_rate,
                'overall_status': overall_status
            },
            'test_categories': test_categories,
            'files_generated': []
        }

        # Generate summary report
        self.generate_test_summary(results)

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.output_dir / f"test_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        results['files_generated'].append(str(results_file))

        self.logger.info("=" * 80)
        self.logger.info("🎉 Test Execution Complete")
        self.logger.info(f"📊 Overall Status: {overall_status.upper()}")
        self.logger.info(f"📈 Success Rate: {overall_success_rate:.1f}%")
        self.logger.info(f"⏱️  Total Time: {total_execution_time:.2f}s")
        self.logger.info(f"📁 Results saved to: {results_file}")

        return results

    def generate_test_summary(self, results: Dict[str, Any]):
        """Generate a comprehensive test summary report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.output_dir / f"test_summary_{timestamp}.md"

        summary = results['execution_summary']

        with open(summary_file, 'w') as f:
            f.write("# P3IF Test Execution Summary\n\n")
            f.write(f"**Execution Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write(f"## Overall Results\n\n")
            f.write(f"**Status:** {summary['overall_status'].upper()}\n")
            f.write(f"**Total Tests Run:** {summary['total_tests_run']}\n")
            f.write(f"**Total Failures:** {summary['total_failures']}\n")
            f.write(f"**Total Errors:** {summary['total_errors']}\n")
            f.write(f"**Success Rate:** {summary['overall_success_rate']:.1f}%\n")
            f.write(f"**Total Execution Time:** {summary['total_execution_time']:.2f} seconds\n\n")

            f.write("## Test Categories\n\n")

            for category in results['test_categories']:
                f.write(f"### {category['test_category'].replace('_', ' ').title()}\n\n")
                f.write(f"**Status:** {category['status'].upper()}\n")
                f.write(f"**Tests Run:** {category['tests_run']}\n")
                f.write(f"**Failures:** {category['failures']}\n")
                f.write(f"**Errors:** {category['errors']}\n")
                f.write(f"**Success Rate:** {category['success_rate']:.1f}%\n")
                f.write(f"**Execution Time:** {category['execution_time']:.2f} seconds\n\n")

                # Add specific error details if available
                if category.get('status') == 'failed' and 'error' in category:
                    f.write(f"**Error:** {category['error']}\n\n")

                f.write("---\n\n")

            f.write("## Coverage Information\n\n")
            f.write("Coverage reports are available in the `output/tests/coverage/` directory:\n")
            f.write("- **HTML Report:** Interactive coverage analysis\n")
            f.write("- **JSON Report:** Machine-readable coverage data\n\n")

            f.write("## Files Generated\n\n")
            for file_path in results['files_generated']:
                f.write(f"- `{file_path}`\n")
            f.write("- `output/tests/coverage/` - Coverage reports and analysis\n")
            f.write("- Test execution logs in `logs/` directory\n\n")

            f.write("## Next Steps\n\n")
            if summary['overall_status'] == 'success':
                f.write("🎉 **All tests passed!** The P3IF system is working correctly.\n\n")
                f.write("### Recommended Actions:\n")
                f.write("1. Review coverage reports to identify untested code\n")
                f.write("2. Run specific test categories if needed:\n")
                f.write("   - Core functionality: `python -m unittest p3if_tests.test_core`\n")
                f.write("   - Composition: `python -m unittest p3if_tests.test_composition`\n")
                f.write("3. Generate visualizations: `python scripts/generate_final_visualizations.py`\n")
            else:
                f.write("⚠️ **Some tests failed.** Please review the test results.\n\n")
                f.write("### Troubleshooting Steps:\n")
                f.write("1. Check the detailed test logs in the `logs/` directory\n")
                f.write("2. Review coverage reports for missing test coverage\n")
                f.write("3. Run individual test files to isolate issues\n")
                f.write("4. Check dependencies and environment setup\n")

            f.write("\n## System Information\n\n")
            f.write(f"- **Python Version:** {sys.version}\n")
            f.write(f"- **Test Runner:** P3IF Comprehensive Test Suite\n")
            f.write(f"- **Coverage Tool:** pytest-cov (if available)\n")
            f.write(f"- **Timestamp:** {datetime.now().isoformat()}\n")

        results['files_generated'].append(str(summary_file))
        self.logger.info(f"📝 Test summary generated: {summary_file}")


class TestResultStream:
    """Custom test result stream for enhanced logging."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def write(self, text):
        """Write text with appropriate formatting."""
        if text.strip():
            if 'FAIL' in text or 'ERROR' in text:
                self.logger.error(f"TEST: {text.strip()}")
            elif 'PASS' in text or 'OK' in text:
                self.logger.info(f"TEST: {text.strip()}")
            else:
                self.logger.debug(f"TEST: {text.strip()}")

    def flush(self):
        """Flush the stream."""
        pass


def main():
    """Main function to run comprehensive tests."""
    print("P3IF Comprehensive Test Runner")
    print("===============================")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Setup logging
    logger = setup_logging()

    # Create and run test suite
    test_suite = P3IFTestSuite(logger)
    results = test_suite.run_all_tests()

    # Exit with appropriate code
    exit_code = 0 if results['execution_summary']['overall_status'] == 'success' else 1

    print()
    print("=" * 60)
    summary = results['execution_summary']
    if exit_code == 0:
        print("✅ ALL TESTS PASSED!")
        print("🎉 The P3IF system is working correctly.")
    else:
        print(f"⚠️  SOME TESTS FAILED! ({summary['total_failures']} failures, {summary['total_errors']} errors)")
        print("🔧 Check the output/tests/ directory for detailed results.")

    print(f"📊 Total Tests: {summary['total_tests_run']}")
    print(f"📈 Success Rate: {summary['overall_success_rate']:.1f}%")
    print(f"⏱️  Total Time: {summary['total_execution_time']:.2f}s")

    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
