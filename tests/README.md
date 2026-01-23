# P3IF Tests Package

This package contains comprehensive test suites for the P3IF (Properties, Processes, and Perspectives Inter-Framework) system, ensuring reliability, correctness, and performance across all components.

## Overview

The `tests` package provides a complete testing framework:

- **Unit Tests**: Individual component testing with comprehensive coverage
- **Integration Tests**: Cross-component interaction validation
- **Performance Tests**: Benchmarking and optimization validation
- **Visualization Tests**: Testing of visualization and animation systems
- **Validation Tests**: Framework integrity and constraint checking

## Architecture

```
tests/
├── __init__.py                    # Package initialization
├── conftest.py                    # Pytest configuration and fixtures
├── unit/                          # Unit tests
│   ├── test_framework.py         # P3IFFramework tests
│   ├── test_models.py            # Data model tests
│   ├── test_composition.py       # Composition and multiplexing tests
│   └── test_core.py              # Core functionality tests
├── integration/                   # Integration tests
│   └── test_integration.py       # Cross-component tests
├── fixtures/                      # Test fixtures and utilities
│   ├── __init__.py               # Fixture exports
│   └── helpers.py                # Test utilities and helpers
└── visualization/                 # Visualization system tests
    ├── __init__.py               # Visualization test package
    ├── test_base.py              # Base visualizer tests
    ├── test_interactive.py       # Interactive visualization tests
    ├── test_portal.py            # Portal system tests
    └── test_dashboard.py         # Dashboard generation tests
```

## Test Categories

### Core Framework Tests
Tests for the fundamental P3IF components:

- **Framework Creation and Management**: Basic framework operations
- **Pattern Management**: Property, Process, Perspective handling
- **Relationship Management**: Connection and dependency management
- **Data Import/Export**: Serialization and persistence
- **Validation**: Framework integrity and constraint checking

### Composition Tests
Tests for framework integration and composition:

- **Framework Overlay**: Combining multiple frameworks
- **Multiplexing**: Cross-dimensional element combination
- **Adapter Integration**: External framework integration
- **Conflict Resolution**: Handling framework conflicts

### Visualization Tests
Tests for visualization and animation systems:

- **Static Visualizations**: PNG generation and styling
- **Animated Sequences**: GIF creation and timing
- **Interactive Interfaces**: Web-based visualization interaction
- **Multi-Domain Portals**: Cross-domain visualization integration

### Performance Tests
Tests for system performance and optimization:

- **Benchmarking**: Operation timing and resource usage
- **Caching**: Cache effectiveness and performance
- **Memory Management**: Resource usage optimization
- **Scalability**: Large dataset handling

## Running Tests

### All Tests
```bash
# Run complete test suite
pytest tests/ -v

# Run with coverage analysis
pytest tests/ --cov=src/p3if --cov-report=html

# Run with parallel execution
pytest tests/ -n auto
```

### Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Visualization tests only
pytest tests/visualization/ -v

# Tests by marker
pytest tests/ -m unit -v
pytest tests/ -m integration -v
pytest tests/ -m visualization -v
```

### Individual Test Files
```bash
# Test specific components
pytest tests/unit/test_framework.py -v
pytest tests/visualization/test_interactive.py -v
```

## Test Utilities

### Test Fixtures
Reusable test data and setup utilities:

```python
from tests.fixtures import create_test_framework, create_multi_domain_test_framework

# Create standard test framework
framework = create_test_framework(num_properties=10, num_processes=8)

# Create multi-domain test framework
multi_domain = create_multi_domain_test_framework(domains=["healthcare", "finance"])
```

### Test Data Generation
Utilities for creating test datasets:

```python
from tests.fixtures import generate_test_json_data, create_pattern_with_metadata

# Generate test JSON data
test_data = generate_test_json_data(num_patterns=20, num_relationships=50)

# Create pattern with specific metadata
pattern = create_pattern_with_metadata(
    "property", "Security", domain="cybersecurity",
    quality_score=0.9, confidence=0.95
)
```

### Assertion Helpers
Utilities for common test assertions:

```python
from tests.fixtures import assert_framework_integrity

# Validate framework structure
assert_framework_integrity(framework)
```

## Test Coverage

### Coverage Goals
- **Core Framework**: >95% coverage
- **Visualization System**: >90% coverage
- **Composition Engine**: >95% coverage
- **API Endpoints**: >90% coverage

### Coverage Analysis
```bash
# Generate coverage report
pytest tests/ --cov=src/p3if --cov-report=html

# View coverage in browser
open htmlcov/index.html
```

## Test Organization

### Test Structure
Tests follow a consistent structure:

1. **Setup**: Create test fixtures and initialize components
2. **Execution**: Run the functionality being tested
3. **Assertions**: Verify expected behavior and outputs
4. **Cleanup**: Clean up any resources created during testing

### Test Naming Conventions
- `test_function_name()`: Test specific function
- `test_class_method()`: Test class method
- `test_integration_component_a_b()`: Integration between components
- `test_performance_operation()`: Performance testing

### Test Documentation
Each test includes clear documentation:

```python
def test_create_pattern_with_metadata():
    """Test pattern creation with metadata validation.

    Verifies that patterns can be created with metadata
    and that metadata is properly stored and retrieved.
    """
    # Test implementation
    pass
```

## Continuous Integration

### CI Pipeline Integration
Tests are designed to work with CI/CD pipelines:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e ".[dev]"
      - name: Run tests
        run: pytest tests/ --cov=src/p3if
```

## Debugging Tests

### Test Debugging Utilities
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run test with debugging
pytest tests/unit/test_core.py::TestP3IFCore::test_create_pattern -v -s
```

### Test Data Inspection
```python
# Inspect test framework data
from tests.fixtures import create_test_framework

framework = create_test_framework()
print(f"Framework has {len(framework._patterns)} patterns")

# Inspect relationships
relationships = framework.get_all_relationships()
print(f"Framework has {len(relationships)} relationships")
```

## Performance Testing

### Benchmarking Framework
```bash
# Run performance benchmarks
python scripts/benchmark_performance.py
```

### Memory Profiling
```python
# Profile memory usage
import tracemalloc
from tests.fixtures import create_large_test_framework

tracemalloc.start()
framework = create_large_test_framework()
current, peak = tracemalloc.get_traced_memory()
print(f"Memory usage: {current / 10**6:.2f}MB (peak: {peak / 10**6:.2f}MB)")
```

## Test Data Management

### Test Database
Tests use in-memory SQLite databases by default:

```python
from p3if.core.framework import P3IFFramework
from p3if.utils.storage import SQLiteStorage

# Test with persistent database
framework = P3IFFramework(SQLiteStorage("test_framework.db"))
```

### Test File Management
```python
# Clean up test files
import tempfile
import os

with tempfile.TemporaryDirectory() as tmpdir:
    # Create test files
    test_file = os.path.join(tmpdir, "test.json")
    # ... test code ...
```

## Contributing to Tests

### Adding New Tests
1. Create test file in appropriate directory
2. Follow naming conventions
3. Include comprehensive docstrings
4. Use test utilities and fixtures
5. Add performance considerations for large tests

### Test Review Checklist
- [ ] Tests are isolated and independent
- [ ] Tests use appropriate fixtures and utilities
- [ ] Tests include both positive and negative cases
- [ ] Tests validate error conditions
- [ ] Tests include performance considerations
- [ ] Tests have clear, descriptive names
- [ ] Tests include comprehensive docstrings

## Critical Rules

**NEVER use mocks for P3IF classes.** Always use real `Property`, `Process`, `Perspective`, and `Relationship` objects from `p3if.core.models`. Test with actual P3IF data structures.

## Quality Assurance

The test suite ensures:
- **Reliability**: All components work as expected
- **Performance**: System meets performance requirements
- **Compatibility**: Components work together correctly
- **Maintainability**: Code changes don't break existing functionality
- **Documentation**: Examples and documentation are accurate

## Support

For test-related issues:
1. Check existing test documentation
2. Review test failure logs
3. Consult the test utilities documentation
4. Create issues for test infrastructure problems

The comprehensive test suite ensures the P3IF system maintains high quality and reliability across all components and use cases.
