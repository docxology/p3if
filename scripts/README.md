# P3IF Scripts

This directory contains all executable scripts and utilities for the P3IF framework.

## Core Scripts

### System Management
- **setup_development.py** - Set up development environment and install dependencies
- **demo_modular_system.py** - Comprehensive demonstration of P3IF modular capabilities

### Testing & Validation
- **run_tests.py** - Comprehensive test suite with detailed reporting
- **run_tests_simple.py** - Simple test runner for quick validation
- **run_p3if_tests.py** - Legacy test runner (redirects to comprehensive runner)
- **run_examples.py** - Execute all P3IF example orchestrators with validation
- **validate_documentation.py** - Validate documentation against project standards
- **validate_documentation_accuracy.py** - Verify documentation accuracy and completeness
- **benchmark_performance.py** - Performance benchmarking and analysis

### Development & Maintenance
- **update_domain_files.py** - Update domain files with relationship data
- **update_imports.py** - Update import statements across codebase
- **verify_imports.py** - Verify all imports are working correctly
- **test_3d_cube_with_domains.py** - Test 3D cube visualization with domain datasets

### Visualization & Output
- **run_multidomain_portal.py** - Generate multi-domain visualization portal
- **generate_final_visualizations.py** - Generate PNG/GIF visualizations and animations
- **fix_visualization_paths.py** - Fix website visualization file paths
- **ensure_website_references.py** - Ensure proper website file references
- **view_p3if_website.py** - Open P3IF website in browser

## Usage Examples

### Interactive Terminal
```bash
# Start interactive terminal (now at repository root)
./interactive_terminal.sh

# Or run all tests and examples
./interactive_terminal.sh --run-all
```

### Development Setup
```bash
# Set up development environment
python3 scripts/setup_development.py
```

### Run Tests
```bash
# Comprehensive test suite
python3 scripts/run_tests.py

# Simple test validation
python3 scripts/run_tests_simple.py

# Run example orchestrators
python3 scripts/run_examples.py
```

### Generate Visualizations
```bash
# Generate all visualizations and animations
python3 scripts/generate_final_visualizations.py

# Multi-domain portal
python3 scripts/run_multidomain_portal.py --output-dir output
```

### Performance Benchmarking
```bash
# Run comprehensive benchmarks
python3 scripts/benchmark_performance.py --output results.json
```

### Documentation Validation
```bash
# Validate documentation standards
python3 scripts/validate_documentation.py

# Verify documentation accuracy
python3 scripts/validate_documentation_accuracy.py
```

## Output Locations

All scripts generate outputs in organized directories:
- **Test Results**: `output/tests/` - Test reports, coverage, logs
- **Example Results**: `output/examples/` - Example execution outputs
- **Visualizations**: `output/visualizations/` - PNG, GIF, HTML outputs
- **Documentation**: `docs/` - Generated documentation and reports
- **Logs**: `logs/` - Execution logs and error reports

## Script Categories

### 🏗️ **System Setup & Management**
Scripts for setting up and managing the P3IF development environment.

**Note:** The interactive terminal (`./interactive_terminal.sh`) is located at the repository root for easy access. A wrapper script is available at `./interactive_terminal_wrapper.sh` for backward compatibility.

### 🧪 **Testing & Validation**
Comprehensive test suites and validation tools to ensure code quality.

### 🎨 **Visualization & Output**
Tools for generating visualizations, animations, and output files.

### 🔧 **Development & Maintenance**
Utilities for maintaining code quality, updating imports, and managing domains.

### 📚 **Documentation**
Tools for validating and maintaining project documentation.

All scripts are designed to be run from the project root directory and follow consistent patterns for logging, error handling, and output organization. 