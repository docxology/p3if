#!/usr/bin/env python3
"""
Tests for the dashboard generator in the P3IF framework.
"""
import unittest
import tempfile
from pathlib import Path
import sys
import os
import re

# Add the project root to the path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from visualization.dashboard import DashboardGenerator
from utils.config import Config
from tests.utils import create_test_framework, create_multi_domain_test_framework


class TestDashboardGenerator(unittest.TestCase):
    """Test cases for the DashboardGenerator class."""
    
    def setUp(self):
        """Set up test environment before each test method."""
        # Create standard test framework
        self.framework = create_test_framework(
            num_properties=10,
            num_processes=10,
            num_perspectives=10,
            num_relationships=50
        )
        
        # Create multi-domain test framework
        self.multi_domain_framework = create_multi_domain_test_framework(
            domains=["Domain1", "Domain2", "Domain3"],
            patterns_per_domain=5,
            relationships_per_domain=15,
            cross_domain_relationships=10
        )
        
        self.config = Config()
        
        # Create output directory in the test_output folder instead of a temporary directory
        self.output_path = Path(__file__).parent / "test_output"
        self.output_path.mkdir(exist_ok=True)
        
        # For backward compatibility, also set test_dir
        self.test_dir = type('obj', (object,), {
            'name': str(self.output_path),
            'cleanup': lambda: None  # No-op cleanup function
        })
        
        # Initialize the dashboard generator
        self.dashboard = DashboardGenerator(self.framework, self.config)
        
        # Initialize multi-domain dashboard
        self.multi_domain_dashboard = DashboardGenerator(self.multi_domain_framework, self.config)
    
    def tearDown(self):
        """Clean up after each test method."""
        # Don't clean up the test output directory
        # self.test_dir.cleanup()
    
    def test_initialization(self):
        """Test the initialization of the DashboardGenerator."""
        self.assertEqual(self.dashboard.framework, self.framework)
        self.assertEqual(self.dashboard.config, self.config)
        self.assertIsNotNone(self.dashboard.logger)
    
    def test_generate_overview_dashboard(self):
        """Test generating an overview dashboard."""
        output_dir = self.output_path / "test_overview_dashboard"
        
        # Generate the dashboard 
        result = self.dashboard.generate_overview_dashboard(output_dir=output_dir)
        
        # Check that all expected visualizations were created
        for viz_name, viz_path in result.items():
            self.assertTrue(viz_path.exists())
            self.assertTrue(viz_path.stat().st_size > 0)
        
        # Check for specific expected files
        self.assertTrue((output_dir / "network_overview.png").exists())
        self.assertTrue((output_dir / "domain_network.png").exists())
        self.assertTrue((output_dir / "matrix_property_process.png").exists())
        self.assertTrue((output_dir / "matrix_property_perspective.png").exists())
        self.assertTrue((output_dir / "matrix_process_perspective.png").exists())
    
    def test_generate_domain_dashboard(self):
        """Test generating a domain-specific dashboard."""
        output_dir = self.output_path / "test_domain_dashboard"
        
        # Generate the dashboard for multi-domain framework
        result = self.multi_domain_dashboard.generate_domain_dashboard(
            domain="Domain1",
            output_dir=output_dir
        )
        
        # Check that visualization files were created
        for viz_name, viz_path in result.items():
            self.assertTrue(viz_path.exists())
            self.assertTrue(viz_path.stat().st_size > 0)
        
        # Check for domain-specific files
        self.assertTrue((output_dir / "pattern_distribution.png").exists())
        self.assertTrue((output_dir / "property_similarity.png").exists())
        self.assertTrue((output_dir / "process_similarity.png").exists())
        self.assertTrue((output_dir / "perspective_similarity.png").exists())
    
    def test_generate_comparison_dashboard(self):
        """Test generating a comparison dashboard for multiple domains."""
        output_dir = self.output_path / "test_comparison_dashboard"
        
        # Generate the dashboard for multi-domain framework
        result = self.multi_domain_dashboard.generate_comparative_dashboard(
            domains=["Domain1", "Domain2"],
            output_dir=output_dir
        )
        
        # Check that visualization files were created
        for viz_name, viz_path in result.items():
            self.assertTrue(viz_path.exists())
            self.assertTrue(viz_path.stat().st_size > 0)
        
        # Check for expected comparison files
        self.assertTrue((output_dir / "domain_metrics.png").exists())
        self.assertTrue((output_dir / "domain_similarity.png").exists())
        self.assertTrue((output_dir / "domain_network.png").exists())
        self.assertTrue((output_dir / "pattern_correlation.png").exists())
        self.assertTrue((output_dir / "comparative_pattern_distribution.png").exists())
    
    def test_generate_interactive_filters(self):
        """Test generating interactive filters for the dashboard."""
        filter_html = self.dashboard.generate_interactive_filters([
            {"id": "pattern-type", "name": "Pattern Type", "options": ["Property", "Process", "Perspective"]},
            {"id": "strength", "name": "Relationship Strength", "options": ["Low", "Medium", "High"]}
        ])
        
        # Check filter HTML
        self.assertIn("filter-container", filter_html)
        self.assertIn("pattern-type", filter_html)
        self.assertIn("strength", filter_html)
        
        # Check options
        self.assertIn("Property", filter_html)
        self.assertIn("Process", filter_html)
        self.assertIn("Perspective", filter_html)
        self.assertIn("Low", filter_html)
        self.assertIn("Medium", filter_html)
        self.assertIn("High", filter_html)
    
    def test_generate_full_dashboard_with_dataset_selector(self):
        """Test generating a full dashboard with dataset selector."""
        output_file = self.output_path / "test_full_dashboard.html"
        
        # Define test datasets
        datasets = [
            {"id": "dataset1", "name": "Test Dataset 1"},
            {"id": "dataset2", "name": "Test Dataset 2"},
            {"id": "dataset3", "name": "Test Dataset 3"}
        ]
        
        # Generate the HTML file
        result_path = self.dashboard.generate_full_dashboard(
            output_file=output_file,
            title="Full Dashboard with Dataset Selector",
            datasets=datasets
        )
        
        # Check that the file was created
        self.assertTrue(output_file.exists())
        self.assertTrue(output_file.stat().st_size > 0)
        
        # Check the content of the file
        with open(output_file, 'r') as f:
            content = f.read()
            
            # Check for dataset selector
            self.assertIn("dataset-selector", content)
            
            # Check that all datasets are in the dropdown
            for dataset in datasets:
                self.assertIn(dataset["id"], content)
                self.assertIn(dataset["name"], content)
            
            # Check for dashboard sections
            self.assertIn("overview-section", content)
            self.assertIn("details-section", content)
            self.assertIn("metrics-section", content)
            
            # Check for interactive elements
            self.assertIn("filter-section", content)
            self.assertIn("onclick", content)
            self.assertIn("addEventListener", content)
    
    def test_dashboard_responsive_design(self):
        """Test that the dashboard has responsive design elements."""
        output_file = self.output_path / "test_responsive_dashboard.html"
        
        # Generate a full dashboard with responsive design
        self.dashboard.generate_full_dashboard(
            output_file=output_file,
            title="Responsive Dashboard Test"
        )
        
        # Check that the file was created
        self.assertTrue(output_file.exists())
        
        # Check for responsive design elements in CSS
        with open(output_file, 'r') as f:
            content = f.read()
            
            # Check for responsive design CSS
            self.assertIn("@media", content)  # Media queries
            self.assertIn("max-width", content)  # Responsive width settings
            self.assertIn("grid-template-columns", content)  # CSS Grid layout
            
            # Check for responsive container
            self.assertIn("dashboard-container", content)
            self.assertIn("overview-section", content)


if __name__ == '__main__':
    unittest.main() 