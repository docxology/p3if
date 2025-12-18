# P3IF Analysis Submodule

## Overview

The `p3if_methods/analysis/` submodule provides comprehensive analytical capabilities for P3IF frameworks, enabling pattern recognition, statistical analysis, network analysis, and meta-analysis across domains.

## Module Structure

```
p3if_methods/analysis/
├── __init__.py              # Package initialization and exports
├── basic.py                 # Basic statistical analysis and pattern distribution
├── meta.py                  # Cross-domain meta-analysis and comparisons
├── network.py               # Network graph analysis and centrality measures
└── report.py                # Comprehensive analysis report generation
```

## Core Components

### Basic Analysis (`basic.py`)

The `BasicAnalyzer` provides fundamental statistical analysis of P3IF frameworks:

```python
from p3if_methods.analysis.basic import BasicAnalyzer

analyzer = BasicAnalyzer(framework)

# Get pattern distribution by type
distribution = analyzer.get_pattern_distribution()
# Returns: {"property": 25, "process": 18, "perspective": 22}

# Get relationship strength statistics
stats = analyzer.get_relationship_strength_statistics()
# Returns: {"min": 0.1, "max": 0.95, "mean": 0.67, "median": 0.7, "std": 0.15}

# Find strongest relationships
top_relationships = analyzer.get_strongest_relationships(top_n=5)
```

**Key Features:**
- Pattern distribution analysis by type and domain
- Relationship strength statistics and distributions
- Strongest/weakest relationship identification
- Pattern connectivity analysis
- Confidence score distributions

### Meta-Analysis (`meta.py`)

The `MetaAnalyzer` enables cross-domain analysis and framework comparisons:

```python
from p3if_methods.analysis.meta import MetaAnalyzer

meta_analyzer = MetaAnalyzer(framework)

# Compare domains within framework
domain_comparison = meta_analyzer.get_domain_comparison()
# Returns domain statistics, similarity matrix, and comparison metrics

# Find domain-specific patterns
healthcare_patterns = meta_analyzer.get_patterns_in_domain("healthcare")

# Analyze cross-domain relationships
cross_domain_links = meta_analyzer.analyze_cross_domain_relationships()
```

**Key Features:**
- Domain comparison and similarity analysis
- Cross-domain pattern identification
- Framework integration analysis
- Domain clustering and grouping
- Pattern migration between domains

### Network Analysis (`network.py`)

The `NetworkAnalyzer` provides graph-based analysis using NetworkX:

```python
from p3if_methods.analysis.network import NetworkAnalyzer

network_analyzer = NetworkAnalyzer(framework)

# Build and analyze network graphs
graph_metrics = network_analyzer.run_full_analysis()
# Returns centrality measures, clustering coefficients, connected components

# Get specific network metrics
degree_centrality = network_analyzer.get_degree_centrality()
betweenness = network_analyzer.get_betweenness_centrality()

# Find network communities
communities = network_analyzer.detect_communities()
```

**Key Features:**
- Multiple graph representations (full, bipartite, domain-specific)
- Centrality analysis (degree, betweenness, closeness, eigenvector)
- Community detection and clustering
- Network connectivity and path analysis
- Graph visualization data export

### Analysis Reports (`report.py`)

The `AnalysisReport` provides comprehensive analysis report generation:

```python
from p3if_methods.analysis.report import AnalysisReport

reporter = AnalysisReport(framework)

# Run complete analysis suite
results = reporter.run_analysis(
    include_basic=True,
    include_network=True,
    include_meta=True
)

# Export results
reporter.export_to_json("analysis_report.json")
reporter.export_to_markdown("analysis_report.md")
```

**Key Features:**
- Integrated analysis execution across all analyzers
- Multiple export formats (JSON, Markdown, HTML)
- Analysis result caching and reuse
- Comprehensive reporting with visualizations
- Performance metrics and timing information

## Analysis Types

### Statistical Analysis
- Pattern distribution and frequency analysis
- Relationship strength and confidence distributions
- Domain-specific metrics and comparisons
- Statistical significance testing

### Network Analysis
- Graph topology analysis
- Centrality and influence measures
- Community detection and clustering
- Path analysis and connectivity
- Network robustness and resilience

### Meta-Analysis
- Cross-domain pattern recognition
- Framework comparison and integration
- Domain similarity analysis
- Pattern evolution tracking
- Multi-framework synthesis

## Usage Patterns

### Comprehensive Framework Analysis

```python
from p3if_methods.analysis.report import AnalysisReport

# Initialize with framework
reporter = AnalysisReport(framework)

# Run complete analysis
results = reporter.run_analysis()

# Access different analysis types
basic_stats = results["basic"]
network_metrics = results["network"]
meta_analysis = results["meta"]

# Export comprehensive report
reporter.export_to_markdown("comprehensive_analysis.md")
```

### Targeted Analysis

```python
from p3if_methods.analysis.basic import BasicAnalyzer
from p3if_methods.analysis.network import NetworkAnalyzer

basic = BasicAnalyzer(framework)
network = NetworkAnalyzer(framework)

# Quick pattern overview
distribution = basic.get_pattern_distribution()

# Network health check
centrality = network.get_degree_centrality()

# Export specific visualizations
network.export_network_graph("network_visualization.json")
```

### Cross-Domain Analysis

```python
from p3if_methods.analysis.meta import MetaAnalyzer

meta = MetaAnalyzer(framework)

# Compare healthcare and finance domains
comparison = meta.get_domain_comparison()

# Find patterns that appear in multiple domains
common_patterns = meta.find_common_patterns_across_domains()

# Analyze domain integration potential
integration_score = meta.calculate_domain_integration_score("healthcare", "finance")
```

## Integration with P3IF Core

The analysis modules integrate seamlessly with core P3IF components:

- **Framework Integration**: Direct integration with `P3IFFramework`
- **Domain Management**: Works with `DomainManager` for cross-domain analysis
- **Visualization**: Provides data for visualization modules
- **Performance**: Optimized for large frameworks with caching

## Performance Considerations

- **Caching**: Analysis results cached for reuse
- **Incremental Updates**: Support for incremental analysis updates
- **Memory Management**: Efficient handling of large networks
- **Parallel Processing**: Support for parallel analysis execution

## Testing

Run analysis tests:

```bash
python -m pytest p3if_tests/ -k "test_analysis" -v
```

## Dependencies

Core dependencies:
- `numpy>=1.26.0` for numerical computations
- `pandas>=2.2.2` for data manipulation
- `networkx>=3.0` for graph operations
- `matplotlib>=3.7.0` for visualization support

## Extending Analysis Capabilities

The analysis framework is designed for extension:

1. **Custom Analyzers**: Create new analysis classes following the established pattern
2. **Analysis Plugins**: Add new analysis methods to existing analyzers
3. **Visualization Integration**: Connect analysis results to visualization modules
4. **Export Formats**: Add new export formats for analysis results

## Contributing

When adding new analysis capabilities:

1. Follow the established analyzer patterns
2. Include comprehensive docstrings and type hints
3. Add unit tests covering all analysis methods
4. Update this documentation with new capabilities
5. Consider performance implications for large datasets

The analysis submodule provides the intelligence layer for P3IF, enabling deep insights into framework structures, relationships, and patterns across domains.
