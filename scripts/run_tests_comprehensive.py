#!/usr/bin/env python3
"""
P3IF Simple Test Runner

A simple, standalone test runner that doesn't rely on complex imports.
"""

import sys
import os
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging

# Setup logging
def setup_logging() -> logging.Logger:
    """Setup logging for test execution."""
    log_dir = Path("outputs/tests")
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
    logger.info("P3IF SIMPLE TEST RUNNER")
    logger.info("=" * 80)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log file: {log_file}")

    return logger

class SimpleTestRunner:
    """Simple test runner that uses subprocess calls."""

    def __init__(self, logger: logging.Logger):
        """Initialize the test runner."""
        self.logger = logger
        self.output_dir = Path("outputs/tests")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_pytest_with_coverage(self) -> dict:
        """Run pytest with coverage reporting."""
        self.logger.info("🧪 Running Pytest with Coverage...")

        try:
            start_time = time.time()

            # Create coverage output directory
            coverage_dir = self.output_dir / "coverage"
            coverage_dir.mkdir(exist_ok=True)

            # Run pytest with coverage
            cmd = [
                sys.executable, "-m", "pytest",
                "--cov=src/p3if",
                "--cov-report=term-missing",
                f"--cov-report=html:{coverage_dir}",
                f"--cov-report=json:{coverage_dir}/coverage.json",
                f"--cov-report=xml:{coverage_dir}/coverage.xml",
                "-v", "tests/"
            ]

            self.logger.info(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True
            )

            end_time = time.time()
            execution_time = end_time - start_time

            # Parse results
            # Extract metrics from pytest summary line (e.g., "74 failed, 154 passed, 1 skipped, 1 warning, 3 errors in 7.90s")
            tests_run = 0
            failures = 0
            errors = 0
            passed = 0
            skipped = 0

            # Look for the summary line
            for line in result.stdout.split('\n'):
                line = line.strip()
                # Look for lines like "77 failed, 155 passed, 1 warning in 5.25s"
                if 'failed' in line and 'passed' in line and '=====' in line:
                    self.logger.info(f"Found summary line: {line}")
                    # Parse the summary line like "77 failed, 155 passed, 1 warning in 5.25s"
                    # Remove the ===== padding
                    line = line.replace('=', '').strip()
                    parts = line.split(',')
                    for part in parts:
                        part = part.strip()
                        if 'failed' in part:
                            try:
                                failures = int(part.split()[0])
                                self.logger.info(f"Parsed failures: {failures}")
                            except (ValueError, IndexError):
                                failures = 0
                        elif 'passed' in part:
                            try:
                                passed = int(part.split()[0])
                                self.logger.info(f"Parsed passed: {passed}")
                            except (ValueError, IndexError):
                                passed = 0
                        elif 'skipped' in part:
                            try:
                                skipped = int(part.split()[0])
                                self.logger.info(f"Parsed skipped: {skipped}")
                            except (ValueError, IndexError):
                                skipped = 0
                        elif 'warning' in part:
                            # warnings are not counted as errors
                            pass
                        elif 'error' in part:
                            try:
                                errors = int(part.split()[0])
                                self.logger.info(f"Parsed errors: {errors}")
                            except (ValueError, IndexError):
                                errors = 0

            tests_run = passed + failures + errors + skipped

            if tests_run > 0:
                success_rate = (passed / tests_run) * 100.0
            else:
                success_rate = 0.0

            if result.returncode == 0 and failures == 0 and errors == 0:
                status = 'success'
            elif result.returncode == 0 and (failures > 0 or errors > 0):
                status = 'partial'
            else:
                status = 'failed'

            test_results = {
                'test_category': 'pytest_coverage',
                'tests_run': tests_run,
                'passed': passed,
                'failures': failures,
                'errors': errors,
                'skipped': skipped,
                'success_rate': success_rate,
                'execution_time': execution_time,
                'status': status,
                'coverage_report': f'{coverage_dir}/coverage.json',
                'html_report': f'{coverage_dir}/index.html'
            }

            self.logger.info("📊 Pytest Results:")
            self.logger.info(f"   Return code: {result.returncode}")
            self.logger.info(f"   Tests run: {test_results['tests_run']}")
            self.logger.info(f"   Failures: {test_results['failures']}")
            self.logger.info(f"   Errors: {test_results['errors']}")
            self.logger.info(f"   Execution time: {execution_time:.2f}s")

            # Log output for debugging
            if result.stdout:
                self.logger.info("STDOUT:")
                for line in result.stdout.split('\n')[-20:]:  # Last 20 lines
                    if line.strip():
                        self.logger.info(f"  {line}")

            if result.stderr:
                self.logger.error("STDERR:")
                for line in result.stderr.split('\n'):
                    if line.strip():
                        self.logger.error(f"  {line}")

            return test_results

        except Exception as e:
            self.logger.error(f"❌ Pytest execution failed: {e}")
            return {
                'test_category': 'pytest_coverage',
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'success_rate': 0.0,
                'execution_time': 0.0,
                'status': 'failed',
                'error': str(e)
            }

    def run_examples_validation(self) -> dict:
        """Run examples validation."""
        self.logger.info("🎭 Validating Examples...")

        try:
            start_time = time.time()

            # Run examples
            cmd = [sys.executable, "scripts/run_examples.py"]
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True
            )

            end_time = time.time()
            execution_time = end_time - start_time

            if result.returncode == 0:
                status = 'success'
                success_rate = 100.0
            else:
                status = 'failed'
                success_rate = 0.0

            examples_results = {
                'test_category': 'examples_validation',
                'tests_run': 1,
                'failures': 0 if result.returncode == 0 else 1,
                'errors': 0,
                'success_rate': success_rate,
                'execution_time': execution_time,
                'status': status,
                'output_dir': 'outputs/examples/'
            }

            self.logger.info(f"📊 Examples Validation: {'PASSED' if result.returncode == 0 else 'FAILED'}")
            self.logger.info(f"   Execution time: {execution_time:.2f}s")

            return examples_results

        except Exception as e:
            self.logger.error(f"❌ Examples validation failed: {e}")
            return {
                'test_category': 'examples_validation',
                'tests_run': 0,
                'failures': 1,
                'errors': 0,
                'success_rate': 0.0,
                'execution_time': 0.0,
                'status': 'failed',
                'error': str(e)
            }

    def generate_visualizations(self) -> dict:
        """Generate visualizations."""
        self.logger.info("🎨 Generating Visualizations...")

        try:
            start_time = time.time()

            # Run visualization generation
            cmd = [sys.executable, "scripts/generate_final_visualizations.py"]
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True
            )

            end_time = time.time()
            execution_time = end_time - start_time

            if result.returncode == 0:
                status = 'success'
                success_rate = 100.0
            else:
                status = 'failed'
                success_rate = 0.0

            viz_results = {
                'test_category': 'visualization_generation',
                'tests_run': 1,
                'failures': 0 if result.returncode == 0 else 1,
                'errors': 0,
                'success_rate': success_rate,
                'execution_time': execution_time,
                'status': status,
                'output_dir': 'outputs/visualizations/'
            }

            self.logger.info(f"📊 Visualization Generation: {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
            self.logger.info(f"   Execution time: {execution_time:.2f}s")

            return viz_results

        except Exception as e:
            self.logger.error(f"❌ Visualization generation failed: {e}")
            return {
                'test_category': 'visualization_generation',
                'tests_run': 0,
                'failures': 1,
                'errors': 0,
                'success_rate': 0.0,
                'execution_time': 0.0,
                'status': 'failed',
                'error': str(e)
            }

    def run_all_tests(self) -> dict:
        """Run all test categories and return comprehensive results."""
        self.logger.info("🚀 Starting Comprehensive Test Suite")
        self.logger.info("=" * 80)

        start_time = time.time()

        # Run all test categories
        test_categories = [
            self.run_pytest_with_coverage(),
            self.run_examples_validation(),
            self.generate_visualizations()
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

    def generate_test_summary(self, results: dict):
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

            f.write("## Files Generated\n\n")
            for file_path in results['files_generated']:
                f.write(f"- `{file_path}`\n")
            f.write("- `outputs/tests/coverage/` - Coverage reports and analysis\n")
            f.write("- `outputs/examples/` - Example execution results\n")
            f.write("- `outputs/visualizations/` - Generated visualizations\n")
            f.write("- Test execution logs in `logs/` directory\n\n")

            f.write("## Next Steps\n\n")
            if summary['overall_status'] == 'success':
                f.write("🎉 **All tests passed!** The P3IF system is working correctly.\n\n")
                f.write("### Recommended Actions:\n")
                f.write("1. Review coverage reports to identify untested code\n")
                f.write("2. Check generated visualizations in `outputs/visualizations/`\n")
                f.write("3. Review example outputs in `outputs/examples/`\n")
            else:
                f.write("⚠️ **Some tests failed.** Please review the test results.\n\n")
                f.write("### Troubleshooting Steps:\n")
                f.write("1. Check the detailed test logs in the `logs/` directory\n")
                f.write("2. Review coverage reports for missing test coverage\n")
                f.write("3. Check that all dependencies are installed\n")
                f.write("4. Verify Python path and environment setup\n")

            f.write("\n## System Information\n\n")
            f.write(f"- **Python Version:** {sys.version}\n")
            f.write(f"- **Test Runner:** P3IF Simple Test Runner\n")
            f.write(f"- **Coverage Tool:** pytest-cov (if available)\n")
            f.write(f"- **Timestamp:** {datetime.now().isoformat()}\n")

        results['files_generated'].append(str(summary_file))
        self.logger.info(f"📝 Test summary generated: {summary_file}")


def main():
    """Main function to run comprehensive tests."""
    print("P3IF Simple Test Runner")
    print("=======================")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Setup logging
    logger = setup_logging()

    # Create and run test suite
    test_runner = SimpleTestRunner(logger)
    results = test_runner.run_all_tests()

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
        print("🔧 Check the outputs/tests/ directory for detailed results.")

    print(f"📊 Total Tests: {summary['total_tests_run']}")
    print(f"📈 Success Rate: {summary['overall_success_rate']:.1f}%")
    print(f"⏱️  Total Time: {summary['total_execution_time']:.2f}s")

    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

