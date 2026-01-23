# P3IF Package

The main P3IF (Properties, Processes, Perspectives Inter-Framework) package.

## Package Structure

```
p3if/
├── __init__.py          # Package exports
├── core/                # Core framework and models
│   ├── framework.py     # P3IFFramework class
│   ├── models.py        # Property, Process, Perspective, Relationship
│   ├── orchestration.py # ThinOrchestrator, workflow engine
│   ├── composition.py   # Framework composition and integration
│   ├── validation.py    # Validation framework
│   └── analysis/        # Analysis tools
├── orchestrators/       # Domain-specific orchestrators
│   ├── cognitive_security.py
│   ├── framework_integration.py
│   └── healthcare_domain.py
├── visualization/       # Visualization system
│   ├── static/          # PNG/SVG generation
│   ├── interactive/     # 3D HTML visualizations
│   ├── animated/        # GIF animations
│   └── portals/         # Web dashboards
├── data/                # Data management
│   ├── domains.py       # Domain data handling
│   ├── synthetic.py     # Synthetic data generation
│   ├── importers.py     # Data import utilities
│   └── exporters.py     # Data export utilities
└── utils/               # Shared utilities
    ├── config.py        # Configuration management
    ├── storage.py       # Data persistence
    ├── performance.py   # Performance monitoring
    └── logging.py       # Logging utilities
```

## Usage

```python
from p3if import P3IFFramework, Property, Process, Perspective
from p3if.orchestrators import CognitiveSecurityOrchestrator
from p3if.visualization import InteractiveVisualizer

# Create framework
framework = P3IFFramework()

# Add patterns
framework.add_pattern(Property(name="Security", domain="cyber"))
framework.add_pattern(Process(name="Authentication", domain="cyber"))

# Use orchestrators
orchestrator = CognitiveSecurityOrchestrator()
results = orchestrator.execute_analysis()

# Generate visualizations
viz = InteractiveVisualizer(framework)
viz.generate_3d_cube_html("output.html")
```

## Testing

```bash
pytest tests/ -v
```
