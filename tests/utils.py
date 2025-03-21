"""
Test utilities for P3IF tests.
"""
import random
from typing import List, Dict, Any, Optional

from core.framework import P3IFFramework
from core.models import Property, Process, Perspective, Relationship


def create_test_framework(num_properties: int = 5,
                         num_processes: int = 5,
                         num_perspectives: int = 5,
                         num_relationships: int = 20,
                         domains: Optional[List[str]] = None) -> P3IFFramework:
    """
    Create a P3IF framework with test data.
    
    Args:
        num_properties: Number of properties to create
        num_processes: Number of processes to create
        num_perspectives: Number of perspectives to create
        num_relationships: Number of relationships to create
        domains: Optional list of domain names
        
    Returns:
        P3IFFramework instance with test data
    """
    # Create a new framework
    framework = P3IFFramework()
    
    # Use default domains if none provided
    if domains is None:
        domains = ["Domain A", "Domain B", "Domain C"]
    
    # Create properties
    properties = []
    for i in range(num_properties):
        domain = random.choice(domains) if domains else None
        prop = Property(
            name=f"Property {i}",
            description=f"Test property {i}",
            domain=domain,
            tags=["test", f"property-{i}"]
        )
        properties.append(prop)
        framework.add_pattern(prop)
    
    # Create processes
    processes = []
    for i in range(num_processes):
        domain = random.choice(domains) if domains else None
        proc = Process(
            name=f"Process {i}",
            description=f"Test process {i}",
            domain=domain,
            tags=["test", f"process-{i}"]
        )
        processes.append(proc)
        framework.add_pattern(proc)
    
    # Create perspectives
    perspectives = []
    for i in range(num_perspectives):
        domain = random.choice(domains) if domains else None
        persp = Perspective(
            name=f"Perspective {i}",
            description=f"Test perspective {i}",
            domain=domain,
            tags=["test", f"perspective-{i}"]
        )
        perspectives.append(persp)
        framework.add_pattern(persp)
    
    # Create relationships
    for _ in range(num_relationships):
        # Randomly decide which pattern types to include in this relationship
        include_property = random.random() > 0.2
        include_process = random.random() > 0.2
        include_perspective = random.random() > 0.2
        
        # Ensure at least two dimension types are included
        if sum([include_property, include_process, include_perspective]) < 2:
            types_to_include = random.sample(["property", "process", "perspective"], 2)
            include_property = "property" in types_to_include
            include_process = "process" in types_to_include
            include_perspective = "perspective" in types_to_include
        
        # Randomly select patterns
        property_id = random.choice(properties).id if include_property and properties else None
        process_id = random.choice(processes).id if include_process and processes else None
        perspective_id = random.choice(perspectives).id if include_perspective and perspectives else None
        
        # Create relationship
        relationship = Relationship(
            property_id=property_id,
            process_id=process_id,
            perspective_id=perspective_id,
            strength=random.random(),
            confidence=random.random()
        )
        
        try:
            framework.add_relationship(relationship)
        except ValueError:
            # If the relationship is invalid, skip it
            pass
    
    return framework


def create_multi_domain_test_framework(domains: List[str] = None,
                                     patterns_per_domain: int = 5,
                                     relationships_per_domain: int = 10,
                                     cross_domain_relationships: int = 5) -> P3IFFramework:
    """
    Create a P3IF framework with test data across multiple domains.
    
    Args:
        domains: List of domain names to use
        patterns_per_domain: Number of each pattern type to create per domain
        relationships_per_domain: Number of relationships within each domain
        cross_domain_relationships: Number of relationships that span domains
        
    Returns:
        P3IFFramework instance with multi-domain test data
    """
    if domains is None:
        domains = ["Domain A", "Domain B", "Domain C"]
    
    framework = P3IFFramework()
    
    # Create patterns for each domain
    domain_patterns = {}
    for domain in domains:
        domain_properties = []
        domain_processes = []
        domain_perspectives = []
        
        # Create properties for this domain
        for i in range(patterns_per_domain):
            prop = Property(
                name=f"{domain} Property {i}",
                description=f"Test property {i} in {domain}",
                domain=domain,
                tags=["test", domain.lower().replace(" ", "-"), f"property-{i}"]
            )
            domain_properties.append(prop)
            framework.add_pattern(prop)
        
        # Create processes for this domain
        for i in range(patterns_per_domain):
            proc = Process(
                name=f"{domain} Process {i}",
                description=f"Test process {i} in {domain}",
                domain=domain,
                tags=["test", domain.lower().replace(" ", "-"), f"process-{i}"]
            )
            domain_processes.append(proc)
            framework.add_pattern(proc)
        
        # Create perspectives for this domain
        for i in range(patterns_per_domain):
            persp = Perspective(
                name=f"{domain} Perspective {i}",
                description=f"Test perspective {i} in {domain}",
                domain=domain,
                tags=["test", domain.lower().replace(" ", "-"), f"perspective-{i}"]
            )
            domain_perspectives.append(persp)
            framework.add_pattern(persp)
        
        domain_patterns[domain] = {
            "property": domain_properties,
            "process": domain_processes,
            "perspective": domain_perspectives
        }
        
        # Create relationships within this domain
        for _ in range(relationships_per_domain):
            # Randomly decide which pattern types to include in this relationship
            include_property = random.random() > 0.2
            include_process = random.random() > 0.2
            include_perspective = random.random() > 0.2
            
            # Ensure at least two dimension types are included
            if sum([include_property, include_process, include_perspective]) < 2:
                types_to_include = random.sample(["property", "process", "perspective"], 2)
                include_property = "property" in types_to_include
                include_process = "process" in types_to_include
                include_perspective = "perspective" in types_to_include
            
            # Randomly select patterns from this domain
            property_id = random.choice(domain_patterns[domain]["property"]).id if include_property else None
            process_id = random.choice(domain_patterns[domain]["process"]).id if include_process else None
            perspective_id = random.choice(domain_patterns[domain]["perspective"]).id if include_perspective else None
            
            # Create relationship
            relationship = Relationship(
                property_id=property_id,
                process_id=process_id,
                perspective_id=perspective_id,
                strength=random.random(),
                confidence=random.random()
            )
            
            try:
                framework.add_relationship(relationship)
            except ValueError:
                # If the relationship is invalid, skip it
                pass
    
    # Create cross-domain relationships
    for _ in range(cross_domain_relationships):
        # Select two different domains
        domain1, domain2 = random.sample(domains, 2)
        
        # Randomly select pattern types to connect
        pattern_types = random.sample(["property", "process", "perspective"], 2)
        
        # Randomly select patterns from each domain
        pattern1_type = pattern_types[0]
        pattern2_type = pattern_types[1]
        
        pattern1 = random.choice(domain_patterns[domain1][pattern1_type])
        pattern2 = random.choice(domain_patterns[domain2][pattern2_type])
        
        # Create relationship data
        rel_data = {
            f"{pattern1_type}_id": pattern1.id,
            f"{pattern2_type}_id": pattern2.id,
            "strength": random.random(),
            "confidence": random.random()
        }
        
        # Set third dimension to None if not used
        third_type = next(t for t in ["property", "process", "perspective"] 
                        if t not in [pattern1_type, pattern2_type])
        rel_data[f"{third_type}_id"] = None
        
        # Create and add relationship
        try:
            relationship = Relationship(**rel_data)
            framework.add_relationship(relationship)
        except ValueError:
            # If the relationship is invalid, skip it
            pass
    
    return framework


def create_large_test_framework(num_properties: int = 20,
                               num_processes: int = 20,
                               num_perspectives: int = 20,
                               num_relationships: int = 100,
                               num_domains: int = 5) -> P3IFFramework:
    """
    Create a large P3IF framework with test data.
    
    Args:
        num_properties: Number of properties to create
        num_processes: Number of processes to create
        num_perspectives: Number of perspectives to create
        num_relationships: Number of relationships to create
        num_domains: Number of domains to create
        
    Returns:
        P3IFFramework instance with large test data
    """
    domains = [f"Domain {chr(65 + i)}" for i in range(num_domains)]
    return create_test_framework(
        num_properties=num_properties,
        num_processes=num_processes,
        num_perspectives=num_perspectives,
        num_relationships=num_relationships,
        domains=domains
    ) 