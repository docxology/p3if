#!/usr/bin/env python3
"""
Script to update P3IF domain files with relationship data for the 3D cube visualization.
"""
import os
import json
import random
import uuid
from pathlib import Path

# Constants
DOMAINS_DIR = Path("p3if/data/domains")
NUM_RELATIONSHIPS_MIN = 50
NUM_RELATIONSHIPS_MAX = 100
STRENGTH_MIN = 0.5
STRENGTH_MAX = 1.0
CONFIDENCE_MIN = 0.7
CONFIDENCE_MAX = 1.0

def update_domain_file(file_path):
    """
    Update a domain file with relationship data.
    
    Args:
        file_path: Path to the domain file
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    domain_name = data.get("domain")
    properties = data.get("properties", [])
    processes = data.get("processes", [])
    perspectives = data.get("perspectives", [])
    
    print(f"Updating domain: {domain_name}")
    print(f"  Properties: {len(properties)}")
    print(f"  Processes: {len(processes)}")
    print(f"  Perspectives: {len(perspectives)}")
    
    # Generate pattern data with IDs
    pattern_data = {
        "properties": [
            {"id": str(uuid.uuid4()), "name": prop, "type": "property", "domain": domain_name}
            for prop in properties
        ],
        "processes": [
            {"id": str(uuid.uuid4()), "name": proc, "type": "process", "domain": domain_name}
            for proc in processes
        ],
        "perspectives": [
            {"id": str(uuid.uuid4()), "name": persp, "type": "perspective", "domain": domain_name}
            for persp in perspectives
        ]
    }
    
    # Generate relationships
    # For 3D cube, we need relationships that connect all three dimensions
    num_relationships = random.randint(NUM_RELATIONSHIPS_MIN, NUM_RELATIONSHIPS_MAX)
    print(f"  Generating {num_relationships} relationships")
    
    relationships = []
    for _ in range(num_relationships):
        # Select random patterns
        property_data = random.choice(pattern_data["properties"])
        process_data = random.choice(pattern_data["processes"])
        perspective_data = random.choice(pattern_data["perspectives"])
        
        # Create relationship
        relationship = {
            "id": str(uuid.uuid4()),
            "property_id": property_data["id"],
            "process_id": process_data["id"],
            "perspective_id": perspective_data["id"],
            "strength": round(random.uniform(STRENGTH_MIN, STRENGTH_MAX), 2),
            "confidence": round(random.uniform(CONFIDENCE_MIN, CONFIDENCE_MAX), 2)
        }
        
        relationships.append(relationship)
    
    # Create the updated domain data structure
    updated_data = {
        "domain": domain_name,
        "version": data.get("version", "1.0"),
        "properties": properties,
        "processes": processes,
        "perspectives": perspectives,
        "patterns": {
            "properties": pattern_data["properties"],
            "processes": pattern_data["processes"],
            "perspectives": pattern_data["perspectives"]
        },
        "relationships": relationships,
        "metadata": data.get("metadata", {})
    }
    
    # Save updated data back to the file
    with open(file_path, 'w') as f:
        json.dump(updated_data, f, indent=2)
    
    print(f"  Updated {file_path}")


def main():
    """Main function to update all domain files."""
    if not DOMAINS_DIR.exists():
        print(f"Error: Directory {DOMAINS_DIR} does not exist")
        return
    
    # Get all domain JSON files (excluding index.json)
    domain_files = [f for f in DOMAINS_DIR.glob("*.json") if f.name != "index.json"]
    
    print(f"Found {len(domain_files)} domain files")
    
    # Update each domain file
    for file_path in domain_files:
        update_domain_file(file_path)
    
    print("All domain files updated successfully!")


if __name__ == "__main__":
    main() 