"""
Tests for the ensure_website_references.py script.
"""
import os
import unittest
import tempfile
from pathlib import Path
import sys
import shutil

# Add the project root to the path so we can import the script
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from p3if.scripts.ensure_website_references import WebsiteReferenceFixer
except ImportError:
    # Fallback import path
    from scripts.ensure_website_references import WebsiteReferenceFixer


class TestWebsiteReferenceFixer(unittest.TestCase):
    """Test the WebsiteReferenceFixer class."""
    
    def setUp(self):
        """Set up a temporary directory structure for testing."""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        
        # Create necessary subdirectories
        self.p3if_dir = self.base_dir / 'p3if'
        self.p3if_dir.mkdir()
        
        self.scripts_dir = self.p3if_dir / 'scripts'
        self.scripts_dir.mkdir()
        
        self.output_dir = self.base_dir / 'output'
        self.output_dir.mkdir()
        
        self.docs_dir = self.base_dir / 'docs'
        self.docs_dir.mkdir()
        
        self.website_dir = self.base_dir / 'website'
        self.website_dir.mkdir()
        
        self.dist_dir = self.website_dir / 'dist'
        self.dist_dir.mkdir()
        
        # Change directory to the temporary base dir
        self.original_dir = os.getcwd()
        os.chdir(self.base_dir)
        
        # Create the fixer
        self.fixer = WebsiteReferenceFixer()
        
        # Override the paths to use our test paths
        self.fixer.base_dir = self.base_dir
        self.fixer.p3if_dir = self.p3if_dir
        self.fixer.scripts_dir = self.scripts_dir
        self.fixer.output_dir = self.output_dir
        self.fixer.docs_dir = self.docs_dir
        self.fixer.website_dir = self.website_dir
        self.fixer.dist_dir = self.dist_dir
    
    def tearDown(self):
        """Clean up the temporary directory."""
        os.chdir(self.original_dir)
        self.temp_dir.cleanup()
    
    def test_fix_html_references(self):
        """Test fixing HTML references."""
        # Create test HTML files with incorrect references
        visualizations_dir = self.dist_dir / 'visualizations'
        visualizations_dir.mkdir()
        
        # Create a test HTML file with incorrect documentation links
        index_html = self.dist_dir / 'index.html'
        self._create_test_file(index_html, """
        <!DOCTYPE html>
        <html>
        <head>
            <title>P3IF Test</title>
            <link rel="stylesheet" href="invalid/path/styles.css">
        </head>
        <body>
            <a href="documentation/invalid_link.html">Invalid Doc Link</a>
            <a href="/visualizations/3d-cube">3D Cube</a>
            <script src="invalid/path/script.js"></script>
        </body>
        </html>
        """)
        
        # Create test documentation file
        self._create_test_file(self.docs_dir / 'invalid_link.html', "<html><body>Test Doc</body></html>")
        
        # Run the fix function
        self.fixer.fix_html_references()
        
        # Check that the references were fixed
        with open(index_html, 'r') as f:
            content = f.read()
            # Documentation link should be fixed
            self.assertIn('href="/docs/invalid_link.html"', content)
            # Visualization link should be fixed
            self.assertIn('href="/visualizations/3d-cube/"', content)
    
    def test_copy_documentation_to_website(self):
        """Test copying documentation to the website directory."""
        # Create test documentation files
        self._create_test_file(self.docs_dir / 'test_doc.md', "# Test Document\n\nThis is a test.")
        self._create_test_file(self.docs_dir / 'another_doc.md', "# Another Document\n\nThis is another test.")
        
        # Create a subdirectory with documentation
        docs_subdir = self.docs_dir / 'subdir'
        docs_subdir.mkdir()
        self._create_test_file(docs_subdir / 'subdir_doc.md', "# Subdir Document\n\nThis is a subdir test.")
        
        # Run the copy function
        self.fixer.copy_documentation_to_website()
        
        # Check that the documentation was copied to the website
        website_docs_dir = self.dist_dir / 'docs'
        
        # Check that the docs directory exists
        self.assertTrue(website_docs_dir.exists())
        self.assertTrue(website_docs_dir.is_dir())
        
        # Check that the index.html was created
        index_html = website_docs_dir / 'index.html'
        self.assertTrue(index_html.exists())
        
        # Check that the documentation files were copied
        test_doc_html = website_docs_dir / 'test_doc.html'
        self.assertTrue(test_doc_html.exists())
        
        another_doc_html = website_docs_dir / 'another_doc.html'
        self.assertTrue(another_doc_html.exists())
        
        # Check that subdirectory was created and its documents copied
        subdir_html = website_docs_dir / 'subdir' / 'subdir_doc.html'
        self.assertTrue(subdir_html.exists())
    
    def test_ensure_website_references(self):
        """Test the full ensure_website_references method."""
        # Create test files
        self._create_test_file(self.docs_dir / 'test_doc.md', "# Test Document\n\nThis is a test.")
        
        visualizations_dir = self.dist_dir / 'visualizations'
        visualizations_dir.mkdir()
        
        index_html = self.dist_dir / 'index.html'
        self._create_test_file(index_html, """
        <!DOCTYPE html>
        <html>
        <head>
            <title>P3IF Test</title>
        </head>
        <body>
            <a href="documentation/test_doc.html">Test Doc</a>
        </body>
        </html>
        """)
        
        # Run the ensure_website_references method
        self.fixer.ensure_website_references()
        
        # Check that documentation was copied
        website_docs_dir = self.dist_dir / 'docs'
        self.assertTrue(website_docs_dir.exists())
        
        # Check that HTML references were fixed
        with open(index_html, 'r') as f:
            content = f.read()
            self.assertIn('href="/docs/test_doc.html"', content)
    
    def _create_test_file(self, path, content):
        """Helper to create a test file with content."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)


if __name__ == '__main__':
    unittest.main() 