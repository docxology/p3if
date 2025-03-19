#!/usr/bin/env python3
"""
Generate Sample Data Script for P3IF Website

This script generates sample data for the P3IF website visualizations
by adapting data from the P3IF framework and combining domains.
"""
import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import p3if
sys.path.append(str(Path(__file__).parent.parent.parent))

from p3if.core.framework import P3IFFramework
from p3if.core.models import Property, Process, Perspective, Relationship, Pattern
from p3if.utils.json import P3IFEncoder, convert_to_serializable

def load_domain_data(domain_file):
    """
    Load domain data from a file.
    
    Args:
        domain_file: Path to the domain file
        
    Returns:
        Dictionary containing the domain data
    """
    with open(domain_file, 'r') as f:
        return json.load(f)

def create_framework_from_domain(domain_data):
    """
    Create a P3IFFramework instance from domain data.
    
    Args:
        domain_data: Dictionary containing domain data
        
    Returns:
        P3IFFramework instance
    """
    framework = P3IFFramework()
    
    # Track pattern IDs
    pattern_map = {}
    
    # Add properties
    for prop_data in domain_data.get("patterns", {}).get("properties", []):
        prop = Property(
            name=prop_data["name"],
            domain=prop_data.get("domain", domain_data.get("domain")),
            type="property"
        )
        new_id = framework.add_pattern(prop)
        pattern_map[prop_data["id"]] = new_id
    
    # Add processes
    for proc_data in domain_data.get("patterns", {}).get("processes", []):
        proc = Process(
            name=proc_data["name"],
            domain=proc_data.get("domain", domain_data.get("domain")),
            type="process"
        )
        new_id = framework.add_pattern(proc)
        pattern_map[proc_data["id"]] = new_id
    
    # Add perspectives
    for persp_data in domain_data.get("patterns", {}).get("perspectives", []):
        persp = Perspective(
            name=persp_data["name"],
            domain=persp_data.get("domain", domain_data.get("domain")),
            type="perspective"
        )
        new_id = framework.add_pattern(persp)
        pattern_map[persp_data["id"]] = new_id
    
    # Add relationships
    for rel_data in domain_data.get("relationships", []):
        if all(id in pattern_map for id in [rel_data["property_id"], rel_data["process_id"], rel_data["perspective_id"]]):
            rel = Relationship(
                property_id=pattern_map[rel_data["property_id"]],
                process_id=pattern_map[rel_data["process_id"]],
                perspective_id=pattern_map[rel_data["perspective_id"]],
                strength=rel_data.get("strength", 0.5),
                confidence=rel_data.get("confidence", 0.5)
            )
            framework.add_relationship(rel)
    
    return framework, pattern_map

def add_cross_domain_relationships(framework, relationship_file, pattern_maps):
    """
    Add cross-domain relationships to a framework.
    
    Args:
        framework: P3IFFramework instance
        relationship_file: Path to the relationship file
        pattern_maps: Dictionary of pattern maps for each domain
        
    Returns:
        Updated framework
    """
    with open(relationship_file, 'r') as f:
        relationships = json.load(f).get("relationships", [])
    
    for rel_data in relationships:
        # Find the property ID in the appropriate domain's pattern map
        property_domain = rel_data.get("property_domain")
        property_id = None
        if property_domain in pattern_maps:
            for orig_id, new_id in pattern_maps[property_domain].items():
                if orig_id == rel_data["property_id"]:
                    property_id = new_id
                    break
        
        # Find the process ID in the appropriate domain's pattern map
        process_domain = rel_data.get("process_domain")
        process_id = None
        if process_domain in pattern_maps:
            for orig_id, new_id in pattern_maps[process_domain].items():
                if orig_id == rel_data["process_id"]:
                    process_id = new_id
                    break
        
        # Find the perspective ID in the appropriate domain's pattern map
        perspective_domain = rel_data.get("perspective_domain")
        perspective_id = None
        if perspective_domain in pattern_maps:
            for orig_id, new_id in pattern_maps[perspective_domain].items():
                if orig_id == rel_data["perspective_id"]:
                    perspective_id = new_id
                    break
        
        # Add the relationship if all IDs were found
        if property_id and process_id and perspective_id:
            rel = Relationship(
                property_id=property_id,
                process_id=process_id,
                perspective_id=perspective_id,
                strength=rel_data.get("strength", 0.5),
                confidence=rel_data.get("confidence", 0.5)
            )
            framework.add_relationship(rel)
    
    return framework

def generate_sample_data(domains_dir, relationships_dir, output_dir):
    """
    Generate sample data for the P3IF website visualizations.
    
    Args:
        domains_dir: Directory containing domain data files
        relationships_dir: Directory containing relationship data files
        output_dir: Directory to output the generated data
    """
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load domain index
    domain_index_path = os.path.join(domains_dir, "index.json")
    with open(domain_index_path, 'r') as f:
        domain_index = json.load(f)
    
    # Load relationship index
    relationship_index_path = os.path.join(relationships_dir, "index.json")
    with open(relationship_index_path, 'r') as f:
        relationship_index = json.load(f)
    
    # Create main framework
    main_framework = P3IFFramework()
    
    # Track pattern maps for each domain
    pattern_maps = {}
    
    # Process each domain
    for domain_info in domain_index.get("domains", []):
        domain_id = domain_info["id"]
        domain_file = os.path.join(domains_dir, domain_info["file"])
        
        print(f"Processing domain: {domain_id}")
        
        # Load domain data
        domain_data = load_domain_data(domain_file)
        
        # Create framework for this domain
        domain_framework, pattern_map = create_framework_from_domain(domain_data)
        
        # Store pattern map for this domain
        pattern_maps[domain_id] = pattern_map
        
        # Merge into main framework
        # Get all patterns by type and combine them
        properties = domain_framework.get_patterns_by_type("property")
        processes = domain_framework.get_patterns_by_type("process")
        perspectives = domain_framework.get_patterns_by_type("perspective")
        patterns = properties + processes + perspectives
        
        for pattern in patterns:
            main_framework.add_pattern(pattern)
        
        relationships = domain_framework.get_relationship()
        for relationship in relationships:
            main_framework.add_relationship(relationship)
        
        # Save individual domain visualization data
        domain_output = {
            "patterns": properties + processes + perspectives,
            "relationships": list(domain_framework._relationships.values())
        }
        domain_output_path = os.path.join(output_dir, f"{domain_id}_visualization.json")
        with open(domain_output_path, 'w') as f:
            json.dump(domain_output, f, indent=2, cls=P3IFEncoder)
        
        print(f"Created domain visualization data: {domain_output_path}")
    
    # Process relationship sets
    for relationship_set in relationship_index.get("relationshipSets", []):
        relationship_id = relationship_set["id"]
        relationship_file = os.path.join(relationships_dir, relationship_set["file"])
        
        print(f"Processing relationship set: {relationship_id}")
        
        # Add cross-domain relationships
        main_framework = add_cross_domain_relationships(
            main_framework, relationship_file, pattern_maps
        )
        
        # Save relationship set visualization data
        set_framework = P3IFFramework()
        
        # Only include patterns and relationships relevant to this set
        with open(relationship_file, 'r') as f:
            rel_data = json.load(f).get("relationships", [])
        
        # Collect domains involved in this relationship set
        domains_in_set = set()
        for rel in rel_data:
            domains_in_set.add(rel.get("property_domain"))
            domains_in_set.add(rel.get("process_domain"))
            domains_in_set.add(rel.get("perspective_domain"))
        
        # Add patterns from these domains
        main_properties = main_framework.get_patterns_by_type("property")
        main_processes = main_framework.get_patterns_by_type("process")
        main_perspectives = main_framework.get_patterns_by_type("perspective")
        main_patterns = main_properties + main_processes + main_perspectives
        
        for pattern in main_patterns:
            if pattern.get("domain") in domains_in_set:
                set_framework.add_pattern(pattern)
        
        # Add relationships from the file
        set_framework = add_cross_domain_relationships(
            set_framework, relationship_file, pattern_maps
        )
        
        # Save set visualization data
        set_properties = set_framework.get_patterns_by_type("property")
        set_processes = set_framework.get_patterns_by_type("process")
        set_perspectives = set_framework.get_patterns_by_type("perspective")
        
        set_output = {
            "patterns": set_properties + set_processes + set_perspectives,
            "relationships": list(set_framework._relationships.values())
        }
        set_output_path = os.path.join(output_dir, f"{relationship_id}_visualization.json")
        with open(set_output_path, 'w') as f:
            json.dump(set_output, f, indent=2, cls=P3IFEncoder)
        
        print(f"Created relationship set visualization data: {set_output_path}")
    
    # Save combined visualization data
    combined_properties = main_framework.get_patterns_by_type("property")
    combined_processes = main_framework.get_patterns_by_type("process")
    combined_perspectives = main_framework.get_patterns_by_type("perspective")
    
    combined_output = {
        "patterns": combined_properties + combined_processes + combined_perspectives,
        "relationships": list(main_framework._relationships.values())
    }
    combined_output_path = os.path.join(output_dir, "combined_visualization.json")
    with open(combined_output_path, 'w') as f:
        json.dump(combined_output, f, indent=2, cls=P3IFEncoder)
    
    print(f"Created combined visualization data: {combined_output_path}")

if __name__ == "__main__":
    # Set up directories
    website_dir = Path(__file__).parent.parent
    domains_dir = website_dir / "data" / "domains"
    relationships_dir = website_dir / "data" / "relationships"
    output_dir = website_dir / "output" / "visualization_data"
    
    generate_sample_data(domains_dir, relationships_dir, output_dir) 