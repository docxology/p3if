# P3IF Utils Package

Shared utility modules for the P3IF framework providing configuration management, data serialization, storage interfaces, performance monitoring, and output organization.

## Overview

The `utils` package contains essential utility modules that support the core P3IF framework operations:

- **Configuration Management**: Centralized settings and environment handling
- **JSON Utilities**: Enhanced JSON serialization with P3IF object support
- **Storage Interfaces**: Abstract storage layer with multiple backend implementations
- **Performance Monitoring**: Comprehensive performance tracking and optimization
- **Output Organization**: Structured file and directory management for outputs

## Modules

### Configuration (`config.py`)

Centralized configuration management system supporting JSON files, environment variables, and programmatic access.

```python
from p3if.utils.config import Config

# Load configuration
config = Config("config.json")

# Access settings
db_path = config.get("storage.path")
log_level = config.get("logging.level")

# Modify settings
config.set("visualization.theme", "dark")
config.save()
```

### JSON Utilities (`json.py`)

Enhanced JSON handling with automatic datetime conversion and P3IF object serialization.

```python
from p3if.utils.json import dumps, loads, P3IFEncoder

# Serialize P3IF objects
data = {"framework": framework, "timestamp": datetime.now()}
json_str = dumps(data)

# Deserialize with proper type conversion
decoded = loads(json_str)
```

### Storage System (`storage.py`)

Abstract storage interface with JSON and SQLite implementations for P3IF data persistence.

```python
from p3if.utils.storage import JSONStorage, SQLiteStorage

# JSON file storage
storage = JSONStorage("data.json")
storage.save_pattern(pattern)

# SQLite database storage
db_storage = SQLiteStorage("p3if.db")
patterns = db_storage.get_patterns_by_type("property")
```

### Performance Monitoring (`performance.py`)

Comprehensive performance tracking with caching, timing decorators, and memory monitoring.

```python
from p3if.utils.performance import PerformanceMonitor, timed, cached

@timed
def analyze_data():
    # Function execution is automatically timed
    return process_data()

@cached(max_size=100, ttl=300)
def expensive_operation(data):
    # Results cached for 5 minutes
    return compute_result(data)

# Manual monitoring
with PerformanceMonitor() as monitor:
    result = run_analysis()
print(f"Execution time: {monitor.get_metrics()['execution_time']}")
```

### Output Organization (`output_organizer.py`)

Structured output management with session-based organization and metadata tracking.

```python
from p3if.utils.output_organizer import OutputOrganizer

organizer = OutputOrganizer()
session_path = organizer.create_session("analysis_2024")

# Save outputs in organized structure
organizer.save_visualization("chart.html", session_path, "visualizations")
organizer.save_image("plot.png", session_path, "images")

# Generate session report
metadata = organizer.generate_metadata(session_path)
```

## Usage Patterns

### Configuration Setup

```python
from p3if.utils.config import Config
import os

# Initialize with defaults
config = Config()

# Load from file
config = Config("my_config.json")

# Environment-specific settings
if os.getenv("ENV") == "production":
    config.set("storage.type", "sqlite")
    config.set("logging.level", "WARNING")
```

### Data Persistence

```python
from p3if.utils.storage import SQLiteStorage
from p3if.core.models import Property

# Initialize storage
storage = SQLiteStorage("p3if.db")

# Store patterns
property_obj = Property(name="Security", domain="cybersecurity")
storage.save_pattern(property_obj)

# Query data
properties = storage.get_patterns_by_type("property")
security_props = [p for p in properties if "security" in p.name.lower()]
```

### Performance Optimization

```python
from p3if.utils.performance import PerformanceMonitor, cached

@cached(max_size=50, ttl=600)  # Cache 50 items for 10 minutes
def load_domain_data(domain_name):
    # Expensive data loading operation
    return fetch_domain_data(domain_name)

# Monitor overall performance
with PerformanceMonitor() as monitor:
    data = load_domain_data("healthcare")
    analysis = perform_analysis(data)

metrics = monitor.get_metrics()
print(f"Memory used: {metrics['memory_usage'] / 1024:.1f} KB")
print(f"Time elapsed: {metrics['execution_time']:.3f}s")
```

### Output Management

```python
from p3if.utils.output_organizer import OutputOrganizer
from p3if.visualization.interactive import InteractiveVisualizer

# Create organized output session
organizer = OutputOrganizer("output")
session_path = organizer.create_session()

# Generate and save visualizations
visualizer = InteractiveVisualizer(framework)
html_file = visualizer.generate_3d_cube_html(f"{session_path}/visualizations/cube.html")

# Save additional assets
organizer.save_data(framework_data, session_path, "data/framework.json")
organizer.save_report(analysis_report, session_path, "reports/analysis.md")

# Generate session summary
summary = organizer.generate_session_summary(session_path)
print(f"Session created: {summary['session_id']}")
print(f"Files generated: {summary['file_count']}")
```

## Integration with P3IF

The utils package integrates seamlessly with all P3IF components:

- **Configuration** is used by visualization, analysis, and core modules
- **JSON utilities** handle serialization in data import/export operations
- **Storage interfaces** provide persistence for `P3IFFramework` instances
- **Performance monitoring** integrates with analysis and visualization operations
- **Output organization** works with all generation and export functions

## Dependencies

The utils package has minimal dependencies and is designed to be lightweight:

- Standard library only (optional: `psutil` for enhanced performance monitoring)
- No external dependencies required for core functionality

## Testing

Run utility tests:

```bash
# Test all utilities
pytest tests/ -k "config or json or storage or performance" -v

# Test specific module
pytest tests/unit/test_config.py -v
```

## Error Handling

All utility modules include comprehensive error handling:

- **Configuration**: Validation of settings and file access
- **Storage**: Database connection and file I/O error handling
- **Performance**: Memory monitoring and resource limit handling
- **Output**: Directory creation and file permission handling

## Contributing

When adding new utilities:

1. Follow the established patterns and interfaces
2. Include comprehensive docstrings and type hints
3. Add unit tests covering all functionality
4. Update this README with new utility descriptions
5. Ensure backward compatibility

The utils package provides the essential infrastructure that enables robust, scalable operation of the P3IF framework across all use cases and environments.
