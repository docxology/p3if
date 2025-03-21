"""
Tests for the fix_visualization_paths.py script.
"""
import os
import unittest
import tempfile
from pathlib import Path
import shutil
import sys

# Add the project root to the path so we can import the script
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from p3if.scripts.fix_visualization_paths import VisualizationFixer
except ImportError:
    # Fallback import path
    from scripts.fix_visualization_paths import VisualizationFixer


class TestVisualizationFixer(unittest.TestCase):
    """Test the VisualizationFixer class."""
    
    def setUp(self):
        """Set up a temporary directory structure for testing."""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        
        # Create necessary subdirectories
        self.output_dir = self.base_dir / 'output'
        self.output_dir.mkdir()
        
        self.portal_output_dir = self.output_dir / 'portal'
        self.portal_output_dir.mkdir()
        
        self.portal_viz_dir = self.portal_output_dir / 'visualizations'
        self.portal_viz_dir.mkdir()
        
        self.website_dir = self.base_dir / 'website'
        self.website_dir.mkdir()
        
        self.dist_dir = self.website_dir / 'dist'
        self.dist_dir.mkdir()
        
        # Change directory to the temporary base dir
        self.original_dir = os.getcwd()
        os.chdir(self.base_dir)
        
        # Create the fixer
        self.fixer = VisualizationFixer()
        
        # Override the paths to use our test paths
        self.fixer.base_dir = self.base_dir
        self.fixer.output_dir = self.output_dir
        self.fixer.portal_output_dir = self.portal_output_dir
        self.fixer.website_dir = self.website_dir
        self.fixer.dist_dir = self.dist_dir
        self.fixer.visualizations_dir = self.dist_dir / 'visualizations'
    
    def tearDown(self):
        """Clean up the temporary directory."""
        os.chdir(self.original_dir)
        self.temp_dir.cleanup()
    
    def test_create_directory_structure(self):
        """Test that directory structure creation works."""
        self.fixer.create_directory_structure()
        
        # Check that visualization directories were created
        for viz_type in ['3d-cube', 'network', 'dashboard', 'matrix']:
            viz_dir = self.fixer.visualizations_dir / viz_type
            self.assertTrue(viz_dir.exists(), f"{viz_dir} should exist")
            self.assertTrue(viz_dir.is_dir(), f"{viz_dir} should be a directory")
            
            # Check that index.html was created
            index_file = viz_dir / 'index.html'
            self.assertTrue(index_file.exists(), f"{index_file} should exist")
            
        # Check that assets directories were created
        assets_dir = self.fixer.dist_dir / 'assets'
        for asset_type in ['css', 'js', 'images', 'data']:
            asset_type_dir = assets_dir / asset_type
            self.assertTrue(asset_type_dir.exists(), f"{asset_type_dir} should exist")
            self.assertTrue(asset_type_dir.is_dir(), f"{asset_type_dir} should be a directory")
    
    def test_copy_portal_visualizations(self):
        """Test copying portal visualizations."""
        # Create the directory structure first
        self.fixer.create_directory_structure()
        
        # Create source files
        self._create_test_file(self.portal_viz_dir / '3d-cube.html', "<html><body>3D Cube Test</body></html>")
        self._create_test_file(self.portal_viz_dir / 'force-graph.html', "<html><body>Force Graph Test</body></html>")
        
        # Create overview directory with test images
        overview_dir = self.portal_viz_dir / 'overview'
        overview_dir.mkdir()
        self._create_test_file(overview_dir / 'dashboard1.png', "test image 1")
        self._create_test_file(overview_dir / 'dashboard2.png', "test image 2")
        
        # Run the copy function
        self.fixer.copy_portal_visualizations()
        
        # Check that the files were copied to the correct locations
        self._assert_file_contains(
            self.fixer.visualizations_dir / '3d-cube' / 'index.html', 
            "3D Cube Test"
        )
        self._assert_file_contains(
            self.fixer.visualizations_dir / 'network' / 'index.html', 
            "Force Graph Test"
        )
        
        # Check that the dashboard was created and contains links to the images
        dashboard_index = self.fixer.visualizations_dir / 'dashboard' / 'index.html'
        dashboard_content = self._read_file(dashboard_index)
        self.assertIn("dashboard1.png", dashboard_content)
        self.assertIn("dashboard2.png", dashboard_content)
        
        # Check that the images were copied
        dashboard_dir = self.fixer.visualizations_dir / 'dashboard'
        self._assert_file_contains(dashboard_dir / 'dashboard1.png', "test image 1")
        self._assert_file_contains(dashboard_dir / 'dashboard2.png', "test image 2")
    
    def _create_test_file(self, path, content):
        """Helper to create a test file with content."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
    
    def _read_file(self, path):
        """Helper to read a file's content."""
        with open(path, 'r') as f:
            return f.read()
    
    def _assert_file_contains(self, path, content):
        """Assert that a file exists and contains the given content."""
        self.assertTrue(path.exists(), f"File {path} should exist")
        file_content = self._read_file(path)
        self.assertIn(content, file_content, 
                     f"File {path} should contain '{content}', but got: '{file_content}'")


if __name__ == '__main__':
    unittest.main() 