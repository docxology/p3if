"""
Test utilities for P3IF tests.
"""
import random
import json
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone
import pytest

from core.framework import P3IFFramework
from core.models import Property, Process, Perspective, Relationship, PatternType


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


def create_pattern_with_metadata(pattern_type: str = "property",
                                name: str = None,
                                domain: str = "test",
                                tags: List[str] = None,
                                quality_score: float = 0.8,
                                confidence: float = 0.9) -> Any:
    """
    Create a pattern with comprehensive metadata for testing.

    Args:
        pattern_type: Type of pattern to create ('property', 'process', 'perspective')
        name: Name for the pattern (auto-generated if None)
        domain: Domain for the pattern
        tags: Tags for the pattern
        quality_score: Quality score for the pattern
        confidence: Confidence score for the pattern

    Returns:
        Pattern instance with metadata
    """
    if name is None:
        name = f"Test {pattern_type.title()} {uuid.uuid4().hex[:8]}"

    if tags is None:
        tags = ["test", pattern_type, "metadata-test"]

    pattern_classes = {
        "property": Property,
        "process": Process,
        "perspective": Perspective
    }

    pattern_class = pattern_classes.get(pattern_type.lower())
    if not pattern_class:
        raise ValueError(f"Unknown pattern type: {pattern_type}")

    # Create base pattern data
    pattern_data = {
        "name": name,
        "description": f"Test {pattern_type} with metadata",
        "domain": domain,
        "tags": tags,
        "quality_score": quality_score,
        "confidence": confidence,
        "version": "1.0.0",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    # Add pattern-specific fields
    if pattern_type.lower() == "perspective":
        pattern_data["viewpoint"] = "Test viewpoint"

    return pattern_class(**pattern_data)


def create_relationship_with_metadata(property_id: str = None,
                                     process_id: str = None,
                                     perspective_id: str = None,
                                     strength: float = 0.7,
                                     confidence: float = 0.8,
                                     relationship_type: str = "correlation") -> Relationship:
    """
    Create a relationship with comprehensive metadata for testing.

    Args:
        property_id: ID of the property pattern
        process_id: ID of the process pattern
        perspective_id: ID of the perspective pattern
        strength: Strength of the relationship
        confidence: Confidence score for the relationship
        relationship_type: Type of relationship

    Returns:
        Relationship instance with metadata
    """
    return Relationship(
        property_id=property_id,
        process_id=process_id,
        perspective_id=perspective_id,
        strength=strength,
        confidence=confidence,
        relationship_type=relationship_type,
        direction="bidirectional",
        temporal_context="current",
        validity_period="2024-01-01T00:00:00Z/2024-12-31T23:59:59Z",
        evidence_sources=["test_source"],
        validation_method="automated",
        assumptions=["test_assumption"],
        status="active",
        quality_score=0.85,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


def create_test_patterns_with_relationships(num_patterns: int = 10,
                                           num_relationships: int = 25) -> P3IFFramework:
    """
    Create test patterns and relationships with realistic metadata.

    Args:
        num_patterns: Number of patterns to create per type
        num_relationships: Number of relationships to create

    Returns:
        P3IFFramework instance with test data
    """
    framework = P3IFFramework()

    # Create properties
    properties = []
    for i in range(num_patterns):
        prop = create_pattern_with_metadata(
            pattern_type="property",
            name=f"TestProperty{i:03d}",
            domain=f"Domain{i % 3 + 1}",
            quality_score=0.7 + random.random() * 0.3
        )
        properties.append(prop)
        framework.add_pattern(prop)

    # Create processes
    processes = []
    for i in range(num_patterns):
        proc = create_pattern_with_metadata(
            pattern_type="process",
            name=f"TestProcess{i:03d}",
            domain=f"Domain{i % 3 + 1}",
            quality_score=0.7 + random.random() * 0.3
        )
        processes.append(proc)
        framework.add_pattern(proc)

    # Create perspectives
    perspectives = []
    for i in range(num_patterns):
        persp = create_pattern_with_metadata(
            pattern_type="perspective",
            name=f"TestPerspective{i:03d}",
            domain=f"Domain{i % 3 + 1}",
            quality_score=0.7 + random.random() * 0.3
        )
        perspectives.append(persp)
        framework.add_pattern(persp)

    # Create relationships
    for i in range(num_relationships):
        # Randomly select pattern types to connect
        pattern_types = random.sample(["property", "process", "perspective"], 2)
        type1, type2 = pattern_types

        # Randomly select patterns
        pattern1 = random.choice(locals()[f"{type1}es"] if type1 == "process" else locals()[f"{type1}s"])
        pattern2 = random.choice(locals()[f"{type2}es"] if type2 == "process" else locals()[f"{type2}s"])

        # Create relationship data
        rel_data = {
            f"{type1}_id": pattern1.id,
            f"{type2}_id": pattern2.id,
            "strength": random.random(),
            "confidence": random.random(),
            "relationship_type": random.choice(["correlation", "causation", "dependency", "influence"]),
            "quality_score": 0.7 + random.random() * 0.3
        }

        # Set third dimension to None
        third_type = next(t for t in ["property", "process", "perspective"]
                         if t not in [type1, type2])
        rel_data[f"{third_type}_id"] = None

        try:
            relationship = Relationship(**rel_data)
            framework.add_relationship(relationship)
        except ValueError:
            # Skip invalid relationships
            pass

    return framework


# Test Fixtures
@pytest.fixture
def empty_framework():
    """Create an empty P3IF framework for testing."""
    return P3IFFramework()


@pytest.fixture
def small_framework():
    """Create a small framework with minimal test data."""
    return create_test_framework(
        num_properties=3,
        num_processes=3,
        num_perspectives=3,
        num_relationships=5
    )


@pytest.fixture
def medium_framework():
    """Create a medium-sized framework for testing."""
    return create_test_patterns_with_relationships(
        num_patterns=10,
        num_relationships=25
    )


@pytest.fixture
def large_framework():
    """Create a large framework for performance testing."""
    return create_test_patterns_with_relationships(
        num_patterns=50,
        num_relationships=200
    )


@pytest.fixture
def multi_domain_framework():
    """Create a framework with multiple domains."""
    return create_multi_domain_test_framework(
        domains=["Healthcare", "Finance", "Technology", "Education"],
        patterns_per_domain=8,
        relationships_per_domain=15,
        cross_domain_relationships=20
    )


def assert_framework_integrity(framework: P3IFFramework):
    """
    Assert that a framework maintains data integrity.

    Args:
        framework: P3IFFramework instance to check
    """
    # Check that all relationships reference existing patterns
    for relationship in framework._relationships.values():
        connected_patterns = relationship.get_connected_patterns()
        for pattern_id in connected_patterns:
            if pattern_id:
                assert pattern_id in framework._patterns, f"Relationship references non-existent pattern: {pattern_id}"

    # Check that pattern indexes are consistent
    assert len(framework._pattern_index) == len(framework._patterns), "Pattern index out of sync"
    assert len(framework._relationship_index) == len(framework._relationships), "Relationship index out of sync"

    # Check that all patterns are properly indexed
    for pattern_id in framework._patterns:
        assert pattern_id in framework._pattern_index, f"Pattern {pattern_id} not in index"

    for rel_id in framework._relationships:
        assert rel_id in framework._relationship_index, f"Relationship {rel_id} not in index"


def generate_test_json_data(num_patterns: int = 5, num_relationships: int = 10) -> Dict[str, Any]:
    """
    Generate test JSON data for import/export testing.

    Args:
        num_patterns: Number of patterns to generate
        num_relationships: Number of relationships to generate

    Returns:
        Dictionary containing test data
    """
    patterns = []
    relationships = []

    # Generate patterns
    for i in range(num_patterns):
        pattern_type = random.choice(["property", "process", "perspective"])
        pattern = {
            "id": str(uuid.uuid4()),
            "name": f"Test{pattern_type.title()}{i:03d}",
            "description": f"Test {pattern_type} pattern {i}",
            "pattern_type": pattern_type,
            "domain": f"Domain{random.randint(1, 3)}",
            "tags": [f"test-{pattern_type}", f"pattern-{i}"],
            "quality_score": round(0.7 + random.random() * 0.3, 2),
            "confidence": round(0.8 + random.random() * 0.2, 2),
            "version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        patterns.append(pattern)

    # Generate relationships
    for i in range(num_relationships):
        # Select two random patterns
        pattern1 = random.choice(patterns)
        pattern2 = random.choice(patterns)

        # Ensure different patterns
        while pattern1 == pattern2:
            pattern2 = random.choice(patterns)

        relationship = {
            "id": str(uuid.uuid4()),
            "property_id": pattern1["id"] if pattern1["pattern_type"] == "property" else None,
            "process_id": pattern1["id"] if pattern1["pattern_type"] == "process" else None,
            "perspective_id": pattern1["id"] if pattern1["pattern_type"] == "perspective" else None,
            "strength": round(random.random(), 2),
            "confidence": round(random.random(), 2),
            "relationship_type": random.choice(["correlation", "causation", "dependency"]),
            "direction": random.choice(["unidirectional", "bidirectional"]),
            "status": random.choice(["active", "deprecated", "experimental"]),
            "quality_score": round(0.7 + random.random() * 0.3, 2),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        # Set the second pattern's ID in the appropriate field
        if pattern2["pattern_type"] == "property" and not relationship["property_id"]:
            relationship["property_id"] = pattern2["id"]
        elif pattern2["pattern_type"] == "process" and not relationship["process_id"]:
            relationship["process_id"] = pattern2["id"]
        elif pattern2["pattern_type"] == "perspective" and not relationship["perspective_id"]:
            relationship["perspective_id"] = pattern2["id"]

        relationships.append(relationship)

    return {
        "patterns": patterns,
        "relationships": relationships,
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator": "test_utils",
            "version": "1.0.0"
        }
    } 