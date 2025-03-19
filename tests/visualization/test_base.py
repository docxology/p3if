"""
Tests for P3IF base visualizer.

This module contains tests for the base visualization class in the P3IF framework.
"""
import pytest
import os
import tempfile
import matplotlib.pyplot as plt
from pathlib import Path

from p3if.core.framework import P3IFFramework
from p3if.core.models import Property, Process, Perspective
from p3if.visualization.base import Visualizer
from p3if.utils.config import Config


@pytest.fixture
def framework_with_domains():
    """Create a framework with patterns from different domains."""
    framework = P3IFFramework()
    
    # Add properties from different domains
    framework.add_pattern(Property(name="Property 1", domain="domain1"))
    framework.add_pattern(Property(name="Property 2", domain="domain2"))
    framework.add_pattern(Property(name="Property 3", domain="domain3"))
    
    # Add processes from different domains
    framework.add_pattern(Process(name="Process 1", domain="domain1"))
    framework.add_pattern(Process(name="Process 2", domain="domain2"))
    
    # Add perspectives from different domains
    framework.add_pattern(Perspective(name="Perspective 1", domain="domain1"))
    framework.add_pattern(Perspective(name="Perspective 2", domain="domain3"))
    
    return framework


class TestVisualizer:
    """Tests for the Visualizer base class."""
    
    def test_initialization(self):
        """Test initializing a visualizer."""
        framework = P3IFFramework()
        visualizer = Visualizer(framework)
        
        assert visualizer.framework == framework
        assert visualizer.config is not None
        assert hasattr(visualizer, 'colormap')
        assert hasattr(visualizer, 'node_size')
        assert hasattr(visualizer, 'edge_width')
        assert hasattr(visualizer, 'figsize')
        assert hasattr(visualizer, 'dpi')
    
    def test_initialization_with_config(self):
        """Test initializing a visualizer with custom config."""
        framework = P3IFFramework()
        
        # Create a config with custom settings
        config = Config()
        config._config["visualization"] = {
            "default_style": "custom",
            "themes": {
                "custom": {
                    "colormap": "plasma",
                    "node_size": 100,
                    "edge_width": 2.0,
                    "figsize": (10, 6),
                    "dpi": 150
                }
            }
        }
        
        visualizer = Visualizer(framework, config)
        
        assert visualizer.colormap == "plasma"
        assert visualizer.node_size == 100
        assert visualizer.edge_width == 2.0
        assert visualizer.figsize == (10, 6)
        assert visualizer.dpi == 150
    
    def test_get_color_palette(self):
        """Test getting a color palette."""
        framework = P3IFFramework()
        visualizer = Visualizer(framework)
        
        # Get a palette of 5 colors
        colors = visualizer.get_color_palette(5)
        
        assert len(colors) == 5
        assert all(isinstance(c, str) and c.startswith('#') for c in colors)
    
    def test_get_domain_colors(self, framework_with_domains):
        """Test getting domain colors."""
        visualizer = Visualizer(framework_with_domains)
        
        domain_colors = visualizer.get_domain_colors()
        
        assert len(domain_colors) == 3
        assert "domain1" in domain_colors
        assert "domain2" in domain_colors
        assert "domain3" in domain_colors
        assert all(isinstance(c, str) and c.startswith('#') for c in domain_colors.values())
    
    def test_get_pattern_type_colors(self):
        """Test getting pattern type colors."""
        framework = P3IFFramework()
        visualizer = Visualizer(framework)
        
        type_colors = visualizer.get_pattern_type_colors()
        
        assert len(type_colors) == 3
        assert "property" in type_colors
        assert "process" in type_colors
        assert "perspective" in type_colors
    
    def test_setup_figure(self):
        """Test setting up a matplotlib figure."""
        framework = P3IFFramework()
        visualizer = Visualizer(framework)
        
        # Test single subplot
        fig, ax = visualizer.setup_figure()
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
        
        # Test multiple subplots
        fig, axes = visualizer.setup_figure(nrows=2, ncols=2)
        assert isinstance(fig, plt.Figure)
        assert axes.shape == (2, 2)
        plt.close(fig)
        
        # Test custom figsize
        fig, ax = visualizer.setup_figure(figsize=(8, 6))
        assert fig.get_size_inches()[0] == 8
        assert fig.get_size_inches()[1] == 6
        plt.close(fig)
    
    def test_save_figure(self):
        """Test saving a figure to file."""
        framework = P3IFFramework()
        visualizer = Visualizer(framework)
        
        # Create a simple figure
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot([1, 2, 3], [1, 4, 9])
        
        # Save to a temporary file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test PNG format
            png_path = os.path.join(temp_dir, "test_figure.png")
            visualizer.save_figure(fig, png_path, title="Test Figure")
            assert os.path.exists(png_path)
            
            # Test PDF format
            pdf_path = os.path.join(temp_dir, "test_figure.pdf")
            visualizer.save_figure(fig, pdf_path)
            assert os.path.exists(pdf_path)
            
            # Test with nested directory
            nested_path = os.path.join(temp_dir, "subfolder", "test_figure.png")
            visualizer.save_figure(fig, nested_path)
            assert os.path.exists(nested_path)
        
        plt.close(fig) 