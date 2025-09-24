"""
P3IF Visualization Tests Package.

This package contains comprehensive test suites for testing the P3IF
visualization components, including:

1. Interactive Visualizer tests for 3D cube and force-directed graph
2. Dashboard Generator tests for interactive dashboards
3. Visualization Portal tests for the full web interface
4. Integrated Website tests with dataset and component selectors

The test suite is designed to be run using the run_visualization_tests.py script
or via a standard test runner like pytest.
"""

# Configure matplotlib to use the non-interactive Agg backend to prevent popups during tests
import matplotlib
matplotlib.use('Agg')

from test_interactive import TestInteractiveVisualizer
from test_portal import TestVisualizationPortal
from test_dashboard import TestDashboardGenerator
from test_integrated_website import TestIntegratedWebsite

__all__ = [
    'TestInteractiveVisualizer',
    'TestVisualizationPortal',
    'TestDashboardGenerator',
    'TestIntegratedWebsite'
] 