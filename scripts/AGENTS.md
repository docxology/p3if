# P3IF Scripts and Tools

## Overview

The `scripts/` directory contains all executable scripts and utilities for the P3IF framework. These tools provide command-line interfaces for development, testing, visualization, and system management, designed to work from the project root directory.

## Script Categories

### 🔧 **System Management**
Scripts for setting up and managing the P3IF development environment.

### 🧪 **Testing & Validation**
Comprehensive test suites and validation tools for code quality assurance.

### 🎨 **Visualization & Output**
Tools for generating visualizations, animations, and managing output files.

### 🔧 **Development & Maintenance**
Utilities for code maintenance, import management, and development workflow.

### 📚 **Documentation**
Tools for validating and maintaining project documentation.

## Core Scripts

### System Setup & Management

#### `setup_development.py`
Environment setup and dependency installation:

```bash
python scripts/setup_development.py
```

**Features:**
- Virtual environment creation
- Dependency installation
- Development tools setup
- Environment validation

#### `demo_modular_system.py`
Comprehensive system demonstration:

```bash
python scripts/demo_modular_system.py
```

**Features:**
- End-to-end P3IF workflow demonstration
- Modular component integration showcase
- Performance benchmarking
- Output organization examples

### Testing & Validation

#### `run_tests.py`
Comprehensive test suite execution:

```bash
python scripts/run_tests.py
```

**Features:**
- Full test suite execution
- Coverage reporting
- Performance metrics
- Cross-platform compatibility

#### `run_tests_simple.py`
Quick validation testing:

```bash
python scripts/run_tests_simple.py
```

**Features:**
- Fast test execution
- Core functionality validation
- Minimal dependency testing

#### `run_p3if_tests.py`
Legacy test runner (redirects to comprehensive runner):

```bash
python scripts/run_p3if_tests.py
```

**Note:** Maintained for backward compatibility.

#### `run_examples.py`
Execute all P3IF example orchestrators:

```bash
python scripts/run_examples.py
```

**Features:**
- Cognitive security orchestrator execution
- Framework integration examples
- Healthcare domain analysis
- Validation and error reporting

#### `validate_documentation.py`
Documentation quality validation:

```bash
python scripts/validate_documentation.py
```

**Features:**
- Markdown syntax validation
- Link checking
- Code example verification
- Consistency checking

#### `validate_documentation_accuracy.py`
Documentation accuracy verification:

```bash
python scripts/validate_documentation_accuracy.py
```

**Features:**
- Code-documentation synchronization
- Example accuracy validation
- API documentation verification

#### `benchmark_performance.py`
Performance analysis and benchmarking:

```bash
python scripts/benchmark_performance.py --output results.json
```

**Features:**
- Comprehensive performance metrics
- Memory usage analysis
- Execution time profiling
- Bottleneck identification

### Visualization & Output

#### `generate_final_visualizations.py`
Complete visualization pipeline:

```bash
python scripts/generate_final_visualizations.py
```

**Features:**
- PNG static visualizations
- GIF animated sequences
- HTML interactive interfaces
- Multi-format output generation

#### `run_multidomain_portal.py`
Multi-domain visualization portal:

```bash
python scripts/run_multidomain_portal.py --output-dir output
```

**Features:**
- Cross-domain visualization
- Interactive web portal
- Domain comparison tools
- Real-time data exploration

#### `fix_visualization_paths.py`
Visualization path correction:

```bash
python scripts/fix_visualization_paths.py
```

**Features:**
- Path normalization
- Link validation
- Asset organization

#### `ensure_website_references.py`
Website reference validation:

```bash
python scripts/ensure_website_references.py
```

**Features:**
- Link integrity checking
- Reference validation
- Asset availability verification

#### `view_p3if_website.py`
Website launcher:

```bash
python scripts/view_p3if_website.py
```

**Features:**
- Local web server startup
- Browser auto-launch
- Development server configuration

### Development & Maintenance

#### `update_domain_files.py`
Domain data management:

```bash
python scripts/update_domain_files.py
```

**Features:**
- Domain file updates
- Relationship data integration
- Data consistency validation

#### `update_imports.py`
Import statement management:

```bash
python scripts/update_imports.py
```

**Features:**
- Import optimization
- Dependency resolution
- Circular import detection

#### `verify_imports.py`
Import validation:

```bash
python scripts/verify_imports.py
```

**Features:**
- Import path verification
- Module availability checking
- Dependency validation

#### `test_3d_cube_with_domains.py`
3D visualization testing:

```bash
python scripts/test_3d_cube_with_domains.py
```

**Features:**
- 3D cube rendering validation
- Domain integration testing
- Visualization accuracy verification

## Interactive Terminal

### `interactive_terminal.sh` (Project Root)
Primary development interface:

```bash
./interactive_terminal.sh
```

**Features:**
- Menu-driven interface
- Comprehensive command execution
- Real-time output monitoring
- Development workflow automation

### `interactive_terminal_wrapper.sh`
Legacy wrapper script for backward compatibility.

## Output Organization

All scripts generate outputs in structured directories:

```
output/
├── p3if_output_YYYYMMDD_HHMMSS/    # Session-based organization
│   ├── visualizations/             # Interactive HTML files
│   ├── images/                     # Static PNG images
│   ├── animations/                 # GIF animation files
│   ├── data/                       # JSON data exports
│   ├── reports/                    # Analysis reports
│   └── session_metadata.json       # Session information
├── tests/                          # Test results and reports
├── examples/                       # Example execution outputs
└── logs/                           # Execution logs
```

## Script Architecture

### Common Patterns

All scripts follow consistent patterns:

1. **Argument Parsing**: Standard command-line argument handling
2. **Logging**: Comprehensive logging with configurable levels
3. **Error Handling**: Robust error handling with informative messages
4. **Output Organization**: Consistent file and directory organization
5. **Progress Reporting**: Progress indicators for long-running operations

### Configuration

Scripts use shared configuration:

```python
from utils.config import Config

config = Config()
output_dir = config.get("output.directory", "output")
log_level = config.get("logging.level", "INFO")
```

### Error Handling

Standardized error handling across scripts:

```python
try:
    # Script execution
    pass
except Exception as e:
    logger.error(f"Script execution failed: {e}")
    sys.exit(1)
```

## Development Workflow Integration

### Pre-commit Hooks

Scripts integrate with development workflows:

```bash
# Pre-commit validation
python scripts/validate_documentation.py
python scripts/run_tests_simple.py
```

### CI/CD Integration

Scripts designed for automated environments:

```yaml
# .github/workflows/ci.yml
- name: Run Tests
  run: python scripts/run_tests.py

- name: Generate Visualizations
  run: python scripts/generate_final_visualizations.py

- name: Validate Documentation
  run: python scripts/validate_documentation.py
```

## Performance Optimization

### Execution Optimization

Scripts include performance considerations:

- **Memory Management**: Efficient data structures for large datasets
- **Parallel Processing**: Multi-threading for CPU-intensive operations
- **Caching**: Result caching for repeated operations
- **Progress Monitoring**: Real-time progress reporting

### Resource Management

- **File Handle Management**: Proper resource cleanup
- **Memory Monitoring**: Large dataset handling
- **Timeout Handling**: Long-running operation management

## Testing Scripts

### Script Validation

Scripts include self-testing capabilities:

```bash
# Test script functionality
python scripts/run_tests.py --test-scripts

# Validate script outputs
python scripts/validate_script_outputs.py
```

### Integration Testing

End-to-end script integration testing:

```bash
# Full pipeline testing
python scripts/test_full_pipeline.py

# Cross-script compatibility
python scripts/test_script_integration.py
```

## Contributing to Scripts

### Adding New Scripts

When adding new scripts:

1. **Follow Naming Conventions**: Descriptive, action-oriented names
2. **Include Documentation**: Comprehensive docstrings and usage examples
3. **Add Error Handling**: Robust error handling and logging
4. **Test Coverage**: Include unit tests and integration tests
5. **Update Documentation**: Add to this AGENTS.md file

### Script Template

```python
#!/usr/bin/env python3
"""
Script description and usage examples.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import Config

def main():
    """Main script execution."""
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    # Logging setup
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO
    )
    logger = logging.getLogger(__name__)

    try:
        # Script implementation
        logger.info("Script execution started")

        # Implementation here

        logger.info("Script execution completed successfully")

    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Troubleshooting

### Common Issues

**Import Errors:**
- Ensure scripts are run from project root
- Check Python path configuration
- Verify dependency installation

**Permission Errors:**
- Check file/directory permissions
- Ensure write access to output directories
- Verify script execution permissions

**Memory Issues:**
- Monitor system resources during execution
- Use smaller datasets for testing
- Implement streaming for large data processing

**Path Issues:**
- Use absolute paths when possible
- Verify working directory
- Check path separators for cross-platform compatibility

## Future Enhancements

### Planned Improvements

1. **Script Orchestration**: Workflow automation for script sequences
2. **Parallel Execution**: Distributed script execution capabilities
3. **Web Interface**: Web-based script execution and monitoring
4. **Configuration Management**: Advanced script configuration options
5. **Result Caching**: Intelligent caching of script results

The scripts directory provides the operational interface for P3IF, enabling comprehensive development, testing, visualization, and maintenance workflows.





