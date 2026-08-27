# P3IF Visualization System

Advanced visualization and animation system for the P3IF framework, providing multiple approaches to represent complex framework relationships.

## Visualization Types

### Static Visualizations
Generate fixed visualizations for reports and documentation:

- **Heatmaps**: Intensity-based relationship visualization
- **Networks**: Graph-based relationship mapping
- **Matrices**: Tabular data representation
- **Hierarchies**: Tree and structure visualization
- **Grids, Lists, Statistics**: Layout and summary generators

### Interactive Visualizations
Dynamic, user-explorable visualizations:

- **3D Interactive Cube**: Dynamic framework exploration
- **Interactive Controls**: Real-time parameter adjustment
- **Drill-down Capabilities**: Detailed relationship exploration

### Animated Visualizations
Time-based visualizations showing framework evolution:

- **Dimension Transitions**: Smooth dimension changes
- **Sequence Animations**: Step-by-step process visualization
- **Timeline Controls**: Animation playback and scrubbing

### Portal System
Comprehensive web-based visualization platforms:

- **Multi-domain Portal**: Cross-framework analysis
- **Dashboard Portal**: Executive overview displays
- **Orchestrator Portal**: Workflow visualization

## Quick Start

```python
from p3if import P3IFFramework
from p3if.visualization.static import GridVisualizer
from p3if.visualization.interactive import InteractiveVisualizer

# Create framework
framework = P3IFFramework()

# Interactive visualization
interactive_viz = InteractiveVisualizer(framework)
interactive_viz.generate_3d_cube_html("cube.html")

# Unified interactive dashboard (Overview / 3D Cube / Network / Analytics)
interactive_viz.generate_modern_dashboard("dashboard.html")

# Static visualization
static_viz = GridVisualizer(framework)
```

## Configuration

Visualizers take the framework as the first argument and an optional
`p3if.utils.config.Config` instance:

```python
from p3if import P3IFFramework
from p3if.utils.config import Config
from p3if.visualization.interactive import InteractiveVisualizer

config = Config()
config.set("visualization.theme", "professional")

framework = P3IFFramework()
visualizer = InteractiveVisualizer(framework, config=config)
```

## Output Formats

- **HTML**: Web-ready interactive visualizations
- **PNG/SVG**: Publication-quality static images
- **JSON**: Raw data for custom visualization tools
- **GIF/MP4**: Animated sequences for presentations

## Architecture

```
visualization/
├── base.py              # Base classes and configuration
├── static/              # Static visualization generators
│   ├── cube_visualizations.py
│   ├── heatmap_visualizations.py
│   ├── network_visualizations.py
│   └── ...
├── interactive/         # Interactive visualization system
│   ├── interactive_3d.py
│   └── interactive.py
├── animated/            # Animation and sequence generation
│   ├── animated_dimensions.py
│   └── animation_visualizations.py
└── portals/             # Web portal system
    ├── dashboard.py
    ├── multi_domain_portal.py
    └── orchestrator.py
```

## Dependencies

- plotly: Interactive visualizations
- matplotlib: Static plotting
- networkx: Graph visualization
- pandas: Data manipulation

## Testing

```bash
# Run all visualization tests
python -m pytest tests/visualization/

# Test specific visualization type
python -m pytest tests/visualization/test_base.py
```





