"""
P3IF Basic Analyzer

This module provides basic analysis capabilities for P3IF data.
"""
from typing import Dict, List, Any, Optional
import logging
import pandas as pd
import numpy as np
from collections import Counter

from core.framework import P3IFFramework
from core.models import BasePattern, Relationship


class BasicAnalyzer:
    """Basic analyzer for P3IF data."""
    
    def __init__(self, framework: P3IFFramework):
        """
        Initialize basic analyzer.
        
        Args:
            framework: P3IF framework instance
        """
        self.framework = framework
        self.logger = logging.getLogger(__name__)
    
    def get_pattern_distribution(self) -> Dict[str, int]:
        """
        Get distribution of patterns by type.
        
        Returns:
            Dictionary of pattern counts by type
        """
        result = {}
        for pattern_type in ["property", "process", "perspective"]:
            result[pattern_type] = len(self.framework.get_patterns_by_type(pattern_type))
        return result
    
    def get_relationship_strength_statistics(self) -> Dict[str, float]:
        """
        Get statistics about relationship strengths.
        
        Returns:
            Dictionary of relationship strength statistics
        """
        if not self.framework._relationships:
            return {
                "min": 0.0,
                "max": 0.0,
                "mean": 0.0,
                "median": 0.0,
                "std": 0.0
            }
        
        strengths = [r.strength for r in self.framework._relationships.values()]
        
        return {
            "min": min(strengths),
            "max": max(strengths),
            "mean": np.mean(strengths),
            "median": np.median(strengths),
            "std": np.std(strengths)
        }
    
    def get_strongest_relationships(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the strongest relationships.
        
        Args:
            top_n: Number of relationships to return
            
        Returns:
            List of strongest relationships with details
        """
        if not self.framework._relationships:
            return []
        
        # Sort relationships by strength
        sorted_relationships = sorted(
            self.framework._relationships.values(), 
            key=lambda r: r.strength, 
            reverse=True
        )
        
        result = []
        for r in sorted_relationships[:top_n]:
            relationship_info = {
                "id": r.id,
                "strength": r.strength,
                "confidence": r.confidence,
                "patterns": {}
            }
            
            # Add pattern information
            if r.property_id:
                prop = self.framework.get_pattern(r.property_id)
                if prop:
                    relationship_info["patterns"]["property"] = {
                        "id": prop.id,
                        "name": prop.name,
                        "domain": getattr(prop, "domain", None)
                    }
            
            if r.process_id:
                proc = self.framework.get_pattern(r.process_id)
                if proc:
                    relationship_info["patterns"]["process"] = {
                        "id": proc.id,
                        "name": proc.name,
                        "domain": getattr(proc, "domain", None)
                    }
            
            if r.perspective_id:
                persp = self.framework.get_pattern(r.perspective_id)
                if persp:
                    relationship_info["patterns"]["perspective"] = {
                        "id": persp.id,
                        "name": persp.name,
                        "domain": getattr(persp, "domain", None)
                    }
            
            result.append(relationship_info)
        
        return result
    
    def get_tag_distribution(self) -> Dict[str, int]:
        """
        Get distribution of tags across all patterns.
        
        Returns:
            Dictionary of tag counts
        """
        tag_counter = Counter()
        
        for pattern in self.framework._patterns.values():
            tag_counter.update(pattern.tags)
        
        return dict(tag_counter)
    
    def get_pattern_activity(self) -> Dict[str, Dict[str, int]]:
        """
        Get activity metrics for patterns.
        
        Returns:
            Dictionary mapping pattern types to dictionaries of pattern IDs and relationship counts
        """
        result = {
            "property": {},
            "process": {},
            "perspective": {}
        }
        
        # Count relationships for each pattern
        for rel in self.framework._relationships.values():
            if rel.property_id:
                result["property"][rel.property_id] = result["property"].get(rel.property_id, 0) + 1
            if rel.process_id:
                result["process"][rel.process_id] = result["process"].get(rel.process_id, 0) + 1
            if rel.perspective_id:
                result["perspective"][rel.perspective_id] = result["perspective"].get(rel.perspective_id, 0) + 1
        
        return result
    
    def get_most_connected_patterns(self, top_n: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the most connected patterns by type.
        
        Args:
            top_n: Number of patterns to return for each type
            
        Returns:
            Dictionary mapping pattern types to lists of pattern details
        """
        pattern_activity = self.get_pattern_activity()
        result = {}
        
        for pattern_type, pattern_counts in pattern_activity.items():
            # Sort patterns by connection count
            sorted_patterns = sorted(
                pattern_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            pattern_list = []
            for pattern_id, count in sorted_patterns[:top_n]:
                pattern = self.framework.get_pattern(pattern_id)
                if pattern:
                    pattern_list.append({
                        "id": pattern.id,
                        "name": pattern.name,
                        "connection_count": count,
                        "domain": getattr(pattern, "domain", None)
                    })
            
            result[pattern_type] = pattern_list
        
        return result
    
    def get_pattern_similarity_matrix(self, pattern_type: str) -> Dict[str, Any]:
        """
        Generate a similarity matrix for patterns of a specific type.
        
        Args:
            pattern_type: Type of patterns to analyze
            
        Returns:
            Dictionary containing matrix data and pattern information
        """
        patterns = self.framework.get_patterns_by_type(pattern_type)
        if not patterns:
            return {"matrix": [], "patterns": []}
        
        # Create a mapping of pattern IDs to indices
        pattern_map = {p.id: i for i, p in enumerate(patterns)}
        
        # Initialize similarity matrix
        n = len(patterns)
        similarity_matrix = np.zeros((n, n))
        
        # Calculate similarities based on shared relationships
        for rel in self.framework._relationships.values():
            rel_patterns = []
            
            if pattern_type == "property" and rel.property_id and rel.property_id in pattern_map:
                rel_patterns.append(rel.property_id)
            elif pattern_type == "process" and rel.process_id and rel.process_id in pattern_map:
                rel_patterns.append(rel.process_id)
            elif pattern_type == "perspective" and rel.perspective_id and rel.perspective_id in pattern_map:
                rel_patterns.append(rel.perspective_id)
            
            # If we found patterns of the specified type, analyze their shared relationships
            if rel_patterns:
                for pattern_id in rel_patterns:
                    idx = pattern_map[pattern_id]
                    # A pattern is similar to itself
                    similarity_matrix[idx, idx] += 1
                    
                    # Calculate similarity with other patterns based on sharing the same relationship
                    for other_id_attr in ["property_id", "process_id", "perspective_id"]:
                        other_id = getattr(rel, other_id_attr)
                        if other_id and other_id in pattern_map and other_id != pattern_id:
                            other_idx = pattern_map[other_id]
                            similarity_matrix[idx, other_idx] += 1
                            similarity_matrix[other_idx, idx] += 1
        
        # Normalize similarity matrix
        row_sums = similarity_matrix.sum(axis=1)
        # Only divide by row_sums where it's not zero to avoid warnings
        mask = row_sums != 0
        similarity_matrix_normalized = np.zeros_like(similarity_matrix, dtype=float)
        if mask.any():  # Only perform division if there are non-zero elements
            similarity_matrix_normalized[mask] = similarity_matrix[mask] / row_sums[mask, np.newaxis]
        similarity_matrix = np.nan_to_num(similarity_matrix_normalized)
        
        pattern_info = [
            {
                "id": p.id,
                "name": p.name,
                "domain": getattr(p, "domain", None)
            }
            for p in patterns
        ]
        
        return {
            "matrix": similarity_matrix.tolist(),
            "patterns": pattern_info
        }
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Run a full basic analysis.
        
        Returns:
            Dictionary containing all analysis results
        """
        return {
            "pattern_distribution": self.get_pattern_distribution(),
            "relationship_strength_stats": self.get_relationship_strength_statistics(),
            "strongest_relationships": self.get_strongest_relationships(),
            "tag_distribution": self.get_tag_distribution(),
            "most_connected_patterns": self.get_most_connected_patterns(),
            "property_similarity": self.get_pattern_similarity_matrix("property"),
            "process_similarity": self.get_pattern_similarity_matrix("process"),
            "perspective_similarity": self.get_pattern_similarity_matrix("perspective")
        } 