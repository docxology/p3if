"""
P3IF Data Exporters

This module provides functions for exporting P3IF data to various file formats.
"""
import json
import csv
import logging
from pathlib import Path
from typing import Dict, List, Any, Union, Optional

import networkx as nx

from p3if_methods.framework import P3IFFramework
from p3if_methods.models import Property, Process, Perspective, Relationship

logger = logging.getLogger(__name__)


class DataExporter:
    """Class for exporting P3IF data to various file formats."""
    
    def __init__(self, framework: P3IFFramework):
        """
        Initialize the data exporter.
        
        Args:
            framework: P3IFFramework instance to export
        """
        self.framework = framework
    
    def export_to_json(self, file_path: Union[str, Path]) -> Path:
        """
        Export P3IF framework data to a JSON file.
        
        Args:
            file_path: Path where JSON file will be saved
            
        Returns:
            Path to the saved file
        """
        return export_to_json(self.framework, file_path)
    
    def export_to_csv(self, patterns_file: Union[str, Path], 
                    relationships_file: Union[str, Path]) -> Dict[str, Path]:
        """
        Export P3IF framework data to CSV files.
        
        Args:
            patterns_file: Path where patterns CSV will be saved
            relationships_file: Path where relationships CSV will be saved
            
        Returns:
            Dictionary with paths to saved files
        """
        return export_to_csv(self.framework, patterns_file, relationships_file)
    
    def export_to_graphml(self, file_path: Union[str, Path]) -> Path:
        """
        Export P3IF framework data to a GraphML file.
        
        Args:
            file_path: Path where GraphML file will be saved
            
        Returns:
            Path to the saved file
        """
        return export_to_graphml(self.framework, file_path)


def export_to_json(framework: P3IFFramework, file_path: Union[str, Path]) -> Path:
    """
    Export P3IF framework data to a JSON file.
    
    Args:
        framework: P3IFFramework instance to export
        file_path: Path where JSON file will be saved
        
    Returns:
        Path to the saved file
    """
    file_path = Path(file_path)
    logger.info(f"Exporting P3IF data to JSON: {file_path}")
    
    try:
        # Build the data structure
        data = {
            "properties": [],
            "processes": [],
            "perspectives": [],
            "relationships": []
        }
        
        # Export properties
        for prop in framework.get_all_patterns("property"):
            data["properties"].append({
                "id": prop.id,
                "name": prop.name,
                "description": prop.description,
                "domain": prop.domain,
                "tags": prop.tags
            })
        
        # Export processes
        for proc in framework.get_all_patterns("process"):
            data["processes"].append({
                "id": proc.id,
                "name": proc.name,
                "description": proc.description,
                "domain": proc.domain,
                "tags": proc.tags
            })
        
        # Export perspectives
        for persp in framework.get_all_patterns("perspective"):
            data["perspectives"].append({
                "id": persp.id,
                "name": persp.name,
                "description": persp.description,
                "domain": persp.domain,
                "tags": persp.tags
            })
        
        # Export relationships
        for rel in framework.get_all_relationships():
            data["relationships"].append({
                "id": rel.id,
                "property_id": rel.property_id,
                "process_id": rel.process_id,
                "perspective_id": rel.perspective_id,
                "strength": rel.strength,
                "confidence": rel.confidence
            })
        
        # Write to JSON file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Successfully exported data to {file_path}")
        return file_path
    
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        raise


def export_to_csv(framework: P3IFFramework, patterns_file: Union[str, Path], 
                 relationships_file: Union[str, Path]) -> Dict[str, Path]:
    """
    Export P3IF framework data to CSV files.
    
    Args:
        framework: P3IFFramework instance to export
        patterns_file: Path where patterns CSV file will be saved
        relationships_file: Path where relationships CSV file will be saved
        
    Returns:
        Dictionary with paths to the saved files
    """
    patterns_file = Path(patterns_file)
    relationships_file = Path(relationships_file)
    
    logger.info(f"Exporting P3IF patterns to CSV: {patterns_file}")
    logger.info(f"Exporting P3IF relationships to CSV: {relationships_file}")
    
    try:
        # Export patterns
        with open(patterns_file, 'w', newline='') as csvfile:
            fieldnames = ['id', 'type', 'name', 'description', 'domain', 'tags']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Export properties
            for prop in framework.get_all_patterns("property"):
                writer.writerow({
                    'id': prop.id,
                    'type': 'property',
                    'name': prop.name,
                    'description': prop.description,
                    'domain': prop.domain if prop.domain else '',
                    'tags': ','.join(prop.tags) if prop.tags else ''
                })
            
            # Export processes
            for proc in framework.get_all_patterns("process"):
                writer.writerow({
                    'id': proc.id,
                    'type': 'process',
                    'name': proc.name,
                    'description': proc.description,
                    'domain': proc.domain if proc.domain else '',
                    'tags': ','.join(proc.tags) if proc.tags else ''
                })
            
            # Export perspectives
            for persp in framework.get_all_patterns("perspective"):
                writer.writerow({
                    'id': persp.id,
                    'type': 'perspective',
                    'name': persp.name,
                    'description': persp.description,
                    'domain': persp.domain if persp.domain else '',
                    'tags': ','.join(persp.tags) if persp.tags else ''
                })
        
        # Export relationships
        with open(relationships_file, 'w', newline='') as csvfile:
            fieldnames = ['id', 'property_id', 'process_id', 'perspective_id', 'strength', 'confidence']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for rel in framework.get_all_relationships():
                writer.writerow({
                    'id': rel.id,
                    'property_id': rel.property_id if rel.property_id else '',
                    'process_id': rel.process_id if rel.process_id else '',
                    'perspective_id': rel.perspective_id if rel.perspective_id else '',
                    'strength': rel.strength,
                    'confidence': rel.confidence
                })
        
        logger.info(f"Successfully exported data to CSV files")
        return {
            'patterns': patterns_file,
            'relationships': relationships_file
        }
    
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        raise


def export_to_graphml(framework: P3IFFramework, file_path: Union[str, Path]) -> Path:
    """
    Export P3IF framework data to a GraphML file for use in network visualization tools.
    
    Args:
        framework: P3IFFramework instance to export
        file_path: Path where GraphML file will be saved
        
    Returns:
        Path to the saved file
    """
    file_path = Path(file_path)
    logger.info(f"Exporting P3IF data to GraphML: {file_path}")
    
    try:
        # Create a NetworkX graph
        G = nx.Graph()
        
        # Add nodes for all patterns
        for pattern_type in ["property", "process", "perspective"]:
            for pattern in framework.get_all_patterns(pattern_type):
                G.add_node(
                    pattern.id,
                    type=pattern_type,
                    name=pattern.name,
                    description=pattern.description,
                    domain=pattern.domain if pattern.domain else "",
                    tags=','.join(pattern.tags) if pattern.tags else ""
                )
        
        # Add edges for all relationships
        for rel in framework.get_all_relationships():
            # Get the patterns in this relationship
            patterns = []
            if rel.property_id:
                patterns.append(rel.property_id)
            if rel.process_id:
                patterns.append(rel.process_id)
            if rel.perspective_id:
                patterns.append(rel.perspective_id)
            
            # Add edges between all patterns in the relationship
            for i in range(len(patterns)):
                for j in range(i+1, len(patterns)):
                    G.add_edge(
                        patterns[i],
                        patterns[j],
                        rel_id=rel.id,
                        strength=rel.strength,
                        confidence=rel.confidence
                    )
        
        # Write to GraphML file
        nx.write_graphml(G, file_path)
        
        logger.info(f"Successfully exported data to GraphML: {file_path}")
        return file_path
    
    except Exception as e:
        logger.error(f"Error exporting to GraphML: {e}")
        raise 