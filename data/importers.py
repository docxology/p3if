"""
P3IF Data Importers

This module provides functions for importing P3IF data from various file formats.
"""
import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Union, Optional

from p3if_methods.framework import P3IFFramework
from p3if_methods.models import Property, Process, Perspective, Relationship

logger = logging.getLogger(__name__)


def import_from_json(file_path: Union[str, Path], framework: Optional[P3IFFramework] = None) -> P3IFFramework:
    """
    Import P3IF data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        framework: Existing framework to import into (creates new one if None)
        
    Returns:
        P3IFFramework with imported data
    """
    if framework is None:
        framework = P3IFFramework()
    
    file_path = Path(file_path)
    logger.info(f"Importing P3IF data from JSON: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Import patterns
        for pattern_type in ['properties', 'processes', 'perspectives']:
            if pattern_type in data:
                for pattern_data in data[pattern_type]:
                    # Convert to singular for class name
                    singular_type = pattern_type[:-3] if pattern_type.endswith('ies') else pattern_type[:-1]
                    
                    # Create the pattern object
                    if singular_type == 'property':
                        pattern = Property(**pattern_data)
                    elif singular_type == 'process':
                        pattern = Process(**pattern_data)
                    elif singular_type == 'perspective':
                        pattern = Perspective(**pattern_data)
                    
                    # Add to framework
                    framework.add_pattern(pattern)
        
        # Import relationships
        if 'relationships' in data:
            for rel_data in data['relationships']:
                relationship = Relationship(**rel_data)
                framework.add_relationship(relationship)
        
        logger.info(f"Successfully imported data from {file_path}")
        return framework
    
    except Exception as e:
        logger.error(f"Error importing from JSON: {e}")
        raise


def import_from_csv(
    patterns_file: Union[str, Path],
    relationships_file: Union[str, Path],
    framework: Optional[P3IFFramework] = None
) -> P3IFFramework:
    """
    Import P3IF data from CSV files.
    
    Args:
        patterns_file: Path to CSV file containing patterns
        relationships_file: Path to CSV file containing relationships
        framework: Existing framework to import into (creates new one if None)
        
    Returns:
        P3IFFramework with imported data
    """
    if framework is None:
        framework = P3IFFramework()
    
    patterns_file = Path(patterns_file)
    relationships_file = Path(relationships_file)
    
    logger.info(f"Importing P3IF patterns from CSV: {patterns_file}")
    logger.info(f"Importing P3IF relationships from CSV: {relationships_file}")
    
    try:
        # Import patterns
        with open(patterns_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                pattern_type = row.get('type')
                
                if pattern_type == 'property':
                    pattern = Property(
                        name=row.get('name'),
                        description=row.get('description', ''),
                        domain=row.get('domain', None),
                        tags=row.get('tags', '').split(',') if row.get('tags') else []
                    )
                elif pattern_type == 'process':
                    pattern = Process(
                        name=row.get('name'),
                        description=row.get('description', ''),
                        domain=row.get('domain', None),
                        tags=row.get('tags', '').split(',') if row.get('tags') else []
                    )
                elif pattern_type == 'perspective':
                    pattern = Perspective(
                        name=row.get('name'),
                        description=row.get('description', ''),
                        domain=row.get('domain', None),
                        tags=row.get('tags', '').split(',') if row.get('tags') else []
                    )
                else:
                    logger.warning(f"Unknown pattern type: {pattern_type}")
                    continue
                
                framework.add_pattern(pattern)
        
        # Import relationships
        with open(relationships_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                relationship = Relationship(
                    property_id=row.get('property_id', None),
                    process_id=row.get('process_id', None),
                    perspective_id=row.get('perspective_id', None),
                    strength=float(row.get('strength', 0.0)),
                    confidence=float(row.get('confidence', 0.0))
                )
                framework.add_relationship(relationship)
        
        logger.info(f"Successfully imported data from CSV files")
        return framework
    
    except Exception as e:
        logger.error(f"Error importing from CSV: {e}")
        raise 