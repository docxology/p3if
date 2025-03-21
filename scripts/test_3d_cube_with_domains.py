#!/usr/bin/env python3
"""
Script to test the 3D cube visualization with domain dataset selection.
"""
import os
import json
import shutil
from pathlib import Path
import sys

# Add the project root to the path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from core.framework import P3IFFramework
from core.models import Property, Process, Perspective, Relationship
from visualization.interactive import InteractiveVisualizer
from utils.config import Config


def load_domain_data(domain_file):
    """
    Load domain data from a file.
    
    Args:
        domain_file: Path to the domain file
        
    Returns:
        Framework with the domain data loaded
    """
    with open(domain_file, 'r') as f:
        data = json.load(f)
    
    # Create framework
    framework = P3IFFramework()
    
    # Add patterns
    pattern_map = {}  # Map pattern IDs to framework IDs
    
    # Add properties
    for prop_data in data.get("patterns", {}).get("properties", []):
        prop = Property(
            name=prop_data["name"],
            domain=prop_data.get("domain"),
            type="property"
        )
        new_id = framework.add_pattern(prop)
        pattern_map[prop_data["id"]] = new_id
    
    # Add processes
    for proc_data in data.get("patterns", {}).get("processes", []):
        proc = Process(
            name=proc_data["name"],
            domain=proc_data.get("domain"),
            type="process"
        )
        new_id = framework.add_pattern(proc)
        pattern_map[proc_data["id"]] = new_id
    
    # Add perspectives
    for persp_data in data.get("patterns", {}).get("perspectives", []):
        persp = Perspective(
            name=persp_data["name"],
            domain=persp_data.get("domain"),
            type="perspective"
        )
        new_id = framework.add_pattern(persp)
        pattern_map[persp_data["id"]] = new_id
    
    # Add relationships
    for rel_data in data.get("relationships", []):
        # Map old IDs to new IDs
        property_id = pattern_map.get(rel_data.get("property_id"))
        process_id = pattern_map.get(rel_data.get("process_id"))
        perspective_id = pattern_map.get(rel_data.get("perspective_id"))
        
        # Create relationship
        rel = Relationship(
            property_id=property_id,
            process_id=process_id,
            perspective_id=perspective_id,
            strength=rel_data.get("strength", 0.5),
            confidence=rel_data.get("confidence", 0.5)
        )
        
        try:
            framework.add_relationship(rel)
        except ValueError as e:
            print(f"Error adding relationship: {e}")
    
    return framework


def get_domain_datasets():
    """
    Get domain datasets information for the dropdown.
    
    Returns:
        List of dataset information dicts
    """
    # Use absolute path to ensure directory exists
    project_root = Path(__file__).parent.parent
    domains_dir = project_root / "data" / "domains"
    
    # Create domains directory if it doesn't exist
    domains_dir.mkdir(parents=True, exist_ok=True)
    
    datasets = []
    
    # Create domain index if it doesn't exist
    if not (domains_dir / "index.json").exists():
        print("Warning: Domain index not found. Creating a basic index.")
        # Get all domain files that match the pattern *.json (excluding template file)
        domain_files = [f for f in domains_dir.glob("*.json") 
                      if f.name != "index.json" and f.name != "template_domain.json"]
        
        # Create basic domain info from filename
        domains_info = []
        for file_path in domain_files:
            domain_id = file_path.stem
            domain_name = domain_id.replace("_", " ").title()
            domains_info.append({
                "id": domain_id,
                "name": domain_name,
                "file": file_path.name
            })
        
        # Write index file
        with open(domains_dir / "index.json", 'w') as f:
            json.dump({"domains": domains_info, "version": "1.0"}, f, indent=2)
        
        print(f"Created domain index with {len(domains_info)} domains.")
    
    # Load the index file to get domain names
    try:
        with open(domains_dir / "index.json", 'r') as f:
            index_data = json.load(f)
        
        domain_name_map = {}
        for domain_info in index_data.get("domains", []):
            if isinstance(domain_info, dict):
                domain_name_map[domain_info.get("id")] = domain_info.get("name")
            elif isinstance(domain_info, str):
                # Handle simple string format for backward compatibility
                domain_id = domain_info.lower().replace(" ", "_")
                domain_name_map[domain_id] = domain_info
    
        # Get all domain files (excluding index.json and template)
        domain_files = [f for f in domains_dir.glob("*.json") 
                      if f.name != "index.json" and f.name != "template_domain.json"]
        
        for file_path in domain_files:
            domain_id = file_path.stem
            domain_name = domain_name_map.get(domain_id, domain_id.replace("_", " ").title())
            
            datasets.append({
                "id": domain_id,
                "name": domain_name,
                "file": str(file_path)
            })
        
    except Exception as e:
        print(f"Error loading domain index: {e}")
        # Fallback to just using filenames
        domain_files = [f for f in domains_dir.glob("*.json") 
                      if f.name != "index.json" and f.name != "template_domain.json"]
        
        for file_path in domain_files:
            domain_id = file_path.stem
            domain_name = domain_id.replace("_", " ").title()
            
            datasets.append({
                "id": domain_id,
                "name": domain_name,
                "file": str(file_path)
            })
    
    return datasets


def generate_domain_cube(domain_id, output_dir="output"):
    """
    Generate a 3D cube visualization for a specific domain.
    
    Args:
        domain_id: Domain ID to generate visualization for
        output_dir: Output directory for the visualization
        
    Returns:
        Path to the generated visualization
    """
    domains_dir = Path("data/domains")
    domain_file = domains_dir / f"{domain_id}.json"
    
    if not domain_file.exists():
        print(f"Error: Domain file {domain_file} does not exist")
        return None
    
    # Load the domain data
    framework = load_domain_data(domain_file)
    
    # Create the output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate the 3D cube visualization
    config = Config()
    visualizer = InteractiveVisualizer(framework, config)
    
    # Generate with a dataset dropdown
    datasets = get_domain_datasets()
    
    output_file = output_path / f"{domain_id}_cube.html"
    
    # Generate the visualization
    result_path = visualizer.generate_3d_cube_html(
        output_file=output_file,
        title=f"3D Cube Visualization - {domain_id}",
        include_dataset_selector=True,
        datasets=datasets
    )
    
    print(f"Generated 3D cube visualization at {result_path}")
    return result_path


def generate_full_website(output_dir="output", website_dir="website"):
    """
    Generate a full website with dataset selection and 3D cube.
    
    Args:
        output_dir: Output directory for the website
        website_dir: Website directory for persistent files
        
    Returns:
        Path to the generated website
    """
    # Get available domains
    datasets = get_domain_datasets()
    
    if not datasets:
        print("Error: No domain datasets found")
        return None
    
    # Use the first domain as default
    default_domain = datasets[0]["id"]
    framework = load_domain_data(Path(datasets[0]["file"]))
    
    # Create the output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create the website directory if it doesn't exist
    website_path = Path(website_dir)
    website_path.mkdir(parents=True, exist_ok=True)
    
    # Generate the website
    config = Config()
    visualizer = InteractiveVisualizer(framework, config)
    
    # Generate files in output directory
    output_file = output_path / "p3if_full_website.html"
    index_file = output_path / "index.html"
    
    # Generate the visualization
    result_path = visualizer.generate_3d_cube_html(
        output_file=output_file,
        title="P3IF 3D Cube Visualization",
        include_dataset_selector=True,
        datasets=datasets
    )
    
    # Copy the output file to index.html in the output directory
    shutil.copy(output_file, index_file)
    print(f"Created index.html at {index_file}")
    
    # Copy the files to the website directory
    website_output_file = website_path / "p3if_full_website.html"
    website_index_file = website_path / "index.html"
    
    shutil.copy(output_file, website_output_file)
    shutil.copy(index_file, website_index_file)
    
    print(f"Generated full website at {result_path}")
    print(f"Copied files to website directory at {website_path}")
    
    return result_path


def main():
    """Main function to run the test."""
    if len(sys.argv) > 1:
        domain_id = sys.argv[1]
        generate_domain_cube(domain_id)
    else:
        generate_full_website()


if __name__ == "__main__":
    main() 