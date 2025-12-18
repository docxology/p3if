# P3IF Data Management

Data handling, import/export, and synthetic data generation for the P3IF framework.

## Components

### Domain Management
Handle domain-specific data structures and validation:

```python
from p3if.data.domains import DomainDataManager

manager = DomainDataManager()
healthcare_data = manager.load_domain("healthcare")
```

### Data Import/Export
Support multiple data formats with validation:

```python
from p3if.data.importers import DataImporter
from p3if.data.exporters import DataExporter

# Import
importer = DataImporter()
data = importer.import_json("healthcare.json")

# Export
exporter = DataExporter()
exporter.export_csv(data, "healthcare.csv")
```

### Synthetic Data Generation
Create realistic test data for development and testing:

```python
from p3if.data.synthetic import SyntheticDataGenerator

generator = SyntheticDataGenerator()
synthetic_data = generator.generate_domain_data(
    domain="healthcare",
    num_records=1000
)
```

## Supported Formats

### Import
- JSON: Structured domain data
- CSV: Tabular data
- XML: Hierarchical structures
- YAML: Configuration data

### Export
- JSON: Complete serialization
- CSV: Spreadsheet format
- XML: System integration
- YAML: Human-readable format

## Data Validation

```python
from p3if.data.domains import DomainValidator

validator = DomainValidator()
result = validator.validate_domain_data(data)

if not result.valid:
    for error in result.errors:
        print(f"Validation error: {error}")
```

## Testing

```bash
python -m pytest tests/unit/test_data.py
```





