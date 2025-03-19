#!/usr/bin/env python3
"""
Generate 3D Visualization Script for P3IF Website

This script generates 3D cube visualizations for the P3IF website by
loading data files and using the P3IF visualization components.
"""
import logging
import json
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import p3if
sys.path.append(str(Path(__file__).parent.parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

from p3if.utils.json import P3IFEncoder

def create_framework_from_data(data):
    """
    Create a P3IFFramework from visualization data.
    
    Args:
        data: Dictionary containing patterns and relationships
        
    Returns:
        P3IFFramework instance
    """
    from p3if.core.framework import P3IFFramework
    from p3if.core.models import Property, Process, Perspective, Relationship
    
    framework = P3IFFramework()
    
    # Pattern ID mapping
    pattern_map = {}
    
    # Add patterns
    for pattern in data.get("patterns", []):
        pattern_type = pattern.get("type")
        if pattern_type == "property":
            obj = Property(**pattern)
        elif pattern_type == "process":
            obj = Process(**pattern)
        elif pattern_type == "perspective":
            obj = Perspective(**pattern)
        else:
            continue
        
        new_id = framework.add_pattern(obj)
        pattern_map[pattern.get("id")] = new_id
    
    # Add relationships
    for rel in data.get("relationships", []):
        if all(id in pattern_map for id in [rel.get("property_id"), rel.get("process_id"), rel.get("perspective_id")]):
            relationship = Relationship(
                property_id=pattern_map[rel.get("property_id")],
                process_id=pattern_map[rel.get("process_id")],
                perspective_id=pattern_map[rel.get("perspective_id")],
                strength=rel.get("strength", 0.5),
                confidence=rel.get("confidence", 0.5)
            )
            framework.add_relationship(relationship)
    
    logger.info(f"Created framework with {len(framework.get_patterns_by_type('property') + framework.get_patterns_by_type('process') + framework.get_patterns_by_type('perspective'))} patterns and {len(framework._relationships)} relationships")
    return framework

def generate_visualization(data_file, output_file, title=None, domain=None):
    """
    Generate a 3D cube visualization from a data file.
    
    Args:
        data_file: Path to the JSON data file
        output_file: Path to save the visualization HTML to
        title: Optional title for the visualization
        domain: Optional domain name
    """
    logger.info(f"Loading visualization data from {data_file}")
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    logger.info("Creating framework from data")
    framework = create_framework_from_data(data)
    
    # Generate a title if not provided
    if not title:
        filename = os.path.basename(data_file)
        title_parts = filename.split("_visualization")[0].split("_")
        title = " ".join(title_parts).title()
    
    logger.info(f"Generating visualization with title: {title}")
    
    from p3if.visualization.interactive import InteractiveVisualizer
    
    visualizer = InteractiveVisualizer(framework)
    
    # Generate HTML
    html = visualizer.generate_3d_cube_html(output_file=output_file, title=title)
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(html)
    
    logger.info(f"Visualization saved to {output_file}")
    return output_file

def generate_all_visualizations(data_dir, output_dir, domain_index=None):
    """
    Generate all visualizations from data files in a directory.
    
    Args:
        data_dir: Directory containing data files
        output_dir: Directory to save visualizations to
        domain_index: Optional domain index file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all visualization data files
    data_files = []
    for filename in os.listdir(data_dir):
        if filename.endswith("_visualization.json"):
            data_files.append(os.path.join(data_dir, filename))
    
    logger.info(f"Found {len(data_files)} visualization data files")
    
    # Generate visualization for each data file
    for data_file in data_files:
        filename = os.path.basename(data_file)
        id_part = filename.split("_visualization")[0]
        
        # Generate title
        title = None
        if domain_index:
            for domain in domain_index.get("domains", []):
                if domain.get("id") == id_part:
                    title = domain.get("name", id_part.title())
                    break
            
            if not title:
                for rel_set in domain_index.get("relationshipSets", []):
                    if rel_set.get("id") == id_part:
                        title = rel_set.get("name", id_part.title())
                        break
        
        if not title:
            title = id_part.replace("_", " ").title()
        
        # Generate output file path
        output_file = os.path.join(output_dir, f"{id_part}_visualization.html")
        
        # Generate visualization
        generate_visualization(data_file, output_file, title=title, domain=id_part)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate 3D cube visualizations for P3IF website')
    parser.add_argument('--data-dir', type=str, required=True, help='Directory containing visualization data files')
    parser.add_argument('--output-dir', type=str, required=True, help='Directory to save visualization files to')
    parser.add_argument('--domain-index', type=str, help='Path to domain index file')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    domain_index = None
    if args.domain_index:
        with open(args.domain_index, 'r') as f:
            domain_index = json.load(f)
    
    generate_all_visualizations(args.data_dir, args.output_dir, domain_index=domain_index) 