# P3IF Data Format Standard

This document describes the data format standard for P3IF (Properties, Processes, and Perspectives Inter-Framework).

## Overview

The P3IF data model is designed to be:
- **Flexible**: supporting various domains and use cases
- **Interoperable**: facilitating integration with other systems
- **Extendable**: allowing for growth and modification
- **Human-readable**: using clear, self-documenting JSON structures

## Directory Structure

```
p3if/data/
├── domains/               # Domain-specific data files
│   ├── index.json         # Index of all available domains
│   ├── healthcare.json    # Healthcare domain data
│   ├── blockchain.json    # Blockchain domain data
│   └── ...                # Other domain files
├── P3IF_Synthetic_Data.json  # Legacy combined format (deprecated)
└── README.md              # This documentation file
```

## Domain Index Format

The `domains/index.json` file contains a listing of all available domains and their metadata.

```json
{
  "domains": [
    {
      "name": "Healthcare",
      "id": "healthcare",
      "file": "healthcare.json",
      "counts": {
        "properties": 50,
        "processes": 50,
        "perspectives": 50
      }
    },
    // Additional domains...
  ],
  "version": "1.0",
  "timestamp": "2023-03-18"
}
```

## Domain Data Format

Each domain file follows a standardized structure:

```json
{
  "domain": "Domain Name",
  "version": "1.0",
  "properties": [
    "Property 1",
    "Property 2",
    ...
  ],
  "processes": [
    "Process 1",
    "Process 2",
    ...
  ],
  "perspectives": [
    "Perspective 1",
    "Perspective 2",
    ...
  ],
  "metadata": {
    "count": {
      "properties": 50,
      "processes": 50,
      "perspectives": 50
    }
  }
}
```

## Framework Data Format

When a P3IF framework is built from domain data, it combines patterns (properties, processes, perspectives) and relationships between them. The resulting framework can be exported in the following format:

```json
{
  "patterns": [
    {
      "id": "unique-id-1",
      "name": "Pattern Name",
      "type": "property",
      "description": "Description of the pattern",
      "domain": "DomainName",
      "metadata": {}
    },
    // More patterns...
  ],
  "relationships": [
    {
      "id": "unique-id-rel-1",
      "property_id": "property-id",
      "process_id": "process-id",
      "perspective_id": "perspective-id",
      "strength": 0.85,
      "confidence": 0.9,
      "metadata": {
        "cross_domain": false
      }
    },
    // More relationships...
  ],
  "metadata": {
    "exported_at": "2023-03-18T12:00:00Z",
    "framework_version": "2.0"
  }
}
```

## Loading Domain Data

To load domain data into a P3IF framework:

1. Use the `DomainManager` class to identify available domains
2. Select one or more domains to incorporate
3. Use the `SyntheticDataGenerator` to generate patterns and relationships based on domain data

Example Python code:

```python
from p3if.core.framework import P3IFFramework
from p3if.data.synthetic import SyntheticDataGenerator

# Create an empty framework
framework = P3IFFramework()

# Create a synthetic data generator with domain data
generator = SyntheticDataGenerator()
generator.load_domain_data("path/to/domains/index.json")

# Generate data for specific domains
generator.generate_for_domain(framework, "Healthcare", num_relationships=100)
generator.generate_for_domain(framework, "Blockchain", num_relationships=100)

# Add cross-domain connections
generator.generate_cross_domain_connections(framework, num_connections=50)

# Framework is now populated with domain data
```

## Multi-Domain Integration

One of P3IF's core strengths is the ability to integrate multiple domains. This is supported through:

1. **Domain Isolation**: Each domain can be treated as a separate entity
2. **Cross-Domain Connections**: Relationships can span across domains
3. **Framework Multiplexing**: Multiple domains can be combined into a single integrated framework

When creating cross-domain connections, the standard practice is to include metadata in the relationship to indicate the domains involved:

```json
{
  "id": "cross-domain-rel-1",
  "property_id": "healthcare-property-id",
  "process_id": "blockchain-process-id",
  "perspective_id": null,
  "strength": 0.75,
  "confidence": 0.8,
  "metadata": {
    "cross_domain": true,
    "domains": ["Healthcare", "Blockchain"]
  }
}
```

## Extending Domain Data

To extend existing domain data or create new domains:

1. Create a new JSON file following the domain data format
2. Add the domain to the index file (or create a new index)
3. Use the `DomainManager` to import the new domain data

## Visualizing Domain Data

The P3IF visualization components support domain-specific views, including:

- Domain filtering in dashboards
- Domain-specific portal tabs
- Cross-domain relationship highlighting
- Domain dropdown selectors for web interfaces

## Best Practices

1. **Domain Naming**: Use CamelCase for domain names (e.g., "HealthCare")
2. **Pattern Uniqueness**: Ensure pattern names are unique within their type and domain
3. **Cross-Domain Relationships**: Use metadata to clearly mark cross-domain relationships
4. **Version Control**: Include version information in all data files
5. **Documentation**: Document any domain-specific semantics or interpretations

## Data Migration

To migrate from the legacy combined format to the new domain-based format:

```bash
# Run the domain splitter script
python3 split_domains.py
```

This will split the `P3IF_Synthetic_Data.json` file into individual domain files in the `domains/` directory.

## Troubleshooting

Common issues:

- **Missing Domain Metadata**: Ensure all patterns have a `domain` attribute
- **Relationship Consistency**: Each relationship should connect at least two dimensions
- **Domain Index**: Verify that all domains are properly indexed
- **File Paths**: Use relative paths based on the project structure 