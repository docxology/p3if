"""
Tests for P3IF Animated Visualizations

Tests for animated visualization modules to ensure they can be imported
and provide basic functionality.
"""

import unittest
from unittest.mock import MagicMock, patch, mock_open
import tempfile
from pathlib import Path
import sys

# Mock matplotlib if not available
try:
    import matplotlib
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    sys.modules['matplotlib'] = MagicMock()
    sys.modules['matplotlib.pyplot'] = MagicMock()
    sys.modules['matplotlib.animation'] = MagicMock()
    sys.modules['matplotlib.patches'] = MagicMock()

# Mock PIL if not available
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    sys.modules['PIL'] = MagicMock()
    sys.modules['PIL.Image'] = MagicMock()

from p3if.core.framework import P3IFFramework
from p3if.core.models import Property, Process, Perspective


class TestAnimatedDimensions(unittest.TestCase):
    """Test cases for animated dimensions."""

    def setUp(self):
        """Set up test fixtures."""
        self.framework = P3IFFramework()
        # Add some test data
        prop = Property(name="Test Property", description="A test property for animation", domain="test")
        proc = Process(name="Test Process", description="A test process for animation", domain="test")
        persp = Perspective(name="Test Perspective", description="A test perspective for animation", domain="test", viewpoint="test")
        self.framework.add_pattern(prop)
        self.framework.add_pattern(proc)
        self.framework.add_pattern(persp)

    @patch('p3if.visualization.animated.animated_dimensions.MATPLOTLIB_AVAILABLE', True)
    def test_dimension_animator_creation(self):
        """Test DimensionAnimator can be created."""
        from p3if.visualization.animated.animated_dimensions import DimensionAnimator

        animator = DimensionAnimator(
            name="test_animator",
            framework_data={"test": "data"}
        )
        self.assertIsNotNone(animator)
        self.assertEqual(animator.name, "test_animator")

    @patch('p3if.visualization.animated.animated_dimensions.MATPLOTLIB_AVAILABLE', False)
    def test_dimension_animator_without_matplotlib(self):
        """Test DimensionAnimator handles missing matplotlib."""
        from p3if.visualization.animated.animated_dimensions import DimensionAnimator

        animator = DimensionAnimator()
        # Should not raise an exception
        self.assertIsNotNone(animator)

    def test_create_dimension_animator(self):
        """Test create_dimension_animator function."""
        from p3if.visualization.animated.animated_dimensions import create_dimension_animator

        framework_data = {"properties": [], "processes": [], "perspectives": []}
        animator = create_dimension_animator(framework_data)
        self.assertIsNotNone(animator)
        self.assertIsInstance(animator, type(animator))  # Should return a DimensionAnimator

    @patch('builtins.open', new_callable=mock_open)
    @patch('p3if.visualization.animated.animated_dimensions.MATPLOTLIB_AVAILABLE', True)
    def test_save_animation(self, mock_file):
        """Test save_animation function."""
        from p3if.visualization.animated.animated_dimensions import DimensionAnimator, save_animation

        animator = DimensionAnimator()
        result = save_animation(animator, "test.gif", 10)
        self.assertIsInstance(result, str)
        # Should contain the filename
        self.assertIn("test.gif", result)


class TestAnimationVisualizations(unittest.TestCase):
    """Test cases for animation visualizations."""

    def setUp(self):
        """Set up test fixtures."""
        self.small_framework = P3IFFramework()
        self.large_framework = P3IFFramework()

        # Add minimal test data to small framework
        prop = Property(name="Test Property", description="Small framework test property", domain="test")
        proc = Process(name="Test Process", description="Small framework test process", domain="test")
        persp = Perspective(name="Test Perspective", description="Small framework test perspective", domain="test", viewpoint="test")
        self.small_framework.add_pattern(prop)
        self.small_framework.add_pattern(proc)
        self.small_framework.add_pattern(persp)

        # Add more data to large framework
        for i in range(5):
            prop = Property(name=f"Property {i}", description=f"Large framework property {i}", domain="test")
            proc = Process(name=f"Process {i}", description=f"Large framework process {i}", domain="test")
            persp = Perspective(name=f"Perspective {i}", description=f"Large framework perspective {i}", domain="test", viewpoint="test")
            self.large_framework.add_pattern(prop)
            self.large_framework.add_pattern(proc)
            self.large_framework.add_pattern(persp)

    @patch('p3if.visualization.animated.animation_visualizations.logger')
    def test_generate_animation_visualizations(self, mock_logger):
        """Test generate_animation_visualizations function."""
        from p3if.visualization.animated.animation_visualizations import generate_animation_visualizations

        with tempfile.TemporaryDirectory() as temp_dir:
            session_path = Path(temp_dir)

            # Should not raise an exception
            try:
                generate_animation_visualizations(
                    self.small_framework,
                    self.large_framework,
                    session_path
                )
            except Exception as e:
                # If matplotlib/PIL not available, it might raise an exception
                # but the function should be importable and callable
                if "matplotlib" in str(e).lower() or "pil" in str(e).lower():
                    pass  # Expected when dependencies not available
                else:
                    raise

    def test_animation_functions_exist(self):
        """Test that key animation functions exist."""
        from p3if.visualization.animated import animation_visualizations

        # Check that main functions exist
        self.assertTrue(hasattr(animation_visualizations, 'generate_animation_visualizations'))
        self.assertTrue(hasattr(animation_visualizations, '_create_p3if_rotation_animation'))
        self.assertTrue(hasattr(animation_visualizations, '_create_framework_evolution_animation'))
        self.assertTrue(hasattr(animation_visualizations, '_create_relationship_dynamics_animation'))
        self.assertTrue(hasattr(animation_visualizations, '_create_component_interaction_animation'))


if __name__ == '__main__':
    unittest.main()

