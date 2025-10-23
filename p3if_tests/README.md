# P3IF Tests Package

This package contains comprehensive test suites for the P3IF (Properties, Processes, and Perspectives Inter-Framework) system, ensuring reliability, correctness, and performance across all components.

## Overview

The `p3if_tests` package provides a complete testing framework:

- **Unit Tests**: Individual component testing with comprehensive coverage
- **Integration Tests**: Cross-component interaction validation
- **Performance Tests**: Benchmarking and optimization validation
- **Visualization Tests**: Testing of visualization and animation systems
- **Validation Tests**: Framework integrity and constraint checking

## Architecture

```
p3if_tests/
├── __init__.py                    # Package initialization
├── core/                          # Core framework tests
│   ├── test_framework.py         # P3IFFramework tests
│   └── test_models.py           # Data model tests
├── test_composition.py           # Composition and multiplexing tests
├── test_core.py                  # Core functionality tests
├── utils.py                      # Test utilities and fixtures
├── run_all_tests.py              # Comprehensive test runner
├── requirements-test.txt         # Test-specific dependencies
├── visualization/                # Visualization system tests
│   ├── __init__.py              # Visualization test package
│   ├── run_all_tests.py         # Visualization test runner
│   ├── test_base.py             # Base visualizer tests
│   ├── test_interactive.py      # Interactive visualization tests
│   ├── test_portal.py           # Portal system tests
│   ├── test_dashboard.py        # Dashboard generation tests
│   ├── test_integrated_website.py # Full integration tests
│   └── requirements-test.txt    # Visualization test dependencies
└── website/                      # Website and API tests
    └── test_api.py               # API endpoint tests
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
python p3if_tests/run_all_tests.py

# Run with coverage analysis
python p3if_tests/run_all_tests.py --coverage

# Run with parallel execution
python p3if_tests/run_all_tests.py --parallel
```

### Specific Test Categories
```bash
# Core framework tests
python -m pytest p3if_tests/test_core.py -v

# Composition tests
python -m pytest p3if_tests/test_composition.py -v

# Visualization tests
python -m pytest p3if_tests/visualization/ -v

# Performance tests
python -m pytest p3if_tests/test_performance.py -v
```

### Individual Test Files
```bash
# Test specific components
python -m pytest p3if_tests/core/test_framework.py -v
python -m pytest p3if_tests/visualization/test_interactive.py -v
```

## Test Utilities

### Test Fixtures
Reusable test data and setup utilities:

```python
from p3if_tests.utils import create_test_framework, create_multi_domain_test_framework

# Create standard test framework
framework = create_test_framework(num_properties=10, num_processes=8)

# Create multi-domain test framework
multi_domain = create_multi_domain_test_framework(domains=["healthcare", "finance"])
```

### Test Data Generation
Utilities for creating test datasets:

```python
from p3if_tests.utils import generate_test_json_data, create_pattern_with_metadata

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
from p3if_tests.utils import assert_framework_integrity, assert_relationship_validity

# Validate framework structure
assert_framework_integrity(framework)

# Validate relationship properties
assert_relationship_validity(relationship, expected_strength=0.8)
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
python -m pytest --cov=p3if_methods --cov-report=html

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
          pip install -r p3if_tests/requirements-test.txt
      - name: Run tests
        run: python p3if_tests/run_all_tests.py --coverage
```

## Debugging Tests

### Test Debugging Utilities
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run test with debugging
python -m pytest p3if_tests/test_core.py::TestP3IFCore::test_create_pattern -v -s
```

### Test Data Inspection
```python
# Inspect test framework data
framework = create_test_framework()
print(f"Framework has {len(framework)} patterns")

# Inspect relationships
relationships = framework.get_all_relationships()
print(f"Framework has {len(relationships)} relationships")
```

## Performance Testing

### Benchmarking Framework
```python
from p3if_tests.utils import benchmark_operation

# Benchmark framework operations
results = benchmark_operation(
    "framework_creation",
    lambda: create_test_framework(num_patterns=100),
    iterations=10
)
print(f"Average creation time: {results['avg_time']:.4f}s")
```

### Memory Profiling
```python
# Profile memory usage
import tracemalloc

tracemalloc.start()
framework = create_large_test_framework()
current, peak = tracemalloc.get_traced_memory()
print(f"Memory usage: {current / 10**6:.2f}MB (peak: {peak / 10**6:.2f}MB)")
```

## Test Data Management

### Test Database
Tests use in-memory SQLite databases by default:

```python
# Test with persistent database
framework = P3IFFramework(SQLiteStorage("test_framework.db"))
```

### Test File Management
```python
# Clean up test files
import tempfile
import shutil

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

## Test Results and Reporting

### Test Report Generation
```python
from p3if_tests.run_all_tests import TestRunner

runner = TestRunner(verbose=True, coverage=True)
report = runner.run_all_tests()
print(f"Tests passed: {report['passed']}")
print(f"Tests failed: {report['failed']}")
```

### Coverage Reporting
```python
# Generate detailed coverage report
runner = TestRunner(coverage=True)
report = runner.run_all_tests()
coverage_data = report['coverage']
print(f"Overall coverage: {coverage_data['overall']:.2%}")
```

## Troubleshooting

### Common Test Issues

**Import Errors**
- Ensure all dependencies are installed
- Check Python path and virtual environment
- Verify package structure is correct

**Test Timeouts**
- Increase timeout for slow tests
- Use smaller test datasets for quick iteration
- Implement test data caching

**Memory Issues**
- Use smaller datasets for memory-intensive tests
- Implement cleanup in test teardown
- Monitor memory usage during test runs

**Flaky Tests**
- Add retry logic for network-dependent tests
- Use deterministic test data
- Avoid time-dependent assertions

## Integration with Development Workflow

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: python -m pytest
        language: system
        pass_filenames: false
        args: [p3if_tests/test_core.py, --tb=short]
```

### GitHub Actions Integration
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: python p3if_tests/run_all_tests.py
```

## Maintenance

### Test Data Updates
Regularly update test data to reflect:
- New framework features
- Performance improvements
- API changes
- Bug fixes

### Test Suite Expansion
Add tests for:
- New visualization types
- Additional framework integrations
- Performance optimizations
- Edge cases and error conditions

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

