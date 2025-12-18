# P3IF Visualization System

Advanced visualization and animation system for the P3IF framework, providing multiple approaches to represent complex framework relationships.

## Visualization Types

### Static Visualizations
Generate fixed visualizations for reports and documentation:

- **3D Cube**: Three-dimensional framework representation
- **Heatmaps**: Intensity-based relationship visualization
- **Networks**: Graph-based relationship mapping
- **Matrices**: Tabular data representation
- **Hierarchies**: Tree and structure visualization

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
from p3if.visualization.static import CubeVisualizer
from p3if.visualization.interactive import Interactive3DVisualizer

# Create framework
framework = create_sample_framework()

# Static visualization
static_viz = CubeVisualizer()
static_viz.generate_cube_html(framework, "cube.html")

# Interactive visualization
interactive_viz = Interactive3DVisualizer()
interactive_viz.create_interactive_cube(framework, "interactive.html")
```

## Configuration

```python
from p3if.visualization.base import VisualizationConfig

config = VisualizationConfig(
    width=1200,
    height=800,
    theme="professional",
    output_format="html",
    show_labels=True,
    interactive=True
)

visualizer = CubeVisualizer(config=config)
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





