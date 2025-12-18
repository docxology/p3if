# P3IF Data Management

## Overview

The `data/` directory contains domain-specific data, synthetic data generators, and data management utilities for the P3IF framework. It provides the foundational datasets and tools for creating, managing, and importing domain knowledge into P3IF frameworks.

## Directory Structure

```
data/
├── __init__.py                     # Package initialization
├── domains/                        # Domain-specific data files
│   ├── index.json                 # Domain registry and metadata
│   ├── healthcare.json            # Healthcare domain patterns
│   ├── blockchain.json            # Blockchain domain patterns
│   ├── cybersecurity.json         # Cybersecurity domain patterns
│   └── [additional domain files]
├── domains.py                      # Domain management utilities
├── synthetic.py                    # Synthetic data generation
├── importers.py                    # Data import utilities
├── exporters.py                    # Data export utilities
└── README.md                       # Data format documentation
```

## Core Components

### Domain Data (`domains/`)

Structured domain-specific pattern collections:

```json
{
  "domain": "Healthcare",
  "version": "1.0",
  "properties": [
    "Patient Privacy",
    "Data Security",
    "Regulatory Compliance"
  ],
  "processes": [
    "Patient Registration",
    "Medical Record Management",
    "Treatment Planning"
  ],
  "perspectives": [
    "Clinical",
    "Administrative",
    "Patient-Centered"
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

### Domain Management (`domains.py`)

Utilities for working with domain data:

```python
from data.domains import DomainManager

manager = DomainManager()

# Load domain data
domains = manager.load_domains()

# Get patterns for specific domain
healthcare_patterns = manager.get_domain_patterns("healthcare")

# Validate domain structure
is_valid = manager.validate_domain("healthcare")
```

**Key Features:**
- Domain loading and validation
- Pattern extraction and organization
- Cross-domain relationship discovery
- Metadata management and statistics

### Synthetic Data Generation (`synthetic.py`)

Advanced synthetic data generation for testing and expansion:

```python
from data.synthetic import SyntheticDataGenerator

generator = SyntheticDataGenerator()

# Generate patterns for domain
generator.generate_for_domain(framework, "healthcare", num_patterns=100)

# Create cross-domain relationships
generator.generate_cross_domain_connections(framework, num_connections=50)

# Generate complete test framework
test_framework = generator.create_test_framework(num_domains=5)
```

**Key Features:**
- Realistic pattern generation
- Relationship strength modeling
- Confidence scoring
- Multi-domain integration
- Statistical distribution control

### Data Import/Export (`importers.py`, `exporters.py`)

Flexible data interchange capabilities:

```python
from data.importers import DataImporter
from data.exporters import DataExporter

# Import from external formats
importer = DataImporter()
framework = importer.from_json("external_data.json")
framework = importer.from_csv("patterns.csv")

# Export framework data
exporter = DataExporter()
exporter.to_json(framework, "export.json")
exporter.to_csv(framework, "patterns.csv")
```

**Key Features:**
- Multiple format support (JSON, CSV, XML)
- Data validation during import
- Schema mapping and transformation
- Batch processing capabilities

## Domain Registry (`domains/index.json`)

Central registry of available domains:

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
      },
      "version": "1.0",
      "last_updated": "2024-01-15"
    }
  ],
  "version": "1.0",
  "total_domains": 15
}
```

## Usage Patterns

### Loading Domain Data

```python
from data.domains import DomainManager

# Initialize domain manager
dm = DomainManager()

# Load all available domains
domains = dm.get_available_domains()

# Load specific domain data
healthcare_data = dm.load_domain("healthcare")

# Get domain statistics
stats = dm.get_domain_statistics("healthcare")
```

### Synthetic Data Generation

```python
from data.synthetic import SyntheticDataGenerator
from p3if_methods.framework import P3IFFramework

# Create framework and generator
framework = P3IFFramework()
generator = SyntheticDataGenerator()

# Populate with synthetic healthcare data
generator.generate_for_domain(framework, "healthcare", num_patterns=200)

# Add realistic relationships
generator.generate_relationships(framework, strength_mean=0.7, confidence_mean=0.8)

# Create cross-domain connections
generator.generate_cross_domain_connections(framework, domains=["healthcare", "finance"])
```

### Data Import/Export Workflow

```python
from data.importers import JSONImporter
from data.exporters import CSVExporter
from p3if_methods.framework import P3IFFramework

# Import data from external source
importer = JSONImporter()
framework = importer.import_framework("external_data.json")

# Process and enhance data
# ... framework operations ...

# Export in multiple formats
csv_exporter = CSVExporter()
csv_exporter.export_patterns(framework, "patterns.csv")
csv_exporter.export_relationships(framework, "relationships.csv")
```

## Data Quality Assurance

### Validation Framework

Built-in data validation ensures quality:

```python
from data.domains import DomainValidator

validator = DomainValidator()

# Validate domain file
issues = validator.validate_domain_file("healthcare.json")

# Check pattern consistency
consistency_score = validator.check_pattern_consistency(framework)

# Validate cross-domain relationships
cross_domain_valid = validator.validate_cross_domain_relationships(framework)
```

### Data Integrity Checks

- Pattern uniqueness within domains
- Relationship consistency
- Metadata completeness
- Schema compliance

## Domain Expansion

### Adding New Domains

Process for adding new domain data:

1. **Define Domain Structure**: Properties, processes, perspectives
2. **Create Domain File**: JSON format following established schema
3. **Update Registry**: Add to `domains/index.json`
4. **Generate Relationships**: Use synthetic generator for initial relationships
5. **Validate**: Run validation checks
6. **Test Integration**: Verify with existing domains

### Domain Template

```json
{
  "domain": "NewDomain",
  "version": "1.0",
  "properties": ["Property 1", "Property 2"],
  "processes": ["Process 1", "Process 2"],
  "perspectives": ["Perspective 1", "Perspective 2"],
  "metadata": {
    "count": {
      "properties": 2,
      "processes": 2,
      "perspectives": 2
    },
    "source": "Domain expert consultation",
    "last_updated": "2024-01-15"
  }
}
```

## Integration with P3IF Core

### Framework Population

Data modules integrate seamlessly with core P3IF:

```python
from p3if_methods.framework import P3IFFramework
from data.domains import DomainManager
from data.synthetic import SyntheticDataGenerator

# Create framework
framework = P3IFFramework()

# Load domain data
dm = DomainManager()
healthcare_patterns = dm.get_domain_patterns("healthcare")

# Add to framework
for pattern_data in healthcare_patterns:
    framework.add_pattern(pattern_data)

# Generate relationships
generator = SyntheticDataGenerator()
generator.generate_relationships(framework)
```

### Analysis Integration

Data provides foundation for analysis:

```python
from p3if_methods.analysis.meta import MetaAnalyzer
from data.domains import DomainManager

# Cross-domain analysis
meta_analyzer = MetaAnalyzer(framework)
domain_comparison = meta_analyzer.get_domain_comparison()

# Domain-specific insights
dm = DomainManager()
healthcare_insights = dm.analyze_domain_patterns("healthcare")
```

## Performance Considerations

### Data Loading Optimization

- Lazy loading for large domain files
- Caching of frequently accessed domains
- Memory-efficient data structures
- Background loading for web interfaces

### Generation Performance

- Batch processing for large datasets
- Parallel relationship generation
- Memory usage monitoring
- Progress tracking for long operations

## Testing

Run data module tests:

```bash
# Domain management tests
python -m pytest p3if_tests/ -k "test_domain" -v

# Synthetic data tests
python -m pytest p3if_tests/ -k "test_synthetic" -v

# Import/export tests
python -m pytest p3if_tests/ -k "test_import or test_export" -v
```

## Contributing

When adding new domain data:

1. Follow established JSON schema
2. Include comprehensive metadata
3. Ensure pattern uniqueness
4. Add cross-domain relationship opportunities
5. Update domain registry
6. Include validation tests

When extending data utilities:

1. Maintain backward compatibility
2. Add comprehensive error handling
3. Include performance optimizations
4. Update documentation
5. Add unit tests

The data management system provides the knowledge foundation that enables P3IF's powerful cross-domain analysis and integration capabilities.





