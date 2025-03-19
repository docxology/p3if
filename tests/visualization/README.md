# P3IF Visualization Tests

This directory contains tests for the P3IF visualization components. The tests verify that the visualization tools correctly generate visual representations of P3IF frameworks including interactive visualizations, dashboards, and web portals.

## Directory Structure

- `test_base.py`: Tests for the base Visualizer class
- `test_interactive.py`: Tests for interactive visualizations (3D cube, force graph)
- `test_dashboard.py`: Tests for dashboard generation 
- `test_portal.py`: Tests for the visualization portal
- `test_integrated_website.py`: Tests for the integrated website with selectors
- `test_config.py`: Configuration settings for visualization tests
- `test_output/`: Directory for test-generated output files
- `run_visualization_tests.py`: Script to run all visualization tests

## Test Output

All tests are configured to save their output files to the `test_output` directory. This includes:

- HTML files for interactive visualizations
- PNG images for static visualizations
- JSON data files
- Asset files (CSS, JS)
- Complete website portal files

The structure of the output is:

```
test_output/
  ├── assets/                   # CSS, JS, and image assets
  ├── visualizations/           # Visualization files
  │   ├── overview/             # Overview visualizations
  │   ├── domain/               # Domain-specific visualizations
  │   └── compare/              # Comparative visualizations
  ├── test_cube.html            # 3D cube visualization
  ├── test_graph.html           # Force-directed graph
  ├── test_portal.html          # Complete visualization portal
  ├── test_dashboard*.html      # Dashboard visualizations
  ├── test_*_dashboard/         # Dashboard image directories
  └── ...                       # Other test outputs
```

## Running Tests

You can run all visualization tests using pytest:

```bash
# Run all visualization tests
python -m pytest tests/visualization/

# Run specific test files
python -m pytest tests/visualization/test_interactive.py
python -m pytest tests/visualization/test_dashboard.py

# Run with verbose output
python -m pytest tests/visualization/ -v
```

Alternatively, you can use the dedicated test runner script:

```bash
cd tests/visualization/
python3 run_visualization_tests.py
```

## Test Descriptions

### Base Visualizer Tests

The `TestVisualizer` class in `test_base.py` tests the basic functionality of the base Visualizer class, including:

- Initializing with a framework and configuration
- Setting up visualization defaults
- Saving figures to files
- Generating color palettes for patterns and domains

### Interactive Visualization Tests

The `TestInteractiveVisualizer` class in `test_interactive.py` tests the generation of interactive visualizations:

- 3D cube visualization showing relationships between properties, processes, and perspectives
- Force-directed graph visualization showing the network of patterns and their relationships

### Dashboard Tests

The `TestDashboardGenerator` class in `test_dashboard.py` tests the generation of dashboards:

- Overview dashboards showing framework statistics and visualizations
- Domain-specific dashboards for analyzing individual domains
- Comparative dashboards for comparing multiple domains
- Interactive dashboard components with filters and selectors

### Portal Tests

The `TestVisualizationPortal` class in `test_portal.py` tests the generation of the visualization portal:

- Creating dataset dropdown selectors
- Creating component selectors
- Generating complete portal HTML with multiple visualizations
- Multi-domain portals with domain-specific tabs
- CSS styling and JavaScript functionality

### Integrated Website Tests

The `TestIntegratedWebsite` class in `test_integrated_website.py` tests the integration of various components:

- Dataset selector functionality
- Component selector functionality
- Full website with all features
- Loading different datasets via JavaScript
- Website export functionality
- Responsive website layout

## Interpreting Test Results

The tests verify that:

1. Visualization files are correctly generated
2. File content includes expected elements (HTML, JavaScript, CSS)
3. Interactive components function correctly
4. Visualizations are properly sized and formatted
5. Data from the framework is correctly represented in the visualizations

When tests pass, the generated output files in the `test_output` directory can be manually inspected to verify the quality and correctness of the visualizations.

## Troubleshooting

If tests fail:

1. Check that all dependencies are installed (see `requirements-test.txt`)
2. Verify that the `test_output` directory exists and is writable
3. Check for warnings in the test output that might indicate issues
4. Inspect any failed assertions to understand what specific aspect of the visualization is failing
5. Look at the generated files in the `test_output` directory to find discrepancies 