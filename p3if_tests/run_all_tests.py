#!/usr/bin/env python3
"""
Comprehensive test runner for the P3IF project.

This script runs all tests across the P3IF codebase with comprehensive reporting,
coverage analysis, and performance metrics.
"""
import sys
import time
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime, timezone


class TestRunner:
    """Comprehensive test runner for P3IF."""

    def __init__(self, verbose: bool = False, coverage: bool = False, parallel: bool = False):
        """Initialize the test runner.

        Args:
            verbose: Enable verbose output
            coverage: Enable coverage reporting
            parallel: Enable parallel test execution
        """
        self.verbose = verbose
        self.coverage = coverage
        self.parallel = parallel
        self.project_root = Path(__file__).parent.parent
        self.test_results = {}

    def run_command(self, command: List[str], description: str) -> Dict[str, Any]:
        """Run a shell command and return the result.

        Args:
            command: Command to run as list of strings
            description: Description of what the command does

        Returns:
            Dictionary with command results
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Running: {description}")
            print(f"Command: {' '.join(command)}")
            print(f"{'='*60}")

        start_time = time.time()
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )

            end_time = time.time()
            duration = end_time - start_time

            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': duration,
                'description': description,
                'command': ' '.join(command)
            }

        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time

            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'duration': duration,
                'description': description,
                'command': ' '.join(command),
                'error': str(e)
            }

    def run_pytest(self, test_path: str, additional_args: List[str] = None) -> Dict[str, Any]:
        """Run pytest on a specific test path.

        Args:
            test_path: Path to test directory or file
            additional_args: Additional arguments for pytest

        Returns:
            Dictionary with test results
        """
        cmd_args = ['python', '-m', 'pytest']

        if self.coverage:
            cmd_args.extend(['--cov', 'core', '--cov', 'website', '--cov', 'utils', '--cov', 'analysis', '--cov', 'visualization'])
            cmd_args.extend(['--cov-report', 'term-missing', '--cov-report', 'html:htmlcov'])

        if self.parallel and 'test_' in test_path:
            cmd_args.extend(['-n', 'auto'])

        if additional_args:
            cmd_args.extend(additional_args)

        cmd_args.append(test_path)
        cmd_args.extend(['-v', '--tb=short', '--strict-markers'])

        return self.run_command(cmd_args, f"Running pytest on {test_path}")

    def run_core_tests(self) -> Dict[str, Any]:
        """Run core module tests."""
        if self.verbose:
            print("\n🧠 Running Core Module Tests")

        return self.run_pytest('tests/core/', [
            '--maxfail=5',
            '--durations=10'
        ])

    def run_api_tests(self) -> Dict[str, Any]:
        """Run API tests."""
        if self.verbose:
            print("\n🌐 Running API Tests")

        return self.run_pytest('tests/website/', [
            '--maxfail=3'
        ])

    def run_visualization_tests(self) -> Dict[str, Any]:
        """Run visualization tests."""
        if self.verbose:
            print("\n📊 Running Visualization Tests")

        return self.run_pytest('tests/visualization/', [
            '--maxfail=3',
            '--durations=20'
        ])

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        if self.verbose:
            print("\n🔗 Running Integration Tests")

        return self.run_pytest('tests/', [
            '-k', 'integration',
            '--maxfail=2'
        ])

    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        if self.verbose:
            print("\n⚡ Running Performance Tests")

        return self.run_pytest('tests/', [
            '-k', 'performance',
            '--maxfail=1'
        ])

    def run_type_checking(self) -> Dict[str, Any]:
        """Run type checking with mypy."""
        if self.verbose:
            print("\n🔍 Running Type Checking")

        return self.run_command([
            'python', '-m', 'mypy',
            'core/', 'website/', 'utils/', 'analysis/', 'visualization/',
            '--ignore-missing-imports',
            '--no-strict-optional'
        ], "Running mypy type checking")

    def run_linting(self) -> Dict[str, Any]:
        """Run linting with flake8."""
        if self.verbose:
            print("\n🧹 Running Linting")

        return self.run_command([
            'python', '-m', 'flake8',
            'core/', 'website/', 'utils/', 'analysis/', 'visualization/',
            '--max-line-length=100',
            '--extend-ignore=E203,W503'
        ], "Running flake8 linting")

    def run_security_check(self) -> Dict[str, Any]:
        """Run security check with bandit."""
        if self.verbose:
            print("\n🔒 Running Security Check")

        return self.run_command([
            'python', '-m', 'bandit',
            '-r', 'core/', 'website/', 'utils/', 'analysis/', 'visualization/',
            '-f', 'json'
        ], "Running bandit security check")

    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report.

        Returns:
            Dictionary containing test report
        """
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'test_results': {},
            'summary': {
                'total_duration': 0,
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'error_tests': 0,
                'success_rate': 0.0
            },
            'quality_metrics': {
                'type_coverage': False,
                'linting_passed': False,
                'security_issues': 0
            }
        }

        # Aggregate test results
        test_categories = ['core', 'api', 'visualization', 'integration', 'performance']
        total_duration = 0

        for category in test_categories:
            if category in self.test_results:
                result = self.test_results[category]
                report['test_results'][category] = result

                if result['success']:
                    # Extract test statistics from stdout
                    lines = result['stdout'].split('\n')
                    for line in lines:
                        if 'passed' in line.lower() and 'failed' in line.lower():
                            parts = line.split(',')
                            for part in parts:
                                if 'passed' in part:
                                    try:
                                        passed = int(part.strip().split()[0])
                                        report['summary']['passed_tests'] += passed
                                    except (ValueError, IndexError):
                                        pass
                                elif 'failed' in part:
                                    try:
                                        failed = int(part.strip().split()[0])
                                        report['summary']['failed_tests'] += failed
                                    except (ValueError, IndexError):
                                        pass

                total_duration += result['duration']

        # Calculate summary statistics
        report['summary']['total_duration'] = total_duration
        report['summary']['total_tests'] = report['summary']['passed_tests'] + report['summary']['failed_tests']

        if report['summary']['total_tests'] > 0:
            report['summary']['success_rate'] = (
                report['summary']['passed_tests'] / report['summary']['total_tests']
            ) * 100

        # Quality metrics
        if 'type_checking' in self.test_results:
            report['quality_metrics']['type_coverage'] = self.test_results['type_checking']['success']

        if 'linting' in self.test_results:
            report['quality_metrics']['linting_passed'] = self.test_results['linting']['success']

        if 'security' in self.test_results:
            security_result = self.test_results['security']
            if security_result['success']:
                try:
                    security_data = json.loads(security_result['stdout'])
                    report['quality_metrics']['security_issues'] = len(security_data.get('results', []))
                except (json.JSONDecodeError, KeyError):
                    report['quality_metrics']['security_issues'] = 0

        return report

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and quality checks.

        Returns:
            Dictionary containing comprehensive test report
        """
        print("🚀 Starting P3IF Comprehensive Test Suite")
        print(f"Project Root: {self.project_root}")
        print(f"Verbose: {self.verbose}, Coverage: {self.coverage}, Parallel: {self.parallel}")
        print("-" * 60)

        # Run test categories
        test_methods = [
            ('core', self.run_core_tests),
            ('api', self.run_api_tests),
            ('visualization', self.run_visualization_tests),
            ('integration', self.run_integration_tests),
            ('performance', self.run_performance_tests),
        ]

        for category, method in test_methods:
            try:
                result = method()
                self.test_results[category] = result
            except Exception as e:
                self.test_results[category] = {
                    'success': False,
                    'returncode': -1,
                    'stdout': '',
                    'stderr': str(e),
                    'duration': 0,
                    'description': f"Running {category} tests",
                    'error': str(e)
                }

        # Run quality checks
        quality_methods = [
            ('type_checking', self.run_type_checking),
            ('linting', self.run_linting),
            ('security', self.run_security_check),
        ]

        for category, method in quality_methods:
            try:
                result = method()
                self.test_results[category] = result
            except Exception as e:
                self.test_results[category] = {
                    'success': False,
                    'returncode': -1,
                    'stdout': '',
                    'stderr': str(e),
                    'duration': 0,
                    'description': f"Running {category} check",
                    'error': str(e)
                }

        # Generate comprehensive report
        report = self.generate_test_report()

        return report

    def print_report(self, report: Dict[str, Any]):
        """Print a formatted test report.

        Args:
            report: Test report dictionary
        """
        print("\n" + "="*80)
        print("📋 P3IF COMPREHENSIVE TEST REPORT")
        print("="*80)
        print(f"Generated: {report['timestamp']}")
        print()

        # Summary section
        summary = report['summary']
        print("📊 SUMMARY")
        print("-" * 40)
        print(f"Total Duration:    {summary['total_duration']:.2f}s")
        print(f"Total Tests:       {summary['total_tests']}")
        print(f"Passed Tests:      {summary['passed_tests']}")
        print(f"Failed Tests:      {summary['failed_tests']}")
        print(f"Success Rate:      {summary['success_rate']:.1f}%")
        print()

        # Quality metrics
        quality = report['quality_metrics']
        print("✨ QUALITY METRICS")
        print("-" * 40)
        print(f"Type Coverage:     {'✅' if quality['type_coverage'] else '❌'}")
        print(f"Linting Passed:    {'✅' if quality['linting_passed'] else '❌'}")
        print(f"Security Issues:   {quality['security_issues']} {'✅' if quality['security_issues'] == 0 else '⚠️'}")
        print()

        # Test results by category
        print("🧪 TEST RESULTS BY CATEGORY")
        print("-" * 40)

        for category, result in report['test_results'].items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            duration = f"{result['duration']:.2f}s"
            print(f"{category:<15} {status:<10} {duration:>8}")

            if not result['success'] and self.verbose:
                print(f"    Error: {result.get('stderr', 'Unknown error')[:100]}...")
                if result.get('error'):
                    print(f"    Exception: {result['error'][:100]}...")

        print()

        # Overall assessment
        success_rate = summary['success_rate']
        if success_rate >= 90:
            print("🎉 EXCELLENT - All tests passing!")
        elif success_rate >= 75:
            print("👍 GOOD - Most tests passing")
        elif success_rate >= 50:
            print("⚠️  NEEDS IMPROVEMENT - Several test failures")
        else:
            print("❌ CRITICAL - Many test failures require attention")

        print("="*80)


def main():
    """Main function to run the test suite."""
    parser = argparse.ArgumentParser(description='Run P3IF comprehensive test suite')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-c', '--coverage', action='store_true', help='Enable coverage reporting')
    parser.add_argument('-p', '--parallel', action='store_true', help='Enable parallel test execution')
    parser.add_argument('--report-only', action='store_true', help='Only generate report from previous run')
    parser.add_argument('--output', type=str, help='Output report to file')

    args = parser.parse_args()

    # Check if we have pytest installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest is not installed. Please install it with: pip install pytest")
        sys.exit(1)

    # Initialize test runner
    runner = TestRunner(verbose=args.verbose, coverage=args.coverage, parallel=args.parallel)

    if args.report_only:
        # Try to load previous results
        report_file = Path('test_report.json')
        if report_file.exists():
            with open(report_file, 'r') as f:
                report = json.load(f)
            runner.print_report(report)
        else:
            print("❌ No previous test report found. Run tests first.")
            sys.exit(1)
    else:
        # Run all tests
        report = runner.run_all_tests()

        # Print report
        runner.print_report(report)

        # Save report if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 Report saved to: {args.output}")

        # Exit with appropriate code
        summary = report['summary']
        if summary['success_rate'] < 100 and summary['failed_tests'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == '__main__':
    main()
