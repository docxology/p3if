"""
Tests to verify all domain data can be visualized correctly.
"""
import os
import unittest
import tempfile
from pathlib import Path
import sys
import json
import glob

# Configure matplotlib to use the non-interactive Agg backend for these tests
import matplotlib
matplotlib.use('Agg')

# Add the project root to the path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.framework import P3IFFramework
    from data.synthetic import SyntheticDataGenerator
    from visualization.portal import VisualizationPortal
    from utils.config import Config
except ImportError:
    # Fallback import paths
    from core.framework import P3IFFramework
    from data.synthetic import SyntheticDataGenerator
    from visualization.portal import VisualizationPortal
    from utils.config import Config


class TestAllDomains(unittest.TestCase):
    """Test that all domains can be visualized correctly."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test output
        self.output_path = Path(__file__).parent / "test_output"
        self.output_path.mkdir(exist_ok=True)
        
        # Initialize the data generator
        self.generator = SyntheticDataGenerator()
        
        # Get all available domains
        self.all_domains = self.generator.get_available_domains()
        
        # Initialize the config
        self.config = Config()
    
    def test_all_domains_can_be_loaded(self):
        """Test that all domains can be loaded."""
        # Check that domains were found
        self.assertGreater(len(self.all_domains), 0, "No domains were found")
        
        # Log the domains found
        print(f"Found {len(self.all_domains)} domains: {', '.join(self.all_domains)}")
        
        # Test loading each domain
        for domain_name in self.all_domains:
            domain_info = self.generator.get_domain_info(domain_name)
            self.assertIsNotNone(domain_info, f"Failed to load domain: {domain_name}")
            self.assertIn("id", domain_info, f"Domain {domain_name} missing 'id' field")
            self.assertIn("patterns", domain_info, f"Domain {domain_name} missing 'patterns' field")
            self.assertIn("processes", domain_info, f"Domain {domain_name} missing 'processes' field")
            self.assertIn("perspectives", domain_info, f"Domain {domain_name} missing 'perspectives' field")
    
    def test_all_domains_can_generate_data(self):
        """Test that all domains can generate data."""
        for domain_name in self.all_domains:
            # Create a new framework for each domain
            framework = P3IFFramework()
            
            # Generate data for the domain
            self.generator.generate_domain(
                framework=framework,
                domain_name=domain_name,
                num_relationships=10  # Use fewer relationships for testing
            )
            
            # Check that the framework contains data
            self.assertGreater(len(framework.patterns), 0, f"No patterns generated for domain: {domain_name}")
            self.assertGreater(len(framework.processes), 0, f"No processes generated for domain: {domain_name}")
            self.assertGreater(len(framework.perspectives), 0, f"No perspectives generated for domain: {domain_name}")
            self.assertGreater(len(framework.relationships), 0, f"No relationships generated for domain: {domain_name}")
    
    def test_all_domains_can_be_visualized(self):
        """Test that all domains can be visualized."""
        for domain_name in self.all_domains:
            # Create a new framework for each domain
            framework = P3IFFramework()
            
            # Generate data for the domain
            self.generator.generate_domain(
                framework=framework,
                domain_name=domain_name,
                num_relationships=10  # Use fewer relationships for testing
            )
            
            # Create visualization portal
            portal = VisualizationPortal(framework, self.config)
            
            # Generate the portal HTML
            output_file = self.output_path / f"{domain_name.lower().replace(' ', '_')}_test.html"
            
            try:
                # Generate a basic portal with just the 3D cube
                result_file = portal.generate_portal(
                    output_file=output_file,
                    title=f"{domain_name} Visualization Test",
                    include_3d_cube=True,
                    include_network=True,
                    include_matrix=True
                )
                
                # Check that the file was created
                self.assertTrue(result_file.exists(), f"Visualization failed for domain: {domain_name}")
                self.assertGreater(result_file.stat().st_size, 0, f"Empty visualization for domain: {domain_name}")
                
                # Check that it contains the expected visualization elements
                with open(result_file, 'r') as f:
                    content = f.read()
                    self.assertIn("3d-cube-container", content, f"3D cube missing for domain: {domain_name}")
                    self.assertIn("network-container", content, f"Network missing for domain: {domain_name}")
                    self.assertIn("matrix-container", content, f"Matrix missing for domain: {domain_name}")
            
            except Exception as e:
                self.fail(f"Visualization failed for domain {domain_name}: {str(e)}")
    
    def test_multiple_domains_can_be_visualized_together(self):
        """Test that multiple domains can be visualized together."""
        # Skip if there are fewer than 2 domains
        if len(self.all_domains) < 2:
            self.skipTest("Need at least 2 domains to test multi-domain visualization")
        
        # Select up to 3 domains for testing
        test_domains = self.all_domains[:min(3, len(self.all_domains))]
        
        # Create a framework
        framework = P3IFFramework()
        
        # Generate data for multiple domains
        self.generator.generate_multi_domain(
            framework=framework,
            domain_names=test_domains,
            relationships_per_domain=10  # Use fewer relationships for testing
        )
        
        # Generate cross-domain connections
        self.generator.generate_cross_domain_connections(
            framework=framework,
            num_connections=5  # Small number of connections for testing
        )
        
        # Check that the framework contains data
        self.assertGreater(len(framework.patterns), 0, "No patterns generated for multi-domain")
        self.assertGreater(len(framework.processes), 0, "No processes generated for multi-domain")
        self.assertGreater(len(framework.perspectives), 0, "No perspectives generated for multi-domain")
        self.assertGreater(len(framework.relationships), 0, "No relationships generated for multi-domain")
        
        # Create visualization portal
        portal = VisualizationPortal(framework, self.config)
        
        # Prepare datasets for dropdown
        datasets = []
        for domain in test_domains:
            domain_info = self.generator.get_domain_info(domain)
            datasets.append({
                "id": domain_info.get("id", domain.lower().replace(" ", "_")),
                "name": domain
            })
        
        # Generate the portal HTML
        output_file = self.output_path / "multi_domain_test.html"
        
        try:
            # Generate a portal with multiple domains
            result_file = portal.generate_portal(
                output_file=output_file,
                title="Multi-Domain Visualization Test",
                include_dataset_dropdown=True,
                datasets=datasets,
                include_3d_cube=True,
                include_network=True,
                include_matrix=True,
                include_dashboard=True
            )
            
            # Check that the file was created
            self.assertTrue(result_file.exists(), "Multi-domain visualization failed")
            self.assertGreater(result_file.stat().st_size, 0, "Empty multi-domain visualization")
            
            # Check that it contains the expected elements
            with open(result_file, 'r') as f:
                content = f.read()
                self.assertIn("dataset-selector", content, "Dataset selector missing in multi-domain visualization")
                self.assertIn("3d-cube-container", content, "3D cube missing in multi-domain visualization")
                self.assertIn("network-container", content, "Network missing in multi-domain visualization")
                self.assertIn("matrix-container", content, "Matrix missing in multi-domain visualization")
                self.assertIn("dashboard-container", content, "Dashboard missing in multi-domain visualization")
                
                # Check that all domain names are in the content
                for domain in test_domains:
                    self.assertIn(domain, content, f"Domain {domain} missing in multi-domain visualization")
        
        except Exception as e:
            self.fail(f"Multi-domain visualization failed: {str(e)}")


if __name__ == '__main__':
    unittest.main() 