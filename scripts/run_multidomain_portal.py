#!/usr/bin/env python3
"""
P3IF Multi-Domain Visualization Portal

This script runs a visualization portal with a domain selector dropdown,
allowing users to explore different domains in the P3IF framework.
"""
import os
import sys
import webbrowser
import tempfile
import logging
import argparse
from pathlib import Path
# Only use SyntheticDataGenerator
from p3if.data.synthetic import SyntheticDataGenerator
from p3if.visualization.portal import VisualizationPortal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s,%(msecs)d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add the project root to the path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from p3if.core.framework import P3IFFramework
from p3if.utils.config import Config


def run_multidomain_portal(domains=None, output_dir=None, open_browser=True, 
                         relationships_per_domain=50, cross_domain_connections=20):
    """
    Run the P3IF portal with multiple domains.
    
    Args:
        domains: List of domain names to include (if None, uses all available domains)
        output_dir: Directory to save the portal files (if None, uses a temp directory)
        open_browser: Whether to open the browser automatically
        relationships_per_domain: Number of relationships to generate per domain
        cross_domain_connections: Number of cross-domain connections to generate
        
    Returns:
        Path to the generated portal HTML file
    """
    # Create output directory if needed
    if output_dir:
        output_dir = Path(output_dir)
        os.makedirs(output_dir, exist_ok=True)
    else:
        # Create a temporary directory
        temp_dir = tempfile.TemporaryDirectory()
        output_dir = Path(temp_dir.name)
    
    # Create framework
    framework = P3IFFramework()
    
    # Create data generator
    generator = SyntheticDataGenerator()
    
    # Get available domains
    available_domains = generator.get_available_domains()
    logger.info(f"Available domains: {available_domains}")
    
    # Filter domains if specified
    if domains:
        # Convert to list if it's a comma-separated string
        if isinstance(domains, str):
            domains = [d.strip() for d in domains.split(",")]
        
        # Verify domains exist
        domains = [d for d in domains if d in available_domains]
        if not domains:
            logger.warning("None of the specified domains were found. Using all available domains.")
            domains = available_domains
    else:
        domains = available_domains
    
    # Generate data for selected domains
    logger.info(f"Generating data for domains: {domains}")
    generator.generate_multi_domain(
        framework=framework,
        domain_names=domains,
        relationships_per_domain=relationships_per_domain
    )
    
    # Generate cross-domain connections
    if len(domains) > 1 and cross_domain_connections > 0:
        logger.info(f"Generating {cross_domain_connections} cross-domain connections")
        generator.generate_cross_domain_connections(
            framework=framework,
            num_connections=cross_domain_connections
        )
    
    # Prepare datasets for dropdown
    datasets = []
    for domain in domains:
        domain_info = generator.get_domain_info(domain)
        datasets.append({
            "id": domain_info.get("id", domain.lower().replace(" ", "_")),
            "name": domain
        })
    
    # Create visualization portal
    portal = VisualizationPortal(framework, Config())
    
    # Generate portal
    output_file = output_dir / "index.html"
    portal.generate_portal(
        output_file=output_file,
        title="P3IF Multi-Domain Portal",
        include_dataset_dropdown=True,
        datasets=datasets,
        include_component_selector=True,
        include_3d_cube=True,
        include_network=True,
        include_matrix=True,
        include_dashboard=True,
        include_data_loading_script=True,
        include_export_buttons=True
    )
    
    logger.info(f"Portal generated at {output_file}")
    
    # Open in browser if requested
    if open_browser:
        portal_url = f"file://{output_file.absolute()}"
        logger.info(f"Opening portal in browser: {portal_url}")
        webbrowser.open(portal_url)
    
    return output_file


def main():
    # Get project root directory
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create portal output directory
    portal_dir = output_dir / 'portal'
    portal_dir.mkdir(parents=True, exist_ok=True)
    
    # Run the multi-domain portal
    run_multidomain_portal(
        output_dir=portal_dir,
        open_browser=False,  # Don't open browser in build process
        relationships_per_domain=50,
        cross_domain_connections=20
    )
    
    logger.info(f"Generated visualization portal at {portal_dir}/index.html")


if __name__ == "__main__":
    main() 