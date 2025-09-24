#!/usr/bin/env python
"""
Test runner for P3IF visualization tests.

This script runs all the visualization test suites and generates a report.
It can be run with various options to control which tests are executed.

All test outputs (HTML files, PNG images, etc.) are saved to the test_output directory 
within the visualization tests folder. This allows for easy inspection of the generated
visualizations after the tests have completed.
"""
import os
import sys
import unittest
import argparse
import datetime
import logging
import tempfile
from pathlib import Path
import re

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Import test modules
from tests.visualization.test_interactive import TestInteractiveVisualizer
from tests.visualization.test_portal import TestVisualizationPortal
from tests.visualization.test_dashboard import TestDashboardGenerator
from tests.visualization.test_integrated_website import TestIntegratedWebsite
from tests.visualization.test_base import TestVisualizer

# Set up logging
log_file = Path('visualization_tests.log')
if log_file.exists():
    # Clear the old log file
    log_file.unlink()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('visualization_tests.log')
    ]
)
logger = logging.getLogger('visualization_tests')


class OutputPathTrackingTestResult(unittest.TextTestResult):
    """Custom TestResult that captures and logs output paths from test runs."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_paths = []
        
    def startTest(self, test):
        super().startTest(test)
        test.setUp()  # Ensure test is set up properly
        
    def stopTest(self, test):
        super().stopTest(test)
        
        # Try to extract output paths from the test's attributes
        try:
            if hasattr(test, 'output_path') and test.output_path:
                self._log_outputs(test.output_path, test)
            
            if hasattr(test, 'test_dir') and test.test_dir:
                self._log_outputs(Path(test.test_dir.name), test)
        except Exception as e:
            logger.error(f"Error extracting output paths from {test}: {e}")
            
    def _log_outputs(self, base_path, test):
        """Log all outputs found in the specified path."""
        try:
            base_path = Path(base_path)
            if not base_path.exists():
                return
                
            logger.info(f"Output directory for {test.__class__.__name__}.{test._testMethodName}: {base_path}")
            
            # Scan for HTML files
            for html_file in base_path.glob('**/*.html'):
                self.output_paths.append(html_file)
                logger.info(f"  HTML output: {html_file}")
                
            # Scan for visualization images
            for img_file in base_path.glob('**/*.png'):
                self.output_paths.append(img_file)
                logger.info(f"  Visualization image: {img_file}")
                
            # Scan for JSON reports
            for json_file in base_path.glob('**/*.json'):
                self.output_paths.append(json_file)
                logger.info(f"  JSON report: {json_file}")
                
            # Inspect HTML files for additional output references
            for html_file in base_path.glob('**/*.html'):
                try:
                    with open(html_file, 'r') as f:
                        content = f.read()
                        # Look for file references in HTML
                        for match in re.finditer(r'src=[\'"]([^\'"]+)[\'"]', content):
                            src = match.group(1)
                            logger.info(f"  Referenced resource in {html_file.name}: {src}")
                except Exception as e:
                    logger.error(f"Error inspecting HTML file {html_file}: {e}")
        except Exception as e:
            logger.error(f"Error logging outputs from {base_path}: {e}")


class OutputPathTrackingTestRunner(unittest.TextTestRunner):
    """Custom TestRunner that uses OutputPathTrackingTestResult."""
    
    def _makeResult(self):
        return OutputPathTrackingTestResult(self.stream, self.descriptions, self.verbosity)


def run_selected_tests(interactive=True, portal=True, dashboard=True, integrated=True, base=True, save_report=True):
    """
    Run selected visualization tests.
    
    All test outputs are saved to the tests/visualization/test_output directory.
    
    Args:
        interactive (bool): Run interactive visualization tests
        portal (bool): Run visualization portal tests
        dashboard (bool): Run dashboard generator tests
        integrated (bool): Run integrated website tests
        base (bool): Run base visualizer tests
        save_report (bool): Save a test report to file
    
    Returns:
        tuple: (test_result, report_path)
    """
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Ensure test_output directory exists
    test_output_dir = Path(__file__).parent / "test_output"
    test_output_dir.mkdir(exist_ok=True)
    
    # Add selected test suites
    if interactive:
        logger.info("Adding interactive visualization tests")
        test_suite.addTest(unittest.makeSuite(TestInteractiveVisualizer))
    
    if portal:
        logger.info("Adding visualization portal tests")
        test_suite.addTest(unittest.makeSuite(TestVisualizationPortal))
    
    if dashboard:
        logger.info("Adding dashboard generator tests")
        test_suite.addTest(unittest.makeSuite(TestDashboardGenerator))
        
    if integrated:
        logger.info("Adding integrated website tests")
        test_suite.addTest(unittest.makeSuite(TestIntegratedWebsite))
        
    if base:
        logger.info("Adding base visualizer tests")
        test_suite.addTest(unittest.makeSuite(TestVisualizer))
    
    # Run tests
    logger.info("Running tests...")
    test_runner = OutputPathTrackingTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)
    
    # Log test results
    logger.info(f"Tests run: {test_result.testsRun}")
    logger.info(f"Errors: {len(test_result.errors)}")
    logger.info(f"Failures: {len(test_result.failures)}")
    
    # Log all output paths
    if hasattr(test_result, 'output_paths') and test_result.output_paths:
        logger.info(f"Found {len(test_result.output_paths)} output files:")
        for path in sorted(set(str(p) for p in test_result.output_paths)):
            logger.info(f"  - {path}")
    
    # Generate report
    report_path = None
    if save_report:
        # Create reports directory if it doesn't exist
        reports_dir = Path("test_reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Generate a timestamp for the report filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"visualization_test_report_{timestamp}.txt"
        
        with open(report_path, 'w') as f:
            f.write("=== P3IF Visualization Test Report ===\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"Tests Run: {test_result.testsRun}\n")
            f.write(f"Errors: {len(test_result.errors)}\n")
            f.write(f"Failures: {len(test_result.failures)}\n\n")
            
            if test_result.errors:
                f.write("=== ERRORS ===\n")
                for test, error in test_result.errors:
                    f.write(f"\n{test}\n")
                    f.write(f"{error}\n")
                f.write("\n")
            
            if test_result.failures:
                f.write("=== FAILURES ===\n")
                for test, failure in test_result.failures:
                    f.write(f"\n{test}\n")
                    f.write(f"{failure}\n")
                f.write("\n")
            
            if hasattr(test_result, 'output_paths') and test_result.output_paths:
                f.write("=== OUTPUT FILES ===\n")
                for path in sorted(set(str(p) for p in test_result.output_paths)):
                    f.write(f"  - {path}\n")
                f.write("\n")
            
            f.write("=== END REPORT ===\n")
        
        logger.info(f"Test report saved to {report_path}")
    
    return test_result, report_path


def main():
    """Parse command line arguments and run tests."""
    parser = argparse.ArgumentParser(description='Run P3IF visualization tests')
    
    parser.add_argument('--interactive', action='store_true',
                        help='Run only interactive visualization tests')
    parser.add_argument('--portal', action='store_true',
                        help='Run only visualization portal tests')
    parser.add_argument('--dashboard', action='store_true',
                        help='Run only dashboard generator tests')
    parser.add_argument('--integrated', action='store_true',
                        help='Run only integrated website tests')
    parser.add_argument('--base', action='store_true',
                        help='Run only base visualizer tests')
    parser.add_argument('--all', action='store_true',
                        help='Run all visualization tests')
    parser.add_argument('--report', action='store_true',
                        help='Save a test report to file')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set debug level if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
        # Also set root logger to debug
        logging.getLogger().setLevel(logging.DEBUG)
    
    # If no specific tests are selected, run all tests
    run_all = args.all or not (args.interactive or args.portal or args.dashboard or args.integrated or args.base)
    
    # Run selected tests
    if run_all:
        logger.info("Running all visualization tests")
        result, report_path = run_selected_tests(
            interactive=True,
            portal=True, 
            dashboard=True,
            integrated=True,
            base=True,
            save_report=args.report
        )
    else:
        logger.info("Running selected visualization tests")
        result, report_path = run_selected_tests(
            interactive=args.interactive,
            portal=args.portal,
            dashboard=args.dashboard,
            integrated=args.integrated,
            base=args.base,
            save_report=args.report
        )
    
    # Return success/failure for CI systems
    return 0 if (len(result.errors) == 0 and len(result.failures) == 0) else 1


if __name__ == "__main__":
    sys.exit(main()) 