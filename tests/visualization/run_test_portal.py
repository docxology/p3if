#!/usr/bin/env python3
"""
Test script for P3IF Visualization Portal.

This script generates a complete visualization portal with all components enabled
and opens it in the default web browser for manual testing.
"""
import os
import sys
import webbrowser
import tempfile
import logging
from pathlib import Path
import argparse
import time

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
tests_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(tests_dir)
sys.path.append(project_root)

from core.framework import P3IFFramework
from visualization.portal import VisualizationPortal
from utils.config import Config

# Use direct import from local path
sys.path.append(tests_dir)
from utils import create_test_framework, create_multi_domain_test_framework

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_test_portal(output_dir=None, multi_domain=False, include_dataset_dropdown=True, 
                        include_component_selector=True, open_browser=True):
    """
    Generate a test visualization portal for manual testing.
    
    Args:
        output_dir: Directory to save the portal. If None, creates a temp directory.
        multi_domain: Whether to use a multi-domain test framework
        include_dataset_dropdown: Whether to include dataset dropdown
        include_component_selector: Whether to include component selector
        open_browser: Whether to open the portal in the browser
        
    Returns:
        Path to the generated HTML file
    """
    # Create temporary directory if not specified
    if output_dir is None:
        temp_dir = tempfile.TemporaryDirectory()
        output_dir = Path(temp_dir.name)
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
    logger.info(f"Generating test portal in {output_dir}")
    
    # Create test framework
    if multi_domain:
        logger.info("Creating multi-domain test framework")
        framework = create_multi_domain_test_framework(
            domains=["Technology", "Business", "Science"],
            patterns_per_domain=5,
            relationships_per_domain=15,
            cross_domain_relationships=10
        )
    else:
        logger.info("Creating standard test framework")
        framework = create_test_framework(
            num_properties=10,
            num_processes=10,
            num_perspectives=10,
            num_relationships=50
        )
    
    # Create config
    config = Config()
    
    # Create test datasets (only used if include_dataset_dropdown is True)
    datasets = [
        {"id": "dataset1", "name": "Technology Framework"},
        {"id": "dataset2", "name": "Business Framework"},
        {"id": "dataset3", "name": "Science Framework"}
    ]
    
    # Create test components (only used if include_component_selector is True)
    components = [
        {"id": "3d-cube", "name": "3D Cube Visualization", 
         "description": "Interactive 3D visualization of framework relationships"},
        {"id": "network", "name": "Network Graph", 
         "description": "Force-directed graph of patterns and relationships"},
        {"id": "matrices", "name": "Matrix Visualizations", 
         "description": "Heatmap matrices showing pattern relationships"},
        {"id": "dashboard", "name": "Interactive Dashboard", 
         "description": "Comprehensive dashboard with multiple visualizations"}
    ]
    
    # Create portal
    portal = VisualizationPortal(framework, config)
    
    # Generate portal file
    output_file = output_dir / "test_portal.html"
    portal.generate_portal(
        output_file=output_file,
        title="P3IF Test Visualization Portal",
        include_dataset_dropdown=include_dataset_dropdown,
        datasets=datasets if include_dataset_dropdown else None,
        include_component_selector=include_component_selector,
        components=components if include_component_selector else None,
        include_3d_cube=True,
        include_network=True,
        include_matrix=True,
        include_dashboard=True,
        include_data_loading_script=True,
        include_export_buttons=True
    )
    
    # Open portal in browser
    if open_browser:
        portal_url = f"file://{output_file.absolute()}"
        logger.info(f"Opening portal in browser: {portal_url}")
        webbrowser.open(portal_url)
    
    logger.info(f"Portal generated at {output_file}")
    return output_file


def main():
    """Parse command line arguments and run the test portal generator."""
    parser = argparse.ArgumentParser(description='Generate and test P3IF visualization portal')
    
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Directory to save the portal')
    parser.add_argument('--multi-domain', action='store_true',
                        help='Use a multi-domain test framework')
    parser.add_argument('--no-dropdown', action='store_true',
                        help='Do not include dataset dropdown')
    parser.add_argument('--no-selector', action='store_true',
                        help='Do not include component selector')
    parser.add_argument('--no-browser', action='store_true',
                        help='Do not open the portal in the browser')
    
    args = parser.parse_args()
    
    # Generate the portal
    generate_test_portal(
        output_dir=args.output_dir,
        multi_domain=args.multi_domain,
        include_dataset_dropdown=not args.no_dropdown,
        include_component_selector=not args.no_selector,
        open_browser=not args.no_browser
    )


if __name__ == "__main__":
    main() 