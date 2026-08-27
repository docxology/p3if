# P3IF Data Management

Data handling, import/export, and synthetic data generation for the P3IF framework.

## Components

### Domain Management
Handle domain-specific data structures and validation:

```python
from p3if.data.domains import DomainManager
from p3if import P3IFFramework

manager = DomainManager(P3IFFramework())
stats = manager.get_domain_statistics("healthcare")
```

### Data Import/Export
Support multiple data formats with validation:

```python
from p3if.data.importers import import_from_json, import_from_csv
from p3if.data.exporters import DataExporter, export_to_json, export_to_csv

# Import (functions build/extend a P3IFFramework)
framework = import_from_json("healthcare.json")
framework = import_from_csv("patterns.csv", "relationships.csv")

# Export (DataExporter is constructed with a framework)
exporter = DataExporter(framework)
exporter.export_to_json("framework.json")
exporter.export_to_csv("patterns.csv", "relationships.csv")
```

### Synthetic Data Generation
Create realistic test data for development and testing:

```python
from p3if.data.synthetic import SyntheticDataGenerator
from p3if import P3IFFramework

generator = SyntheticDataGenerator()
framework = P3IFFramework()
generator.generate_for_domain(framework, "Healthcare", num_relationships=100)
```

## Supported Formats

### Import
- JSON: Structured domain/framework data
- CSV: Tabular patterns and relationships

### Export
- JSON: Complete framework serialization
- CSV: Patterns and relationships (separate files)
- GraphML: Graph-based interchange

## Data Validation

```python
from p3if.core.validation import ValidationEngine
from p3if import P3IFFramework

result = ValidationEngine().validate_framework(P3IFFramework())
print(f"Overall valid: {result['overall_valid']}")
for issue in result["issues"]:
    print(f"Issue: {issue}")
```

## Testing

```bash
python -m pytest tests/data/ -v
```





