"""
P3IF Domain Manager

This module provides domain management functionality for P3IF.
"""
from typing import Dict, List, Any, Optional, Set, Union
import json
from pathlib import Path
import logging

from core.models import BasePattern, Property, Process, Perspective
from core.framework import P3IFFramework


class DomainManager:
    """Manager for P3IF domains."""
    
    def __init__(self, framework: P3IFFramework):
        """
        Initialize domain manager.
        
        Args:
            framework: P3IF framework instance
        """
        self.framework = framework
        self.logger = logging.getLogger(__name__)
    
    def get_domains(self) -> Set[str]:
        """
        Get all domains in the framework.
        
        Returns:
            Set of domain names
        """
        domains = set()
        
        # Check all pattern types for domains
        for pattern_type in ["property", "process", "perspective"]:
            patterns = self.framework.get_patterns_by_type(pattern_type)
            for pattern in patterns:
                domain = getattr(pattern, "domain", None)
                if domain:
                    domains.add(domain)
        
        return domains
    
    def get_patterns_by_domain(self, domain: str) -> Dict[str, List[BasePattern]]:
        """
        Get all patterns in a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Dictionary of pattern lists by type
        """
        result = {
            "property": [],
            "process": [],
            "perspective": []
        }
        
        # Get patterns for each type
        for pattern_type in result.keys():
            patterns = self.framework.get_patterns_by_type(pattern_type)
            for pattern in patterns:
                if getattr(pattern, "domain", None) == domain:
                    result[pattern_type].append(pattern)
        
        return result
    
    def get_domain_statistics(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a domain or all domains.
        
        Args:
            domain: Optional domain name (if None, gets stats for all domains)
            
        Returns:
            Dictionary of domain statistics
        """
        if domain:
            domains = [domain]
        else:
            domains = self.get_domains()
        
        result = {}
        for d in domains:
            patterns = self.get_patterns_by_domain(d)
            
            # Count relationships
            domain_relationships = 0
            for rel in self.framework._relationships.values():
                rel_patterns = []
                if rel.property_id:
                    prop = self.framework.get_pattern(rel.property_id)
                    if prop and getattr(prop, "domain", None) == d:
                        rel_patterns.append(prop)
                
                if rel.process_id:
                    proc = self.framework.get_pattern(rel.process_id)
                    if proc and getattr(proc, "domain", None) == d:
                        rel_patterns.append(proc)
                
                if rel.perspective_id:
                    persp = self.framework.get_pattern(rel.perspective_id)
                    if persp and getattr(persp, "domain", None) == d:
                        rel_patterns.append(persp)
                
                if len(rel_patterns) >= 2:
                    domain_relationships += 1
            
            result[d] = {
                "num_properties": len(patterns["property"]),
                "num_processes": len(patterns["process"]),
                "num_perspectives": len(patterns["perspective"]),
                "num_relationships": domain_relationships
            }
        
        return result
    
    def get_cross_domain_relationships(self) -> List[Dict[str, Any]]:
        """
        Get all cross-domain relationships.
        
        Returns:
            List of cross-domain relationship details
        """
        result = []
        
        for rel_id, rel in self.framework._relationships.items():
            domains = set()
            
            if rel.property_id:
                prop = self.framework.get_pattern(rel.property_id)
                if prop and hasattr(prop, "domain") and prop.domain:
                    domains.add(prop.domain)
            
            if rel.process_id:
                proc = self.framework.get_pattern(rel.process_id)
                if proc and hasattr(proc, "domain") and proc.domain:
                    domains.add(proc.domain)
            
            if rel.perspective_id:
                persp = self.framework.get_pattern(rel.perspective_id)
                if persp and hasattr(persp, "domain") and persp.domain:
                    domains.add(persp.domain)
            
            if len(domains) > 1:
                result.append({
                    "relationship_id": rel_id,
                    "domains": list(domains),
                    "strength": rel.strength,
                    "patterns": {
                        "property_id": rel.property_id,
                        "process_id": rel.process_id,
                        "perspective_id": rel.perspective_id
                    }
                })
        
        return result
    
    def export_domain(self, domain: str, file_path: Union[str, Path]) -> None:
        """
        Export a domain to a JSON file.
        
        Args:
            domain: Domain name
            file_path: Path to export file
        """
        patterns = self.get_patterns_by_domain(domain)
        
        # Flatten patterns
        all_patterns = []
        for pattern_list in patterns.values():
            all_patterns.extend(pattern_list)
        
        # Get all pattern IDs in the domain
        pattern_ids = {p.id for p in all_patterns}
        
        # Find relationships containing these patterns
        domain_relationships = []
        for rel in self.framework._relationships.values():
            rel_pattern_ids = []
            if rel.property_id and rel.property_id in pattern_ids:
                rel_pattern_ids.append(rel.property_id)
            if rel.process_id and rel.process_id in pattern_ids:
                rel_pattern_ids.append(rel.process_id)
            if rel.perspective_id and rel.perspective_id in pattern_ids:
                rel_pattern_ids.append(rel.perspective_id)
            
            if len(rel_pattern_ids) >= 2:
                domain_relationships.append(rel)
        
        # Export to JSON
        data = {
            "domain": domain,
            "patterns": [p.dict() for p in all_patterns],
            "relationships": [r.dict() for r in domain_relationships]
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Exported domain '{domain}' to {file_path}")
    
    def import_domain(self, file_path: Union[str, Path]) -> None:
        """
        Import a domain from a JSON file.
        
        Args:
            file_path: Path to import file
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        domain = data.get("domain")
        if not domain:
            self.logger.error("Missing domain name in import file")
            return
        
        # Import patterns
        pattern_map = {}  # Map old IDs to new IDs
        
        for pattern_data in data.get("patterns", []):
            pattern_type = pattern_data.get("type")
            
            if pattern_type == "property":
                pattern = Property(**pattern_data)
            elif pattern_type == "process":
                pattern = Process(**pattern_data)
            elif pattern_type == "perspective":
                pattern = Perspective(**pattern_data)
            else:
                # Create appropriate pattern type based on data
                pattern_type = pattern_data.get('type', 'property')
                if pattern_type == 'property':
                    pattern = Property(**pattern_data)
                elif pattern_type == 'process':
                    pattern = Process(**pattern_data)
                elif pattern_type == 'perspective':
                    pattern = Perspective(**pattern_data)
                else:
                    pattern = Property(**pattern_data)  # Default to Property
            
            old_id = pattern.id
            new_id = self.framework.add_pattern(pattern)
            pattern_map[old_id] = new_id
        
        # Import relationships
        for rel_data in data.get("relationships", []):
            # Update IDs
            if rel_data.get("property_id") in pattern_map:
                rel_data["property_id"] = pattern_map[rel_data["property_id"]]
            if rel_data.get("process_id") in pattern_map:
                rel_data["process_id"] = pattern_map[rel_data["process_id"]]
            if rel_data.get("perspective_id") in pattern_map:
                rel_data["perspective_id"] = pattern_map[rel_data["perspective_id"]]
            
            relationship = self.framework._relationships.get(rel_data.get("id"))
            if relationship:
                continue  # Skip existing relationship
            
            # Create new relationship
            from core.models import Relationship
            relationship = Relationship(**rel_data)
            
            try:
                self.framework.add_relationship(relationship)
            except ValueError as e:
                self.logger.warning(f"Skipping invalid relationship: {str(e)}")
        
        self.logger.info(f"Imported domain '{domain}' from {file_path}")
        
    def merge_domains(self, source_domains: List[str], target_domain: str) -> None:
        """
        Merge multiple domains into a new domain.
        
        Args:
            source_domains: List of source domain names
            target_domain: Target domain name
        """
        if not source_domains:
            self.logger.error("No source domains provided")
            return
        
        # Get patterns from all source domains
        all_source_patterns = []
        for domain in source_domains:
            domain_patterns = self.get_patterns_by_domain(domain)
            for pattern_list in domain_patterns.values():
                all_source_patterns.extend(pattern_list)
        
        # Create new patterns in target domain
        for pattern in all_source_patterns:
            # Create a copy with new ID and target domain
            if pattern.type == "property":
                new_pattern = Property(
                    name=pattern.name,
                    description=pattern.description,
                    tags=pattern.tags.copy(),
                    metadata=pattern.metadata.copy(),
                    domain=target_domain
                )
            elif pattern.type == "process":
                new_pattern = Process(
                    name=pattern.name,
                    description=pattern.description,
                    tags=pattern.tags.copy(),
                    metadata=pattern.metadata.copy(),
                    domain=target_domain
                )
            elif pattern.type == "perspective":
                new_pattern = Perspective(
                    name=pattern.name,
                    description=pattern.description,
                    tags=pattern.tags.copy(),
                    metadata=pattern.metadata.copy(),
                    domain=target_domain
                )
            else:
                continue
            
            self.framework.add_pattern(new_pattern)
        
        self.logger.info(f"Merged domains {source_domains} into {target_domain}") 