# P3IF Scripts

Thin orchestrator scripts for running P3IF components. All outputs go to `outputs/` subdirectories.

## Quick Start

```bash
# Run everything (tests, visualizations, benchmarks, examples, validation)
python scripts/run_all.py

# Run specific components
python scripts/run_all.py --tests
python scripts/run_all.py --viz
python scripts/run_all.py --bench
python scripts/run_all.py --examples
python scripts/run_all.py --validate

# Combine components
python scripts/run_all.py --tests --viz
```

## Core Scripts

| Script | Purpose | Output Directory |
|--------|---------|------------------|
| `run_all.py` | Master orchestrator - runs all components | `outputs/p3if_run_{timestamp}/` |
| `run_examples.py` | Run example orchestrators (cognitive security, healthcare, framework integration) | `outputs/examples/` |
| `generate_final_visualizations.py` | Generate all visualization types | `outputs/visualizations_{timestamp}/` |
| `benchmark_performance.py` | Performance benchmarks and metrics | User-specified or stdout |
| `validate_system.py` | System validation and health checks | `/tmp/p3if_comprehensive_report.json` |
| `setup_development.py` | Development environment setup | - |
| `view_p3if_website.py` | Launch local website for viewing | - |

## Output Structure

When running `run_all.py`, outputs are organized as:

```
outputs/
  p3if_run_{timestamp}/
    tests/
      junit.xml           # Test results in JUnit format
      coverage/           # HTML coverage report
      pytest_output.txt   # Raw pytest output
    visualizations/
      network/            # Network visualizations
      heatmap/            # Heatmap visualizations
      cube/               # 3D cube visualizations
      ...
    benchmarks/
      benchmark_results.json
      benchmark_output.txt
    examples/
      examples_results.json
    validation/
      validation_output.txt
    logs/
    run_all_results.json  # Summary of entire run
```

## Usage Examples

### Run Everything
```bash
python scripts/run_all.py
```
This runs all tests, generates visualizations, runs benchmarks, executes examples, and validates the system. Results are saved to a timestamped directory in `outputs/`.

### Run Tests Only
```bash
python scripts/run_all.py --tests
# Or use pytest directly
python -m pytest tests/ -v
```

### Generate Visualizations
```bash
python scripts/run_all.py --viz
# Or use the visualization script directly
python scripts/generate_final_visualizations.py
```

### Run Performance Benchmarks
```bash
python scripts/run_all.py --bench
# Or run directly with options
python scripts/benchmark_performance.py --quick
python scripts/benchmark_performance.py --full --output results.json
```

### Run Example Orchestrators
```bash
python scripts/run_all.py --examples
# Or run directly
python scripts/run_examples.py
```

### Validate System
```bash
python scripts/run_all.py --validate
# Or run directly
python scripts/validate_system.py
```

### View Website
```bash
python scripts/view_p3if_website.py
```

## Script Categories

### Master Orchestration
- **run_all.py** - Runs all components with organized output

### Testing & Validation
- **validate_system.py** - System health checks

### Visualization
- **generate_final_visualizations.py** - Generate all visualization types

### Performance
- **benchmark_performance.py** - Performance benchmarking

### Examples
- **run_examples.py** - Execute example orchestrators

### Development
- **setup_development.py** - Development environment setup
- **view_p3if_website.py** - View website locally

All scripts are designed to be run from the project root directory and follow consistent patterns for logging, error handling, and output organization.
