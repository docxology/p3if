# P3IF Utils Package

## Overview

The `utils` package provides shared utility modules that support the core P3IF framework operations. These utilities handle configuration management, data serialization, storage interfaces, performance monitoring, and output organization.

## Module Structure

```
utils/
├── __init__.py                 # Package initialization and imports
├── config.py                   # Configuration management system
├── json.py                     # JSON serialization utilities with P3IF encoders
├── storage.py                  # Storage interfaces and implementations
├── performance.py              # Performance monitoring and optimization
└── output_organizer.py         # Output organization for visualizations
```

## Core Components

### Configuration Management (`config.py`)

The `Config` class provides centralized configuration management for P3IF applications:

```python
from utils.config import Config

# Load default configuration
config = Config()

# Load from custom file
config = Config("custom_config.json")

# Access configuration values
storage_path = config.get("storage.path")
visualization_theme = config.get("visualization.default_style")
```

**Key Features:**
- Default configuration with sensible defaults
- JSON-based configuration files
- Environment variable support
- Validation and type checking

### JSON Utilities (`json.py`)

Specialized JSON handling for P3IF objects with custom encoders:

```python
from utils.json import P3IFEncoder, dumps, loads

# Encode P3IF objects with datetime support
data = {"pattern": pattern_object, "timestamp": datetime.now()}
json_str = dumps(data)

# Decode with custom handling
decoded = loads(json_str)
```

**Key Features:**
- `P3IFEncoder`: Custom JSON encoder for P3IF objects and datetime
- `convert_to_serializable()`: Convert objects to JSON-compatible format
- `dumps()` and `loads()`: Convenience functions with P3IF support

### Storage Interfaces (`storage.py`)

Abstract storage layer supporting multiple backends:

```python
from utils.storage import JSONStorage, SQLiteStorage, StorageInterface

# JSON file storage
storage = JSONStorage("p3if_data.json")

# SQLite database storage
storage = SQLiteStorage("p3if.db")

# Save and retrieve patterns
storage.save_pattern(pattern)
retrieved = storage.get_pattern(pattern.id)
```

**Key Features:**
- Abstract `StorageInterface` for backend flexibility
- JSON file storage implementation
- SQLite database storage implementation
- Pattern and relationship management
- Transaction support

### Performance Monitoring (`performance.py`)

Comprehensive performance tracking and optimization:

```python
from utils.performance import PerformanceMonitor, timed, cached

@timed
def expensive_operation():
    # Operation will be automatically timed
    pass

@cached(max_size=100, ttl=300)
def cached_function(data):
    # Results cached with LRU and TTL
    return process_data(data)

# Manual performance monitoring
with PerformanceMonitor() as monitor:
    result = perform_operation()
metrics = monitor.get_metrics()
```

**Key Features:**
- `@timed` decorator for automatic timing
- `@cached` decorator with LRU and TTL support
- `PerformanceMonitor` context manager
- Memory and CPU usage tracking
- Profiling and bottleneck identification

### Output Organization (`output_organizer.py`)

Structured output management for P3IF visualizations:

```python
from utils.output_organizer import OutputOrganizer

organizer = OutputOrganizer()
session_path = organizer.create_session("my_analysis")

# Save files in organized structure
organizer.save_visualization("cube.html", session_path, "visualizations")
organizer.save_image("network.png", session_path, "images")

# Generate session metadata
metadata = organizer.generate_metadata(session_path)
```

**Key Features:**
- Session-based directory organization
- Standard subdirectory structure (visualizations, images, animations, etc.)
- Metadata generation and tracking
- File organization and cleanup utilities

## Usage Patterns

### Configuration Setup

```python
from utils.config import Config

# Initialize with defaults
config = Config()

# Customize for specific use case
config.set("visualization.node_size", 60)
config.set("storage.type", "sqlite")

# Save configuration
config.save("my_config.json")
```

### Data Persistence

```python
from utils.storage import SQLiteStorage
from p3if_methods.models import Property

# Initialize storage
storage = SQLiteStorage("p3if.db")

# Create and store patterns
property_obj = Property(name="Security", domain="cybersecurity")
storage.save_pattern(property_obj)

# Query patterns
patterns = storage.get_patterns_by_type("property")
```

### Performance Optimization

```python
from utils.performance import PerformanceMonitor, cached

@cached(max_size=100, ttl=3600)
def analyze_patterns(patterns):
    # Expensive analysis cached for 1 hour
    return perform_complex_analysis(patterns)

# Monitor overall performance
with PerformanceMonitor() as monitor:
    results = analyze_patterns(large_dataset)
    print(f"Analysis took {monitor.get_metrics()['execution_time']:.2f}s")
```

## Integration with P3IF Core

The utils package integrates seamlessly with core P3IF components:

- **Configuration** is used by all major P3IF modules
- **JSON utilities** handle serialization in data export/import
- **Storage interfaces** are used by `P3IFFramework` for persistence
- **Performance monitoring** integrates with `PerformanceOptimizer`
- **Output organization** works with visualization modules

## Testing

Run utility tests:

```bash
python -m pytest p3if_tests/ -k "test_config or test_json or test_storage" -v
```

## Dependencies

Core dependencies:
- Standard library only (no external dependencies)
- Optional: `psutil` for enhanced performance monitoring

## Contributing

When adding new utilities:

1. Follow the established patterns and interfaces
2. Include comprehensive docstrings and type hints
3. Add unit tests in `p3if_tests/test_utils.py`
4. Update this documentation
5. Ensure backward compatibility

The utils package provides the foundational utilities that enable the robust, scalable operation of the P3IF framework across all domains and use cases.
