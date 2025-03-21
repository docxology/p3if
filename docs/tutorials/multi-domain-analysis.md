# Multi-Domain Analysis with P3IF

This tutorial provides a comprehensive guide to performing multi-domain analysis using the P3IF framework. You'll learn how to identify and analyze patterns across different domains, discover cross-domain connections, and generate insights from complex data relationships.

## Prerequisites

Before starting this tutorial, ensure you have:

1. Installed P3IF and its dependencies (see [Installation Guide](../guides/installation.md))
2. Generated or imported data for at least two domains
3. Familiarity with basic P3IF concepts (see [Getting Started](../guides/getting-started.md))

## Understanding Multi-Domain Analysis

Multi-domain analysis in P3IF allows you to:

1. **Identify cross-domain relationships**: Discover how entities in different domains relate to each other
2. **Compare domain structures**: Analyze similarities and differences between domain patterns
3. **Find emergent patterns**: Detect patterns that only become visible when examining multiple domains together
4. **Translate concepts**: Map concepts from one domain to equivalent concepts in another

## Step 1: Prepare Your Data

First, let's generate data for multiple domains:

```bash
python scripts/run_multidomain_portal.py --domains cybersecurity,healthcare,finance --relationships 100 --cross-domain 50 --output-dir output
```

This command:
- Generates data for three domains: cybersecurity, healthcare, and finance
- Creates 100 relationships within each domain
- Establishes 50 cross-domain connections
- Outputs the results to the `output` directory

## Step 2: Explore Cross-Domain Connections

Open the generated portal at `output/index.html` and follow these steps:

1. **Select "All Domains"** from the domain dropdown
2. **Switch to the Network View** to visualize cross-domain connections
3. **Enable entity labels** to identify nodes by name
4. **Use the filter panel** to highlight cross-domain connections:
   - Set "Connection Type" to "Cross-Domain"
   - Adjust the "Strength" slider to focus on stronger connections

The network visualization will show you how entities from different domains connect to each other. Nodes are color-coded by domain, and edges represent relationships between entities.

## Step 3: Analyze Domain Similarities

To analyze similarities between domains:

1. **Switch to the Matrix View**
2. **Select "Domain Comparison"** from the view options
3. **Examine the heatmap** showing the density of connections between domains
4. **Click on a cell** to explore specific cross-domain connections

The matrix provides a quantitative view of how domains relate to each other. Darker cells indicate more connections between the corresponding domains.

## Step 4: Identify Common Patterns

To identify patterns that appear across multiple domains:

```python
# Python code example for analyzing common patterns
from p3if.core.framework import P3IFFramework
from p3if.analysis.patterns import PatternAnalyzer

# Load the framework data
framework = P3IFFramework()
framework.load_data("output/data/framework_data.json")

# Create a pattern analyzer
analyzer = PatternAnalyzer(framework)

# Find common patterns across domains
common_patterns = analyzer.find_common_patterns(
    domains=["cybersecurity", "healthcare", "finance"],
    min_occurrence=2,  # Pattern must appear in at least 2 domains
    min_size=3  # Pattern must involve at least 3 entities
)

# Print the common patterns
for pattern in common_patterns:
    print(f"Pattern: {pattern.name}")
    print(f"Occurs in domains: {pattern.domains}")
    print(f"Entities involved: {pattern.entities}")
    print(f"Confidence score: {pattern.confidence}")
    print("---")
```

This code analyzes the framework data to find patterns that appear in multiple domains, helping you identify common structures and relationships.

## Step 5: Visualize Cross-Domain Insights

To create a visualization focused on cross-domain insights:

1. **Switch to the Dashboard View**
2. **Select "Cross-Domain Analysis"** from the dashboard options
3. **Explore the various widgets**:
   - Cross-Domain Connection Map
   - Domain Similarity Matrix
   - Common Pattern Frequency Chart
   - Entity Translation Table

The dashboard provides a comprehensive view of cross-domain relationships and patterns, making it easier to identify insights across domains.

## Step 6: Perform Advanced Analysis

For more advanced analysis, you can use the P3IF API to perform custom queries:

```python
# Python code example for advanced cross-domain analysis
from p3if.core.framework import P3IFFramework
from p3if.analysis.cross_domain import CrossDomainAnalyzer
from p3if.visualization.heatmap import HeatmapGenerator

# Load the framework data
framework = P3IFFramework()
framework.load_data("output/data/framework_data.json")

# Create a cross-domain analyzer
analyzer = CrossDomainAnalyzer(framework)

# Calculate domain similarity matrix
similarity_matrix = analyzer.calculate_domain_similarity(
    domains=["cybersecurity", "healthcare", "finance"],
    method="jaccard",  # Use Jaccard similarity coefficient
    entity_types=["property", "process", "perspective"]
)

# Generate a heatmap visualization
heatmap = HeatmapGenerator()
heatmap.generate(
    data=similarity_matrix,
    title="Domain Similarity Heatmap",
    output_file="output/visualizations/domain_similarity.html"
)

# Find potential domain translations
translations = analyzer.find_concept_translations(
    source_domain="cybersecurity",
    target_domain="healthcare",
    min_confidence=0.7
)

# Print the translations
for translation in translations:
    print(f"Cybersecurity: {translation.source_entity.name}")
    print(f"Healthcare equivalent: {translation.target_entity.name}")
    print(f"Confidence: {translation.confidence}")
    print("---")
```

This code performs advanced cross-domain analysis, including calculating domain similarities and finding concept translations between domains.

## Step 7: Export and Share Results

To export your analysis results:

1. **Click the "Export" button** in the portal
2. **Select the export format** (JSON, CSV, or PDF)
3. **Choose what to include** in the export:
   - Cross-domain connections
   - Common patterns
   - Domain similarities
   - Concept translations
4. **Click "Export"** to download the file

You can then share the exported file with colleagues or import it into other analysis tools.

## Advanced Topics

### Custom Domain Mapping

Create custom mappings between domains to enhance cross-domain analysis:

```python
# Python code example for custom domain mapping
from p3if.core.framework import P3IFFramework
from p3if.analysis.mapping import DomainMapper

# Load the framework data
framework = P3IFFramework()
framework.load_data("output/data/framework_data.json")

# Create a domain mapper
mapper = DomainMapper(framework)

# Define custom entity mappings
custom_mappings = [
    {
        "source_domain": "cybersecurity",
        "source_entity": "data_breach",
        "target_domain": "healthcare",
        "target_entity": "patient_data_exposure",
        "confidence": 0.9
    },
    {
        "source_domain": "cybersecurity",
        "source_entity": "encryption",
        "target_domain": "finance",
        "target_entity": "data_protection",
        "confidence": 0.85
    }
]

# Apply custom mappings
mapper.apply_custom_mappings(custom_mappings)

# Save the updated framework
framework.save_data("output/data/framework_data_mapped.json")
```

This code allows you to define custom mappings between entities in different domains, enhancing the cross-domain analysis capabilities.

### Temporal Analysis

Analyze how cross-domain relationships evolve over time:

```python
# Python code example for temporal cross-domain analysis
from p3if.core.framework import P3IFFramework
from p3if.analysis.temporal import TemporalAnalyzer
import datetime

# Load multiple framework snapshots
snapshots = {
    "2022-01": P3IFFramework().load_data("output/data/framework_2022_01.json"),
    "2022-06": P3IFFramework().load_data("output/data/framework_2022_06.json"),
    "2023-01": P3IFFramework().load_data("output/data/framework_2023_01.json")
}

# Create a temporal analyzer
analyzer = TemporalAnalyzer(snapshots)

# Analyze cross-domain relationship evolution
evolution = analyzer.analyze_relationship_evolution(
    domains=["cybersecurity", "healthcare"],
    start_date=datetime.date(2022, 1, 1),
    end_date=datetime.date(2023, 1, 1)
)

# Print the evolution results
for period, metrics in evolution.items():
    print(f"Period: {period}")
    print(f"Number of cross-domain relationships: {metrics['relationship_count']}")
    print(f"Average relationship strength: {metrics['avg_strength']}")
    print(f"New relationships: {metrics['new_relationships']}")
    print(f"Removed relationships: {metrics['removed_relationships']}")
    print("---")
```

This code analyzes how cross-domain relationships evolve over time, allowing you to identify trends and changes in the relationships between domains.

## Conclusion

In this tutorial, you've learned how to perform multi-domain analysis with P3IF, including:

1. Preparing data for multiple domains
2. Exploring cross-domain connections
3. Analyzing domain similarities
4. Identifying common patterns
5. Visualizing cross-domain insights
6. Performing advanced analysis
7. Exporting and sharing results

Multi-domain analysis is a powerful capability of P3IF that helps you discover insights that would be impossible to see when examining domains in isolation. By connecting and comparing different domains, you can identify common patterns, translate concepts, and gain a deeper understanding of complex systems.

## Next Steps

- [Advanced Visualization Techniques](advanced-visualizations.md)
- [Extending P3IF with Custom Domains](extending-p3if.md)
- [Integrating External Data Sources](data-integration.md) 