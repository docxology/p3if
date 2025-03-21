"""
P3IF Core Framework

This module contains the main P3IF framework class.
"""
from typing import Dict, List, Optional, Union, Any, Tuple, Set
import json
import logging
from pathlib import Path
from datetime import datetime
from uuid import UUID
import sys

# Add the project root to the path if this module is run directly
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

from core.models import Property, Process, Perspective, Relationship, Pattern
from utils.storage import StorageInterface


class P3IFFramework:
    """
    The main P3IF framework class responsible for managing patterns and relationships.
    
    This class provides an interface for working with P3IF data, including:
    - Adding, retrieving, and removing patterns of all types
    - Creating and managing relationships between patterns
    - Importing and exporting data
    - Framework operations like hot-swapping and multiplexing
    """
    
    def __init__(self, storage_backend: Optional[StorageInterface] = None):
        """
        Initialize a new P3IF framework instance.
        
        Args:
            storage_backend: Optional storage backend implementation
        """
        self.logger = logging.getLogger(__name__)
        self._storage = storage_backend
        
        # Initialize in-memory collections
        self._patterns: Dict[str, Pattern] = {}
        self._relationships: Dict[str, Relationship] = {}
        
        # Dimensionality config
        self._dimensions = {
            "property": Property,
            "process": Process,
            "perspective": Perspective
        }
    
    def add_pattern(self, pattern: Pattern) -> str:
        """
        Add a pattern to the framework.
        
        Args:
            pattern: The pattern to add
            
        Returns:
            The ID of the added pattern
        """
        self._patterns[pattern.id] = pattern
        if self._storage:
            self._storage.save_pattern(pattern)
        return pattern.id
        
    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """
        Retrieve a pattern by ID.
        
        Args:
            pattern_id: The ID of the pattern to retrieve
            
        Returns:
            The pattern, or None if not found
        """
        return self._patterns.get(pattern_id)
    
    def get_patterns_by_type(self, pattern_type: str) -> List[Pattern]:
        """
        Retrieve all patterns of a specific type.
        
        Args:
            pattern_type: The type of patterns to retrieve
            
        Returns:
            A list of patterns of the specified type
        """
        return [p for p in self._patterns.values() if p.type == pattern_type]
    
    def add_relationship(self, relationship: Relationship) -> str:
        """
        Add a relationship to the framework.
        
        Args:
            relationship: The relationship to add
            
        Returns:
            The ID of the added relationship
        """
        # Ensure at least two dimensions are connected
        dimensions_present = sum(
            1 for dim_id in [relationship.property_id, relationship.process_id, relationship.perspective_id] 
            if dim_id is not None
        )
        
        if dimensions_present < 2:
            raise ValueError("A relationship must connect at least two dimensions")
        
        self._relationships[relationship.id] = relationship
        if self._storage:
            self._storage.save_relationship(relationship)
        return relationship.id
    
    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """
        Retrieve a relationship by ID.
        
        Args:
            relationship_id: The ID of the relationship to retrieve
            
        Returns:
            The relationship, or None if not found
        """
        return self._relationships.get(relationship_id)
    
    def export_to_json(self, file_path: Optional[str] = None) -> Optional[str]:
        """
        Export the framework data to JSON.
        
        Args:
            file_path: Optional path to write the JSON to
            
        Returns:
            If file_path is None, returns the JSON string
        """
        data = {
            "patterns": [p.dict() for p in self._patterns.values()],
            "relationships": [r.dict() for r in self._relationships.values()],
            "metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "framework_version": "2.0"
            }
        }
        
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return None
        else:
            return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: Union[str, Path, Dict]) -> None:
        """
        Import framework data from JSON.
        
        Args:
            json_data: JSON string, file path, or dict
        """
        # Load data from various sources
        if isinstance(json_data, str) and Path(json_data).exists():
            with open(json_data, 'r') as f:
                data = json.load(f)
        elif isinstance(json_data, str):
            data = json.loads(json_data)
        elif isinstance(json_data, Path):
            with open(json_data, 'r') as f:
                data = json.load(f)
        elif isinstance(json_data, dict):
            data = json_data
        else:
            raise ValueError("Invalid JSON data format")
        
        # Process patterns
        for pattern_data in data.get("patterns", []):
            pattern_type = pattern_data.get("type")
            pattern_class = self._dimensions.get(pattern_type, Pattern)
            pattern = pattern_class(**pattern_data)
            self._patterns[pattern.id] = pattern
            if self._storage:
                self._storage.save_pattern(pattern)
        
        # Process relationships
        for rel_data in data.get("relationships", []):
            relationship = Relationship(**rel_data)
            self._relationships[relationship.id] = relationship
            if self._storage:
                self._storage.save_relationship(relationship)
    
    def hot_swap_dimension(self, old_dimension: str, new_dimension: str) -> None:
        """
        Hot-swap one dimension with another.
        
        Args:
            old_dimension: The dimension to replace
            new_dimension: The dimension to use as replacement
        """
        if old_dimension not in self._dimensions or new_dimension not in self._dimensions:
            valid_dimensions = list(self._dimensions.keys())
            raise ValueError(f"Both dimensions must be one of: {valid_dimensions}")
        
        for rel in self._relationships.values():
            old_attr = f"{old_dimension}_id"
            new_attr = f"{new_dimension}_id"
            
            if hasattr(rel, old_attr) and hasattr(rel, new_attr):
                old_value = getattr(rel, old_attr)
                if old_value:
                    setattr(rel, new_attr, old_value)
                    setattr(rel, old_attr, None)
                    rel.updated_at = datetime.utcnow()
                    
                    if self._storage:
                        self._storage.save_relationship(rel)
    
    def multiplex_frameworks(self, external_framework: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        Integrate patterns from an external framework.
        
        Args:
            external_framework: Dictionary containing patterns to integrate
        """
        for dimension, items in external_framework.items():
            if dimension not in self._dimensions:
                self.logger.warning(f"Unknown dimension: {dimension}")
                continue
                
            dimension_class = self._dimensions[dimension]
            for item_data in items:
                # Check if item already exists
                existing_items = [p for p in self._patterns.values() 
                                 if p.type == dimension and p.name == item_data.get("name")]
                
                if not existing_items:
                    # Create new pattern
                    pattern = dimension_class(**item_data)
                    self._patterns[pattern.id] = pattern
                    if self._storage:
                        self._storage.save_pattern(pattern)
    
    def clear(self) -> None:
        """Clear all patterns and relationships."""
        self._patterns.clear()
        self._relationships.clear()
        if self._storage:
            self._storage.clear()
            
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for the framework.
        
        Returns:
            Dictionary containing statistics
        """
        properties = [p for p in self._patterns.values() if p.type == "property"]
        processes = [p for p in self._patterns.values() if p.type == "process"]
        perspectives = [p for p in self._patterns.values() if p.type == "perspective"]
        
        strengths = [r.strength for r in self._relationships.values()]
        avg_strength = sum(strengths) / len(strengths) if strengths else 0
        
        return {
            "num_properties": len(properties),
            "num_processes": len(processes),
            "num_perspectives": len(perspectives),
            "num_relationships": len(self._relationships),
            "avg_relationship_strength": avg_strength
        } 