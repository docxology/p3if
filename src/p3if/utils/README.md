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

# Access settings (dot notation supported)
db_path = config.get("storage.path")
log_level = config.get("logging.level")

# Modify settings
config.set("visualization.theme", "dark")
config.save_to_file("config.json")
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

# Both backends expose async variants (e.g. save_pattern_async, get_pattern_async)
```

### Performance Monitoring (`performance.py`)

Performance tracking with timing, caching, and optional memory monitoring (`psutil` when available).

```python
from p3if.utils.performance import PerformanceMonitor, timed, cached

monitor = PerformanceMonitor()

@timed("analyze_data")
def analyze_data():
    # Execution is recorded under the "analyze_data" timer
    return process_data()

@cached(cache_key="expensive", ttl=300)
def expensive_operation(data):
    # Results cached for 5 minutes
    return compute_result(data)

# Manual timing
monitor.start_timer("run_analysis")
result = run_analysis()
monitor.end_timer("run_analysis")
print(monitor.get_metrics("run_analysis"))
print(monitor.get_summary_stats("run_analysis"))
```

### Output Organization (`output_organizer.py`)

Structured output management with session-based organization and metadata tracking.

```python
from p3if.utils.output_organizer import OutputOrganizer

organizer = OutputOrganizer("output")
session_path = organizer.create_session_structure("analysis_2024")

# Resolve organized paths for outputs
viz_path = organizer.get_visualization_path("network", "graph.html")
img_path = organizer.get_image_path("charts", "plot.png")

# Summarize the output directory
summary = organizer.get_session_summary()
print(summary["file_counts"])
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
from p3if.utils.performance import cached, performance_timer

@cached(cache_key="load_domain", ttl=600)  # Cache results for 10 minutes
def load_domain_data(domain_name):
    # Expensive data loading operation
    return fetch_domain_data(domain_name)

# Timer context manager
with performance_timer("analysis_block"):
    data = load_domain_data("healthcare")
    analysis = perform_analysis(data)
```

### Output Management

```python
from p3if.utils.output_organizer import OutputOrganizer
from p3if.visualization.interactive import InteractiveVisualizer

# Create organized output session
organizer = OutputOrganizer("output")
session_path = organizer.create_session_structure()

# Generate a visualization into the session's visualization path
visualizer = InteractiveVisualizer(framework)
viz_path = organizer.get_visualization_path("cube", "cube.html")
visualizer.generate_3d_cube_html(viz_path)

# Organize pre-existing files and build an index
organizer.organize_existing_files("misc_outputs")
organizer.create_output_index()

# Summarize the session
summary = organizer.get_session_summary()
print(f"Session directory: {session_path}")
print(f"Tracked files: {summary['file_counts']}")
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
# Test storage (including async variants)
pytest tests/unit/test_async_storage.py -v

# Test performance monitoring
pytest tests/unit/test_performance_monitoring.py -v

# Test logging
pytest tests/unit/test_logging.py -v
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
