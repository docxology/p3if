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
from typing import Optional, List

# Add the project root to the path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Only use SyntheticDataGenerator
from data.synthetic import SyntheticDataGenerator
from visualization.portal import VisualizationPortal
from utils.output_organizer import create_standard_output_structure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s,%(msecs)d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from core.framework import P3IFFramework
from utils.config import Config

# Import domain functionality
from data.domains import DomainManager

def run_multidomain_portal(
    domain_names: List[str],
    output_dir: Optional[str] = None,
    num_relationships_per_domain: int = 20,
    num_cross_domain_relationships: int = 10,
    enable_visualizations: bool = True,
    openai_api_key: Optional[str] = None,
) -> None:
    """
    Generate a multi-domain portal.

    Args:
        domain_names: List of domain names
        output_dir: Output directory
        num_relationships_per_domain: Number of relationships to generate per domain
        num_cross_domain_relationships: Number of cross-domain relationships to generate
        enable_visualizations: Whether to generate visualizations
        openai_api_key: OpenAI API key
    """
    # Set OpenAI API key
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key

    # Initialize framework
    framework = P3IFFramework()
    config = Config()
    
    # Load domains using SyntheticDataGenerator
    generator = SyntheticDataGenerator()
    available_domains = generator.get_available_domains()
    
    logger.info(f"Available domains: {available_domains}")
    
    # Filter to requested domains
    domains_to_use = []
    for domain_name in domain_names:
        if domain_name in available_domains:
            domains_to_use.append(domain_name)
        else:
            logger.warning(f"Domain not found: {domain_name}")
    
    if not domains_to_use:
        logger.error("No valid domains specified")
        return
    
    # Set up output path correctly within the repository
    project_root = Path(__file__).parent.parent  # Two levels up from this script
    
    if output_dir is None:
        # Use the standard output structure
        output_organizer = create_standard_output_structure()
        output_path = output_organizer
    else:
        # Handle both absolute and relative paths
        output_path = Path(output_dir)
        # If the path is absolute, make it relative to the project root
        if output_path.is_absolute():
            try:
                # Try to make it relative to the project root
                output_path = output_path.relative_to(project_root)
                output_path = project_root / output_path
            except ValueError:
                # If the path is outside the project, place it in output/custom
                logging.warning(f"Output path {output_path} is outside the project. Using output/custom instead.")
                output_path = project_root / "output" / "custom"
        else:
            # It's already relative, ensure it's relative to project root
            output_path = project_root / output_path
    
    # Ensure the output directory exists
    logging.info(f"Creating output directory: {output_path}")
    os.makedirs(output_path, exist_ok=True)
    
    # Generate data for each domain
    for domain in domains_to_use:
        logger.info(f"Generating data for domain: {domain}")
        generator.generate_domain(
            framework=framework,
            domain_name=domain,
            num_relationships=num_relationships_per_domain
        )
    
    # Generate cross-domain connections
    if len(domains_to_use) > 1 and num_cross_domain_relationships > 0:
        logger.info(f"Generating {num_cross_domain_relationships} cross-domain connections")
        generator.generate_cross_domain_connections(
            framework=framework,
            num_connections=num_cross_domain_relationships
        )
    
    # Prepare dataset information for portal
    datasets = []
    for domain in domains_to_use:
        datasets.append({
            "id": domain.lower().replace(" ", "_"),
            "name": domain
        })
    
    # Create visualization portal
    portal = VisualizationPortal(framework, config)
    
    # Generate portal
    output_file = output_path / "index.html"
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

    logging.info(f"Portal generated at {output_file}")

def main():
    """Command-line interface for running the portal."""
    parser = argparse.ArgumentParser(description="Generate a P3IF multi-domain portal")
    parser.add_argument("--domains", type=str, help="Comma-separated list of domain names")
    parser.add_argument("--output_dir", type=str, help="Output directory for the portal")
    parser.add_argument("--num_relationships_per_domain", type=int, default=20, 
                      help="Number of relationships to generate per domain")
    parser.add_argument("--num_cross_domain_relationships", type=int, default=10,
                      help="Number of cross-domain relationships to generate")
    parser.add_argument("--enable_visualizations", type=bool, default=True,
                      help="Whether to generate visualizations")
    args = parser.parse_args()
    
    if args.domains:
        domains = [d.strip() for d in args.domains.split(',')]
    else:
        # Default to a couple of interesting domains
        domains = ["Cybersecurity", "MachineLearning"]
    
    run_multidomain_portal(
        domain_names=domains,
        output_dir=args.output_dir,
        num_relationships_per_domain=args.num_relationships_per_domain,
        num_cross_domain_relationships=args.num_cross_domain_relationships,
        enable_visualizations=args.enable_visualizations
    )

if __name__ == "__main__":
    main() 