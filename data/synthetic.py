"""
P3IF Synthetic Data Generator

This module provides functionality for generating synthetic P3IF data.
"""
import random
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import json
from pathlib import Path
import os
import sys

# Add the project root to the path if this module is run directly
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

from core.models import Property, Process, Perspective, Relationship, Pattern
from core.framework import P3IFFramework


class SyntheticDataGenerator:
    """Generator for synthetic P3IF data across domains."""
    
    def __init__(self, domain_data_path: Optional[Union[str, Path]] = None):
        """
        Initialize the synthetic data generator.
        
        Args:
            domain_data_path: Optional path to domain data file or directory
        """
        self.logger = logging.getLogger(__name__)
        self.domains = {}
        self.domain_index = None
        
        if domain_data_path:
            self.load_domain_data(domain_data_path)
        else:
            # Load built-in domain data
            module_dir = Path(__file__).parent
            default_data_path = module_dir / "P3IF_Synthetic_Data.json"
            
            # Check if we have the new domain directory format
            domains_dir = module_dir / "domains"
            index_file = domains_dir / "index.json"
            
            if domains_dir.exists() and index_file.exists():
                self.logger.info(f"Loading domains from {domains_dir}")
                self.load_domain_index(index_file)
            elif default_data_path.exists():
                self.load_domain_data(default_data_path)
            else:
                # Attempt to find domains in the repo structure
                project_root = Path(__file__).parent.parent  # Go up to project root
                domains_dir = project_root / "data" / "domains"
                index_file = domains_dir / "index.json"
                
                if domains_dir.exists() and index_file.exists():
                    self.logger.info(f"Loading domains from repository at {domains_dir}")
                    self.load_domain_index(index_file)
                else:
                    self.logger.warning(f"No domain data found. Checked: {domains_dir}, {default_data_path}")
    
    def load_domain_index(self, index_path: Union[str, Path]) -> None:
        """
        Load domain index information from a JSON file.
        
        Args:
            index_path: Path to domain index file
        """
        try:
            with open(index_path, 'r') as f:
                self.domain_index = json.load(f)
            
            # Get the directory containing the index file
            index_dir = Path(index_path).parent
            
            self.logger.info(f"Loaded domain index with {len(self.domain_index.get('domains', []))} domains")
            
            # Load each domain referenced in the index
            for domain_info in self.domain_index.get("domains", []):
                domain_file = domain_info.get("file")
                if domain_file:
                    domain_path = index_dir / domain_file
                    self.load_domain_file(domain_path)
        
        except Exception as e:
            self.logger.error(f"Error loading domain index: {str(e)}")
    
    def load_domain_file(self, domain_path: Union[str, Path]) -> None:
        """
        Load a single domain file.
        
        Args:
            domain_path: Path to domain file
        """
        try:
            with open(domain_path, 'r') as f:
                domain_data = json.load(f)
            
            domain_name = domain_data.get("domain")
            if not domain_name:
                self.logger.warning(f"Domain file {domain_path} missing domain name, skipping")
                return
            
            # Extract the relevant properties, processes, and perspectives
            domain_info = {
                "properties": domain_data.get("properties", []),
                "processes": domain_data.get("processes", []),
                "perspectives": domain_data.get("perspectives", [])
            }
            
            self.domains[domain_name] = domain_info
            self.logger.info(f"Loaded domain {domain_name} from {domain_path}")
        
        except Exception as e:
            self.logger.error(f"Error loading domain file {domain_path}: {str(e)}")
    
    def load_domain_data(self, data_path: Union[str, Path]) -> None:
        """
        Load domain data from a file or directory.
        
        Args:
            data_path: Path to domain data file or directory
        """
        path = Path(data_path)
        
        # Check if it's a directory containing domain files
        if path.is_dir():
            # Look for an index file
            index_file = path / "index.json"
            if index_file.exists():
                self.load_domain_index(index_file)
            else:
                # Load all JSON files in the directory as domains
                for file_path in path.glob("*.json"):
                    self.load_domain_file(file_path)
            
            self.logger.info(f"Loaded {len(self.domains)} domains from directory {data_path}")
            return
            
        # Otherwise, assume it's a legacy format file with all domains
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
                self.domains = data.get("DOMAINS", {})
            self.logger.info(f"Loaded {len(self.domains)} domains from legacy file {data_path}")
        except Exception as e:
            self.logger.error(f"Error loading domain data: {str(e)}")
    
    def get_available_domains(self) -> List[str]:
        """
        Get a list of available domain names.
        
        Returns:
            List of domain names
        """
        return list(self.domains.keys())
    
    def get_domain_info(self, domain_name: str) -> Dict[str, Any]:
        """
        Get information about a specific domain.
        
        Args:
            domain_name: Name of the domain
            
        Returns:
            Dictionary containing domain information, or empty dict if not found
        """
        domain_data = self.domains.get(domain_name, {})
        
        # If we have the domain index, get additional information
        if self.domain_index:
            for domain_info in self.domain_index.get("domains", []):
                if domain_info.get("name") == domain_name:
                    return {
                        "name": domain_name,
                        "id": domain_info.get("id", domain_name.lower().replace(" ", "_")),
                        "counts": domain_info.get("counts", {
                            "properties": len(domain_data.get("properties", [])),
                            "processes": len(domain_data.get("processes", [])),
                            "perspectives": len(domain_data.get("perspectives", []))
                        })
                    }
        
        # If we don't have the index or domain not found in index
        if domain_data:
            return {
                "name": domain_name,
                "id": domain_name.lower().replace(" ", "_"),
                "counts": {
                    "properties": len(domain_data.get("properties", [])),
                    "processes": len(domain_data.get("processes", [])),
                    "perspectives": len(domain_data.get("perspectives", []))
                }
            }
        
        return {}
    
    def generate_for_domain(self, framework: P3IFFramework, domain_name: str, 
                            num_relationships: int = 100, 
                            strength_range: Tuple[float, float] = (0.0, 1.0),
                            include_all_patterns: bool = False) -> None:
        """
        Generate synthetic data for a specific domain.
        
        Args:
            framework: P3IF framework instance
            domain_name: Name of the domain to generate data for
            num_relationships: Number of relationships to generate
            strength_range: Range of relationship strengths
            include_all_patterns: Whether to include all patterns or only those in relationships
        """
        if domain_name not in self.domains:
            self.logger.error(f"Domain '{domain_name}' not found in domain data")
            return
        
        domain = self.domains[domain_name]
        
        # Generate patterns
        properties = []
        for prop_name in domain.get("properties", []):
            prop = Property(
                name=prop_name,
                description=f"Property: {prop_name}",
                domain=domain_name
            )
            properties.append(prop)
            framework.add_pattern(prop)
        
        processes = []
        for proc_name in domain.get("processes", []):
            proc = Process(
                name=proc_name,
                description=f"Process: {proc_name}",
                domain=domain_name
            )
            processes.append(proc)
            framework.add_pattern(proc)
        
        perspectives = []
        for persp_name in domain.get("perspectives", []):
            persp = Perspective(
                name=persp_name,
                description=f"Perspective: {persp_name}",
                domain=domain_name
            )
            perspectives.append(persp)
            framework.add_pattern(persp)
        
        # Generate relationships
        for _ in range(num_relationships):
            prop = random.choice(properties) if properties else None
            proc = random.choice(processes) if processes else None
            persp = random.choice(perspectives) if perspectives else None
            
            # Ensure at least two dimensions are connected
            while (prop is None and proc is None) or (prop is None and persp is None) or (proc is None and persp is None):
                prop = random.choice(properties) if properties else None
                proc = random.choice(processes) if processes else None
                persp = random.choice(perspectives) if perspectives else None
            
            strength = random.uniform(strength_range[0], strength_range[1])
            confidence = random.uniform(0.5, 1.0)
            
            relationship = Relationship(
                property_id=prop.id if prop else None,
                process_id=proc.id if proc else None,
                perspective_id=persp.id if persp else None,
                strength=strength,
                confidence=confidence
            )
            
            try:
                framework.add_relationship(relationship)
            except ValueError as e:
                self.logger.warning(f"Skipping invalid relationship: {str(e)}")
        
        self.logger.info(f"Generated synthetic data for domain '{domain_name}'")
    
    def generate_multi_domain(self, framework: P3IFFramework, 
                              domain_names: Optional[List[str]] = None,
                              relationships_per_domain: int = 100) -> None:
        """
        Generate synthetic data for multiple domains.
        
        Args:
            framework: P3IF framework instance
            domain_names: List of domain names to generate data for (if None, uses all domains)
            relationships_per_domain: Number of relationships per domain
        """
        if domain_names is None:
            domain_names = list(self.domains.keys())
        
        for domain_name in domain_names:
            if domain_name in self.domains:
                self.generate_for_domain(
                    framework=framework,
                    domain_name=domain_name,
                    num_relationships=relationships_per_domain
                )
            else:
                self.logger.warning(f"Domain '{domain_name}' not found, skipping")
        
        self.logger.info(f"Generated synthetic data for {len(domain_names)} domains")
    
    def generate_cross_domain_connections(self, framework: P3IFFramework, 
                                         num_connections: int = 50,
                                         min_strength: float = 0.3) -> None:
        """
        Generate cross-domain connections between patterns.
        
        Args:
            framework: P3IF framework instance
            num_connections: Number of cross-domain connections to generate
            min_strength: Minimum relationship strength for cross-domain connections
        """
        # Get all patterns by domain
        all_properties = framework.get_patterns_by_type("property")
        all_processes = framework.get_patterns_by_type("process")
        all_perspectives = framework.get_patterns_by_type("perspective")
        
        # Group by domain
        properties_by_domain = {}
        processes_by_domain = {}
        perspectives_by_domain = {}
        
        for prop in all_properties:
            domain = getattr(prop, "domain", None)
            if domain:
                if domain not in properties_by_domain:
                    properties_by_domain[domain] = []
                properties_by_domain[domain].append(prop)
        
        for proc in all_processes:
            domain = getattr(proc, "domain", None)
            if domain:
                if domain not in processes_by_domain:
                    processes_by_domain[domain] = []
                processes_by_domain[domain].append(proc)
        
        for persp in all_perspectives:
            domain = getattr(persp, "domain", None)
            if domain:
                if domain not in perspectives_by_domain:
                    perspectives_by_domain[domain] = []
                perspectives_by_domain[domain].append(persp)
        
        # Generate cross-domain connections
        for _ in range(num_connections):
            # Pick two different domains
            all_domains = list(set(list(properties_by_domain.keys()) + 
                                  list(processes_by_domain.keys()) + 
                                  list(perspectives_by_domain.keys())))
            
            if len(all_domains) < 2:
                self.logger.warning("Not enough domains for cross-domain connections")
                break
                
            domain1, domain2 = random.sample(all_domains, 2)
            
            # Pick patterns from each domain
            from_patterns = []
            if domain1 in properties_by_domain and properties_by_domain[domain1]:
                from_patterns.extend(properties_by_domain[domain1])
            if domain1 in processes_by_domain and processes_by_domain[domain1]:
                from_patterns.extend(processes_by_domain[domain1])
            if domain1 in perspectives_by_domain and perspectives_by_domain[domain1]:
                from_patterns.extend(perspectives_by_domain[domain1])
                
            to_patterns = []
            if domain2 in properties_by_domain and properties_by_domain[domain2]:
                to_patterns.extend(properties_by_domain[domain2])
            if domain2 in processes_by_domain and processes_by_domain[domain2]:
                to_patterns.extend(processes_by_domain[domain2])
            if domain2 in perspectives_by_domain and perspectives_by_domain[domain2]:
                to_patterns.extend(perspectives_by_domain[domain2])
            
            if not from_patterns or not to_patterns:
                continue
                
            # Create relationship between patterns
            from_pattern = random.choice(from_patterns)
            to_pattern = random.choice(to_patterns)
            
            # Set relationship based on pattern types
            property_id = None
            process_id = None
            perspective_id = None
            
            if from_pattern.type == "property":
                property_id = from_pattern.id
            elif from_pattern.type == "process":
                process_id = from_pattern.id
            elif from_pattern.type == "perspective":
                perspective_id = from_pattern.id
                
            if to_pattern.type == "property" and property_id is None:
                property_id = to_pattern.id
            elif to_pattern.type == "process" and process_id is None:
                process_id = to_pattern.id
            elif to_pattern.type == "perspective" and perspective_id is None:
                perspective_id = to_pattern.id
            
            # Check if we have at least two dimensions
            dimensions_present = sum(1 for dim in [property_id, process_id, perspective_id] if dim is not None)
            if dimensions_present < 2:
                continue
                
            strength = random.uniform(min_strength, 1.0)
            relationship = Relationship(
                property_id=property_id,
                process_id=process_id,
                perspective_id=perspective_id,
                strength=strength,
                confidence=random.uniform(0.7, 1.0),
                metadata={"cross_domain": True, "domains": [domain1, domain2]}
            )
            
            try:
                framework.add_relationship(relationship)
            except ValueError:
                pass
        
        self.logger.info(f"Generated {num_connections} cross-domain connections")
    
    def generate_domain(self, framework: P3IFFramework, domain_name: str, 
                        num_relationships: int = 100) -> None:
        """
        Generate data for a specific domain.
        
        Args:
            framework: P3IF framework instance
            domain_name: Name of the domain to generate
            num_relationships: Number of relationships to generate
        """
        return self.generate_for_domain(
            framework=framework,
            domain_name=domain_name,
            num_relationships=num_relationships
        ) 