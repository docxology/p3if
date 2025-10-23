# P3IF Visualization Package

This package provides comprehensive visualization and animation capabilities for P3IF (Properties, Processes, and Perspectives Inter-Framework) data, including static images, animated sequences, and interactive web interfaces.

## Overview

The `p3if_visualization` package offers a complete visualization ecosystem:

- **Static Visualizations**: High-resolution PNG images for publication and presentation
- **Animated Sequences**: GIF animations showing dynamic framework evolution
- **Interactive Interfaces**: Web-based 3D visualizations with real-time manipulation
- **Multi-Domain Portals**: Unified interfaces for exploring multiple domains
- **Dashboard Generation**: Comprehensive analytics dashboards and reports

## Architecture

```
p3if_visualization/
├── __init__.py                 # Package initialization
├── base.py                     # Base visualizer classes
├── interactive.py              # Interactive visualization engine
├── interactive_3d.py           # 3D visualization components
├── animated_dimensions.py      # Animation and dimension visualization
├── portal.py                   # Multi-domain portal generation
├── multi_domain_portal.py      # Multi-domain analysis portal
├── orchestrator.py             # Visualization orchestration
├── network.py                  # Network graph visualizations
├── network_visualizations.py   # Network visualization generators
├── matrix.py                   # Matrix visualization engine
├── matrix_visualizations.py    # Matrix visualization generators
├── cube_visualizations.py      # 3D cube visualization generators
├── list_visualizations.py      # List-based visualizations
├── grid_visualizations.py      # Grid-based visualizations
├── heatmap_visualizations.py   # Heatmap visualization generators
├── hierarchy_visualizations.py # Hierarchical visualizations
├── statistical_visualizations.py # Statistical analysis visualizations
├── animation_visualizations.py  # Animation sequence generators
└── dashboard.py                # Dashboard generation
```

## Core Components

### InteractiveVisualizer
Main entry point for interactive visualization generation.

```python
from p3if_visualization.interactive import InteractiveVisualizer

visualizer = InteractiveVisualizer(framework, config)
cube_data = visualizer.generate_3d_cube_data()
html_file = visualizer.generate_3d_cube_html("output/cube.html", cube_data)
```

### Interactive3DVisualizer
Advanced 3D visualization with animation capabilities.

```python
from p3if_visualization.interactive_3d import Interactive3DVisualizer

viz = Interactive3DVisualizer(framework_data)
scatter_plot = viz.create_3d_scatter_plot("all")
rotation_anim = viz.create_animated_visualization("rotation")
```

### VisualizationPortal
Multi-domain portal generation with unified interface.

```python
from p3if_visualization.portal import VisualizationPortal

portal = VisualizationPortal(framework, config)
portal.generate_portal("output/portal.html", include_dataset_dropdown=True)
```

## Visualization Types

### Static Visualizations (PNG)
- **Network Graphs**: Force-directed layouts with customizable styling
- **Statistical Charts**: Distribution analysis and confidence metrics
- **Matrix Views**: Cross-tabulation of relationships
- **3D Cube Projections**: 2D representations of 3D data

### Animated Visualizations (GIF)
- **Component Rotation**: P3IF framework components orbiting central core
- **Dimension Evolution**: Progressive dimension highlighting
- **Relationship Formation**: Animated relationship establishment
- **Pattern Discovery**: Dynamic pattern identification

### Interactive Visualizations (HTML/WebGL)
- **3D Cube Navigation**: Interactive 3D space exploration
- **Multi-Domain Portals**: Cross-domain comparison interfaces
- **Network Exploration**: Clickable nodes and edges
- **Real-time Filtering**: Dynamic data exploration

## Usage Examples

### Basic Static Visualization

```python
from p3if_visualization.network import NetworkVisualizer

visualizer = NetworkVisualizer(framework)
visualizer.visualize_full_network("output/network.png", layout="spring")
```

### Interactive 3D Visualization

```python
from p3if_visualization.interactive_3d import Interactive3DVisualizer

viz = Interactive3DVisualizer(framework_data)
fig = viz.create_3d_scatter_plot("all")
fig.show()  # Opens in browser
```

### Multi-Domain Portal

```python
from p3if_visualization.multi_domain_portal import MultiDomainPortal

portal = MultiDomainPortal()
portal.add_domain("healthcare", healthcare_data)
portal.add_domain("finance", finance_data)
portal.generate_portal_html("output/multi_domain.html")
```

## Animation Features

### Dimension Animation
Animated rotation and pulsing of P3IF dimensions.

```python
from p3if_visualization.animated_dimensions import DimensionAnimator

animator = DimensionAnimator(framework_data)
orbit_anim = animator.create_orbit_animation()
pulse_anim = animator.create_pulse_animation()
```

### Evolution Animation
Shows how frameworks evolve over time.

```python
from p3if_visualization.animation_visualizations import generate_animation_visualizations

generate_animation_visualizations(small_framework, large_framework, session_path)
```

## Portal System

### Multi-Domain Portal
Unified interface for exploring multiple domains simultaneously.

```python
from p3if_visualization.multi_domain_portal import MultiDomainPortal

portal = MultiDomainPortal()
portal.load_domains_from_file("data/domains.json")
dashboard = portal.create_portal_dashboard()
html_file = portal.generate_portal_html("output/portal.html")
```

## Dashboard Generation

### Overview Dashboard
Comprehensive dashboard with multiple visualization types.

```python
from p3if_visualization.dashboard import DashboardGenerator

generator = DashboardGenerator(framework, config)
visualizations = generator.generate_overview_dashboard("output/dashboard")
```

### Domain-Specific Dashboards
Specialized dashboards for individual domains.

```python
domain_dashboard = generator.generate_domain_dashboard("healthcare", "output/healthcare")
```

## Performance Optimization

### Caching
Built-in caching for expensive visualization operations.

```python
from p3if_visualization.interactive import VisualizationConfig

config = VisualizationConfig(cache_enabled=True, cache_ttl=3600)
```

### Progressive Rendering
Efficient rendering for large datasets.

```python
visualizer = InteractiveVisualizer(framework, config)
data = visualizer.generate_3d_cube_data(max_elements=1000)
```

## Configuration Options

### VisualizationConfig
Comprehensive configuration for all visualization types.

```python
config = VisualizationConfig(
    width=1200,
    height=800,
    theme="dark",
    interactive=True,
    animation_duration=1000,
    quality="high"
)
```

## Integration with P3IF Core

### Framework Integration
Seamless integration with core P3IF components.

```python
from p3if_methods.framework import P3IFFramework
from p3if_visualization.interactive import InteractiveVisualizer

framework = P3IFFramework()
# ... populate framework ...

visualizer = InteractiveVisualizer(framework)
html_file = visualizer.generate_3d_cube_html("output/visualization.html")
```

## Output Formats

### Supported Output Types
- **PNG**: High-resolution static images (300 DPI)
- **GIF**: Animated sequences with compression
- **HTML**: Interactive web interfaces
- **SVG**: Scalable vector graphics
- **PDF**: Publication-ready reports

### File Organization
Standardized output structure with session-based organization.

```
output/p3if_output_YYYYMMDD_HHMMSS/
├── visualizations/          # Interactive HTML files
├── images/                  # Static PNG images
├── animations/              # GIF animation files
├── data/                    # JSON data exports
├── reports/                 # Analysis reports
└── session_metadata.json    # Session information
```

## Testing

```bash
# Run visualization tests
python -m pytest p3if_tests/visualization/ -v

# Test specific visualization type
python -m pytest p3if_tests/visualization/test_interactive.py -v
```

## Performance Considerations

### For Large Datasets
- Enable progressive rendering
- Use data sampling for preview
- Implement lazy loading
- Monitor memory usage

### For High-Quality Output
- Increase resolution settings
- Enable anti-aliasing
- Use higher DPI for static images
- Optimize animation frame rates

## Extension Points

### Custom Visualization Types
Add new visualization types by extending base classes.

```python
class CustomVisualizer(Visualizer):
    def generate_custom_visualization(self, data, output_file):
        # Custom visualization logic
        pass
```

### Custom Animation Types
Create specialized animations for domain-specific needs.

```python
def create_custom_animation(framework_data, animation_type):
    # Custom animation implementation
    pass
```

## Dependencies

Core dependencies include:
- `matplotlib>=3.7.0` for static plotting
- `plotly>=5.14.0` for interactive visualizations
- `networkx>=3.0` for graph operations
- `numpy>=1.26.0` for numerical computations
- `pandas>=2.2.2` for data manipulation

## Contributing

When contributing to this package:

1. Follow the established visualization patterns
2. Add comprehensive tests for new visualizations
3. Update documentation for public APIs
4. Ensure performance optimization
5. Follow accessibility guidelines

See the [main contribution guidelines](../CONTRIBUTING.md) for more details.

