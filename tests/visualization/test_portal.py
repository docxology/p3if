"""
Tests for the P3IF Visualization Portal.
"""
import os
import unittest
import tempfile
from pathlib import Path
import re
from bs4 import BeautifulSoup

from p3if.visualization.portal import VisualizationPortal
from p3if.utils.config import Config
from tests.utils import create_test_framework, create_multi_domain_test_framework


class TestVisualizationPortal(unittest.TestCase):
    """Test cases for the VisualizationPortal class."""
    
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
        
        # Initialize the portal
        self.portal = VisualizationPortal(self.framework, self.config)
        
        # Initialize multi-domain portal
        self.multi_domain_portal = VisualizationPortal(self.multi_domain_framework, self.config)
    
    def tearDown(self):
        """Clean up after each test method."""
        # Don't clean up the test output directory
        # self.test_dir.cleanup()
    
    def test_initialization(self):
        """Test the initialization of the VisualizationPortal."""
        self.assertEqual(self.portal.framework, self.framework)
        self.assertEqual(self.portal.config, self.config)
        self.assertIsNotNone(self.portal.logger)
    
    def test_generate_dataset_dropdown(self):
        """Test generating the dataset dropdown HTML."""
        # Create a test dataset list
        datasets = [
            {"id": "dataset1", "name": "Test Dataset 1"},
            {"id": "dataset2", "name": "Test Dataset 2"},
            {"id": "dataset3", "name": "Test Dataset 3"}
        ]
        
        dropdown_html = self.portal.generate_dataset_dropdown(datasets)
        
        # Check that the dropdown contains the expected elements
        self.assertIn("<select", dropdown_html)
        self.assertIn("id=\"dataset-selector\"", dropdown_html)
        
        # Check that all datasets are in the dropdown
        for dataset in datasets:
            self.assertIn(f"value=\"{dataset['id']}\"", dropdown_html)
            self.assertIn(f">{dataset['name']}<", dropdown_html)
    
    def test_generate_component_selector(self):
        """Test generating the component selector HTML."""
        # Define test components
        components = [
            {"id": "3d-cube", "name": "3D Cube", "description": "3D visualization of P3IF relationships"},
            {"id": "network", "name": "Network Graph", "description": "Network visualization of P3IF elements"},
            {"id": "matrix", "name": "Matrix View", "description": "Matrix visualization of P3IF relationships"}
        ]
        
        selector_html = self.portal.generate_component_selector(components)
        
        # Check that the selector contains the expected elements
        self.assertIn("<div", selector_html)
        self.assertIn("class=\"component-selector\"", selector_html)
        
        # Check that all components are in the selector
        for component in components:
            self.assertIn(f"data-component=\"{component['id']}\"", selector_html)
            self.assertIn(f">{component['name']}<", selector_html)
            self.assertIn(component['description'], selector_html)
    
    def test_generate_full_portal_html(self):
        """Test generating the full portal HTML."""
        output_file = self.output_path / "test_portal.html"
        
        # Create test datasets
        test_datasets = [
            {"id": "dataset1", "name": "Test Dataset 1"},
            {"id": "dataset2", "name": "Test Dataset 2"},
            {"id": "dataset3", "name": "Test Dataset 3"}
        ]
        
        # Create test components
        test_components = [
            {"id": "cube", "name": "3D Cube", "description": "Interactive 3D cube visualization"},
            {"id": "network", "name": "Network", "description": "Force-directed graph visualization"},
            {"id": "matrix", "name": "Matrix", "description": "Matrix visualizations"}
        ]
        
        # Generate the HTML file
        result_path = self.portal.generate_portal(
            output_file=output_file,
            title="Test P3IF Portal",
            include_dataset_dropdown=True,
            datasets=test_datasets,
            include_component_selector=True,
            components=test_components
        )
        
        # Check that the file was created
        self.assertTrue(output_file.exists())
        self.assertTrue(output_file.stat().st_size > 0)
        self.assertEqual(result_path, output_file)
        
        # Check the content of the file
        with open(output_file, 'r') as f:
            content = f.read()
            
            # Check for key HTML elements
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("<title>Test P3IF Portal</title>", content)
            
            # Check for dataset dropdown
            self.assertIn("id=\"dataset-selector\"", content)
            
            # Check for component selector
            self.assertIn("class=\"component-selector\"", content)
            self.assertIn("3D Cube", content)
            self.assertIn("Network", content)
            self.assertIn("Matrix", content)
            
            # Check for key JavaScript functionality
            self.assertIn("function loadDataset", content)
            self.assertIn("DOMContentLoaded", content)
    
    def test_multi_domain_portal(self):
        """Test generating a portal with multi-domain data."""
        output_file = self.output_path / "test_multi_domain_portal.html"
        
        # Generate the HTML file
        result_path = self.multi_domain_portal.generate_portal(
            output_file=output_file,
            title="Multi-Domain P3IF Portal",
            include_dataset_dropdown=True,
            include_component_selector=True
        )
        
        # Check that the file was created
        self.assertTrue(output_file.exists())
        self.assertTrue(output_file.stat().st_size > 0)
        
        # Check the content of the file
        with open(output_file, 'r') as f:
            content = f.read()
            
            # Check for domain-specific content
            self.assertIn("Domain1", content)
            self.assertIn("Domain2", content)
            self.assertIn("Domain3", content)
            
            # Parse the HTML to check domain tabs
            soup = BeautifulSoup(content, 'html.parser')
            domain_tabs = soup.select(".domain-tab")
            self.assertGreaterEqual(len(domain_tabs), 3)  # At least 3 domain tabs
    
    def test_portal_css(self):
        """Test that the portal includes appropriate CSS styling."""
        output_file = self.output_path / "test_css_portal.html"
        
        # Generate the HTML file
        self.portal.generate_portal(
            output_file=output_file,
            title="Test CSS Portal"
        )
        
        # Check for CSS content
        with open(output_file, 'r') as f:
            content = f.read()
            
            # Find the CSS section
            css_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
            self.assertIsNotNone(css_match)
            
            css_content = css_match.group(1)
            
            # Check for key styling elements
            self.assertIn("body", css_content)
            self.assertIn("header", css_content)
            self.assertIn("nav", css_content)
            self.assertIn("main", css_content)
            self.assertIn("footer", css_content)
            
            # Check for responsive design
            self.assertIn("@media", css_content)
    
    def test_portal_javascript(self):
        """Test that the portal includes appropriate JavaScript functionality."""
        output_file = self.output_path / "test_js_portal.html"
        
        # Generate the HTML file
        self.portal.generate_portal(
            output_file=output_file,
            title="Test JS Portal"
        )
        
        # Check for JavaScript content
        with open(output_file, 'r') as f:
            content = f.read()
            
            # Find the JavaScript section
            js_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
            self.assertIsNotNone(js_match)
            
            js_content = js_match.group(1)
            
            # Check for key JavaScript functionality
            self.assertIn("document.addEventListener", js_content)
            self.assertIn("function", js_content)
            
            # Check for event handlers
            self.assertIn("addEventListener", js_content)
            
            # Check for DOM manipulation
            self.assertIn("document.getElementById", js_content)
            self.assertIn("querySelector", js_content)


if __name__ == '__main__':
    unittest.main() 