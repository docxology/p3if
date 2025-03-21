# Domain-Specific Visualizations in P3IF

This document describes the domain-specific visualization capabilities in the P3IF framework. These visualizations allow users to analyze and explore data relationships within a specific domain or compare data across multiple domains.

## Overview

P3IF provides several specialized visualizations for domain-specific analysis:

1. **Domain Dashboards**: Comprehensive visualizations for a single domain
2. **Comparative Dashboards**: Visualizations comparing multiple domains
3. **Domain Network Visualizations**: Network graphs showing relationships between domains
4. **3D Cube Domain Views**: 3D visualizations filtered by domain
5. **Domain Heatmaps**: Matrix visualizations showing relationship strengths within domains

## Domain Dashboard

The domain dashboard provides a comprehensive view of data for a single domain, including:

- Pattern distribution (Properties, Processes, Perspectives)
- Similarity matrices for patterns within the domain
- Network visualization focused on the domain
- Domain-specific metrics

### Generation

```python
from core.framework import P3IFFramework
from visualization.dashboard import DashboardGenerator
from utils.config import Config

# Initialize framework and load data
framework = P3IFFramework()
# ... load domain data ...

# Create dashboard generator
dashboard = DashboardGenerator(framework, Config())

# Generate domain dashboard
output_dir = "output/domain_dashboard"
visualizations = dashboard.generate_domain_dashboard("ArtificialIntelligence", output_dir)
```

## Comparative Dashboard

The comparative dashboard allows analysis of multiple domains side-by-side, including:

- Comparative pattern distribution
- Domain similarity matrix
- Domain network visualization showing cross-domain connections
- Pattern correlation across domains

### Generation

```python
# Using the dashboard generator from above
domains = ["ArtificialIntelligence", "HealthCare", "Blockchain"]
output_dir = "output/comparative_dashboard"
visualizations = dashboard.generate_comparative_dashboard(domains, output_dir)
```

## Domain Network Visualization

Domain network visualizations show relationships between domains, with:

- Nodes representing domains
- Edges representing cross-domain connections
- Node size indicating domain size (number of patterns)
- Edge width indicating connection strength

### Generation

```python
from visualization.network import NetworkVisualizer

network_viz = NetworkVisualizer(framework, Config())
domain_network_path = "output/domain_network.png"
network_viz.visualize_domain_network(file_path=domain_network_path)
```

## Domain Similarity Analysis

P3IF can generate similarity matrices comparing domains:

- Heatmaps showing similarity scores between domains
- Normalized metrics for fair comparison of domains of different sizes
- Detail views for specific relationships across domains

### Generation

```python
from visualization.matrix import MatrixVisualizer

matrix_viz = MatrixVisualizer(framework, Config())
similarity_path = "output/domain_similarity.png"
matrix_viz.visualize_domain_similarity(file_path=similarity_path)
```

## Integration with the Visualization Portal

All domain visualizations can be accessed through the main visualization portal:

```python
from visualization.portal import VisualizationPortal

portal = VisualizationPortal(framework, Config())
portal.generate_portal(
    output_file="output/index.html", 
    include_dataset_dropdown=True,  # Enable domain selection
    datasets=[
        {"id": "artificial_intelligence", "name": "Artificial Intelligence"},
        {"id": "healthcare", "name": "Healthcare"},
        # ... other domains ...
    ]
)
```

## Running Domain Visualizations from Command Line

The `run_multidomain_portal.py` script in the `scripts` directory provides a convenient way to generate domain visualizations:

```bash
python scripts/run_multidomain_portal.py --domains ArtificialIntelligence,HealthCare --relationships-per-domain 50 --cross-domain-connections 20 --output-dir output/domains
```

This command will:
1. Generate synthetic data for the specified domains
2. Create cross-domain connections
3. Generate all domain-specific visualizations
4. Save outputs to the specified directory

## Testing Domain Visualizations

The P3IF test suite includes comprehensive tests for domain visualizations:

```bash
python tests/visualization/run_all_tests.py --pattern domain
```

This will run all domain-specific visualization tests to ensure everything is working correctly.

## Best Practices

When working with domain visualizations:

1. **Domain Selection**: Be selective about which domains to compare (3-5 is optimal)
2. **Consistent Color Schemes**: Use the same color scheme across visualizations for consistency
3. **Output Organization**: Keep domain visualizations organized by domain name
4. **Interactive Elements**: For web-based visualizations, include interactive filters for domains
5. **Documentation**: Document domain-specific insights from visualizations

## Reference

The following core classes provide domain visualization capabilities:

- `DashboardGenerator`: Creates comprehensive dashboards for domains
- `NetworkVisualizer`: Generates network visualizations including domain networks
- `MatrixVisualizer`: Creates matrix/heatmap visualizations for domain comparison
- `InteractiveVisualizer`: Produces interactive 3D visualizations with domain filtering
- `VisualizationPortal`: Integrates all visualizations with domain selection 