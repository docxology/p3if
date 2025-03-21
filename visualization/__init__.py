"""
P3IF Visualization Package.

This package provides visualization capabilities for P3IF data, including:
1. Interactive visualizations (3D cube, force-directed graphs)
2. Matrix visualizations (patterns, domains, relationships)
3. Network visualizations
4. Dashboard generation
5. Visualization portal

All visualizers are built on the base Visualizer class.
"""

# Configure matplotlib to use the non-interactive Agg backend by default
# This ensures that figures are not displayed during batch processing or tests
import matplotlib
matplotlib.use('Agg')

from visualization.base import Visualizer
from visualization.matrix import MatrixVisualizer
from visualization.network import NetworkVisualizer
from visualization.interactive import InteractiveVisualizer
from visualization.dashboard import DashboardGenerator
from visualization.portal import VisualizationPortal

# For backward compatibility with p3if.visualization imports
try:
    import sys
    sys.modules['p3if.visualization'] = sys.modules[__name__]
    sys.modules['p3if.visualization.base'] = sys.modules['visualization.base']
    sys.modules['p3if.visualization.portal'] = sys.modules['visualization.portal']
    sys.modules['p3if.visualization.network'] = sys.modules['visualization.network']
    sys.modules['p3if.visualization.matrix'] = sys.modules['visualization.matrix']
    sys.modules['p3if.visualization.dashboard'] = sys.modules['visualization.dashboard']
    sys.modules['p3if.visualization.interactive'] = sys.modules['visualization.interactive']
except Exception:
    pass

__version__ = '0.1.0'

__all__ = [
    'Visualizer',
    'MatrixVisualizer',
    'NetworkVisualizer',
    'InteractiveVisualizer',
    'DashboardGenerator',
    'VisualizationPortal'
] 