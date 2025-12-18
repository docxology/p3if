# P3IF Tests Module - AI Agent Documentation

## Overview

The `tests/` directory contains the comprehensive test suite for the P3IF framework, ensuring reliability, performance, and correctness across all components.

## Test Structure

### Unit Tests (`unit/`)
- **Core Functionality**: Test individual components in isolation
- **Framework Operations**: Validate framework creation and manipulation
- **Model Validation**: Ensure data model integrity
- **Utility Functions**: Test helper and utility functions

### Integration Tests (`integration/`)
- **Component Interaction**: Test how components work together
- **API Endpoints**: Validate web API functionality
- **Workflow Testing**: End-to-end process validation

### Visualization Tests (`visualization/`)
- **Static Visualizations**: Test chart and graph generation
- **Interactive Components**: Validate user interaction handling
- **Animation Sequences**: Test animated visualization playback
- **Portal Functionality**: Web portal system testing

### Test Infrastructure
- **Fixtures**: Reusable test data and setup (`fixtures/`)
- **Configuration**: Pytest configuration (`conftest.py`)
- **Test Runners**: Execution scripts (`run_all_tests.py`)

## Testing Patterns

### Unit Test Structure
```python
import pytest
from p3if.core import P3IFCore

class TestP3IFCore:
    def test_framework_creation(self):
        """Test basic framework creation."""
        core = P3IFCore()
        framework = core.create_framework()

        assert framework is not None
        assert len(framework.patterns) == 0

    def test_pattern_addition(self):
        """Test adding patterns to framework."""
        core = P3IFCore()
        framework = core.create_framework()

        # Add property
        framework.add_property("Security", domain="cybersecurity")

        assert len(framework.properties) == 1
        assert framework.properties[0].name == "Security"
```

### Integration Test Structure
```python
def test_full_workflow(test_framework):
    """Test complete framework workflow."""
    # Setup
    framework = test_framework

    # Execute workflow
    result = process_framework_data(framework)

    # Validate results
    assert result["status"] == "success"
    assert "analysis" in result
    assert "visualization" in result
```

### Visualization Test Structure
```python
def test_cube_visualization():
    """Test 3D cube visualization generation."""
    from p3if.visualization.static import CubeVisualizer

    framework = create_test_framework()
    visualizer = CubeVisualizer()

    # Generate visualization
    result = visualizer.generate_cube_html(framework, "test_cube.html")

    # Validate output
    assert result["status"] == "success"
    assert Path("test_cube.html").exists()
```

## Test Data Management

### Fixtures
```python
@pytest.fixture
def test_framework():
    """Create test framework for testing."""
    core = P3IFCore()
    framework = core.create_framework()

    # Add test patterns
    framework.add_property("Test Property", domain="test")
    framework.add_process("Test Process", domain="test")
    framework.add_perspective("Test Perspective", domain="test")

    return framework

@pytest.fixture
def sample_data():
    """Provide sample domain data."""
    return {
        "domain": "healthcare",
        "records": [
            {"id": "P001", "condition": "diabetes"},
            {"id": "P002", "condition": "hypertension"}
        ]
    }
```

## Test Coverage Requirements

- **Unit Tests**: >90% coverage for all modules
- **Integration Tests**: Cover all major workflows
- **Error Conditions**: Test failure scenarios
- **Edge Cases**: Validate boundary conditions
- **Performance Tests**: Ensure acceptable performance

## Running Tests

### All Tests
```bash
python tests/run_all_tests.py
```

### Specific Test Categories
```bash
# Unit tests only
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Visualization tests
python -m pytest tests/visualization/
```

### With Coverage
```bash
python -m pytest --cov=p3if --cov-report=html tests/
```

## Test Development Guidelines

### Test Naming
- Use descriptive test names: `test_should_validate_framework_creation`
- Group related tests in classes: `TestFrameworkValidation`
- Use clear assertion messages

### Test Isolation
- Each test should be independent
- Use fixtures for common setup
- Clean up resources after tests

### Mock and Stub Usage
- **NEVER use mock methods or mock classes for P3IF components**
- **ALWAYS use real P3IF classes**: `P3IFFramework`, `Property`, `Process`, `Perspective`, `Relationship`
- **External dependencies may use pytest.skip**: Use `pytest.skip("dependency not available")` when external libraries (matplotlib, PIL, psutil) are not installed
- Prefer integration tests over heavily mocked unit tests
- All P3IF framework instances, patterns, and relationships should be real objects created with actual data

## Performance Testing

### Benchmarking
```python
def test_large_framework_performance(benchmark):
    """Test performance with large frameworks."""
    def create_large_framework():
        core = P3IFCore()
        framework = core.create_framework()

        # Add many patterns
        for i in range(1000):
            framework.add_property(f"Property{i}", domain="test")

        return framework

    # Benchmark framework creation
    result = benchmark(create_large_framework)
    assert result is not None
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

- **Fast Feedback**: Unit tests run quickly
- **Comprehensive Coverage**: Integration tests validate workflows
- **Quality Gates**: Coverage and quality thresholds
- **Parallel Execution**: Tests can run in parallel

## Dependencies

- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **pytest-benchmark**: Performance testing
- **fixtures**: Reusable test data

## Development Notes

- Write tests before implementing features (TDD)
- Keep tests fast and reliable
- Document test assumptions and requirements
- Update tests when refactoring code
- Use meaningful test data that represents real scenarios





