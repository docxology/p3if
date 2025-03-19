"""
Tests for the P3IF interactive visualizations.
"""
import os
import unittest
import json
import tempfile
from pathlib import Path

from p3if.visualization.interactive import InteractiveVisualizer
from p3if.utils.config import Config
from tests.utils import create_test_framework


class TestInteractiveVisualizer(unittest.TestCase):
    """Test cases for the InteractiveVisualizer class."""
    
    def setUp(self):
        """Set up test environment before each test method."""
        self.framework = create_test_framework(
            num_properties=10,
            num_processes=10,
            num_perspectives=10,
            num_relationships=50
        )
        self.config = Config()
        self.visualizer = InteractiveVisualizer(self.framework, self.config)
        
        # Create output directory in the test_output folder instead of a temporary directory
        self.output_path = Path(__file__).parent / "test_output"
        self.output_path.mkdir(exist_ok=True)
        
        # For backward compatibility, also set test_dir
        self.test_dir = type('obj', (object,), {
            'name': str(self.output_path),
            'cleanup': lambda: None  # No-op cleanup function
        })
    
    def tearDown(self):
        """Clean up after each test method."""
        # Don't clean up the test output directory
        # self.test_dir.cleanup()
    
    def test_initialization(self):
        """Test the initialization of the InteractiveVisualizer."""
        self.assertEqual(self.visualizer.framework, self.framework)
        self.assertEqual(self.visualizer.config, self.config)
        self.assertIsNotNone(self.visualizer.logger)
    
    def test_generate_3d_cube_data(self):
        """Test generating data for the 3D cube visualization."""
        cube_data = self.visualizer.generate_3d_cube_data()
        
        # Check that the data structure is correct
        self.assertIn("dimensions", cube_data)
        self.assertIn("connections", cube_data)
        
        # Check dimensions
        dimensions = cube_data["dimensions"]
        self.assertIn("property", dimensions)
        self.assertIn("process", dimensions)
        self.assertIn("perspective", dimensions)
        
        # Check that we have data for each dimension
        self.assertTrue(len(dimensions["property"]) > 0)
        self.assertTrue(len(dimensions["process"]) > 0)
        self.assertTrue(len(dimensions["perspective"]) > 0)
        
        # Check connection data format
        if cube_data["connections"]:
            connection = cube_data["connections"][0]
            self.assertIn("id", connection)
            self.assertIn("property_id", connection)
            self.assertIn("process_id", connection)
            self.assertIn("perspective_id", connection)
            self.assertIn("strength", connection)
            self.assertIn("confidence", connection)
            self.assertIn("x", connection)
            self.assertIn("y", connection)
            self.assertIn("z", connection)
    
    def test_generate_3d_cube_html(self):
        """Test generating HTML for the 3D cube visualization."""
        output_file = self.output_path / "test_cube.html"
        
        # Generate the HTML file
        result_path = self.visualizer.generate_3d_cube_html(
            output_file=output_file,
            title="Test 3D Cube"
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
            self.assertIn("<title>Test 3D Cube</title>", content)
            
            # Check for Three.js inclusion
            self.assertIn("three.min.js", content)
            
            # Check for our data in the script
            self.assertIn("p3ifData", content)
            
            # Check for key visualization components
            self.assertIn("PerspectiveCamera", content)
            self.assertIn("OrbitControls", content)
            self.assertIn("BoxGeometry", content)
    
    def test_generate_force_directed_graph_data(self):
        """Test generating data for the force-directed graph visualization."""
        graph_data = self.visualizer.generate_force_directed_graph_data()
        
        # Check that the data structure is correct
        self.assertIn("nodes", graph_data)
        self.assertIn("links", graph_data)
        
        # Check that we have nodes
        self.assertTrue(len(graph_data["nodes"]) > 0)
        
        # Check node data format
        if graph_data["nodes"]:
            node = graph_data["nodes"][0]
            self.assertIn("id", node)
            self.assertIn("name", node)
            self.assertIn("type", node)
        
        # Check link data format if we have links
        if graph_data["links"]:
            link = graph_data["links"][0]
            self.assertIn("source", link)
            self.assertIn("target", link)
            self.assertIn("strength", link)
            self.assertIn("type", link)
    
    def test_generate_force_directed_graph_html(self):
        """Test generating HTML for the force-directed graph visualization."""
        output_file = self.output_path / "test_graph.html"
        
        # Generate the HTML file
        result_path = self.visualizer.generate_force_directed_graph_html(
            output_file=output_file,
            title="Test Force Graph"
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
            self.assertIn("<title>Test Force Graph</title>", content)
            
            # Check for D3.js inclusion
            self.assertIn("d3.v7.min.js", content)
            
            # Check for our data in the script
            self.assertIn("graphData", content)
            
            # Check for key visualization components
            self.assertIn("forceSimulation", content)
            self.assertIn("forceManyBody", content)
            self.assertIn("forceCenter", content)
            
    def test_3d_cube_with_dataset_selection(self):
        """Test generating a 3D cube visualization with dataset selection capabilities."""
        output_file = self.output_path / "test_cube_with_datasets.html"
        
        # Define test datasets
        datasets = [
            {"id": "default", "name": "Default Dataset"},
            {"id": "alternative", "name": "Alternative Dataset"}
        ]
        
        # Generate the HTML file with dataset selection
        result_path = self.visualizer.generate_3d_cube_html(
            output_file=output_file,
            title="3D Cube with Dataset Selection",
            include_dataset_selector=True,
            datasets=datasets
        )
        
        # Check that the file was created
        self.assertTrue(output_file.exists())
        self.assertTrue(output_file.stat().st_size > 0)
        self.assertEqual(result_path, output_file)
        
        # Check the content of the file
        with open(output_file, 'r') as f:
            content = f.read()
            
            # Check for dataset selector
            self.assertIn("dataset-selector", content)
            
            # Check that datasets are included
            for dataset in datasets:
                self.assertIn(f"value=\"{dataset['id']}\"", content)
                self.assertIn(dataset["name"], content)
            
            # Check for JavaScript to handle dataset changes
            self.assertIn("function loadDataset", content)
            self.assertIn("addEventListener", content)
            
            # Check that the 3D cube visualization is still there
            self.assertIn("PerspectiveCamera", content)
            self.assertIn("OrbitControls", content)
            self.assertIn("BoxGeometry", content)


if __name__ == '__main__':
    unittest.main() 