"""
P3IF Dashboard Generator

This module provides dashboard generation capabilities for P3IF data.
"""
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
from pathlib import Path
import os
import numpy as np
import networkx as nx
import datetime

from p3if.core.framework import P3IFFramework
from p3if.visualization.base import Visualizer
from p3if.visualization.network import NetworkVisualizer
from p3if.visualization.matrix import MatrixVisualizer
from p3if.utils.config import Config
from p3if.analysis.report import AnalysisReport


class DashboardGenerator(Visualizer):
    """Dashboard generator for P3IF data."""
    
    def __init__(self, framework: P3IFFramework, config: Optional[Config] = None):
        """
        Initialize dashboard generator.
        
        Args:
            framework: P3IF framework instance
            config: Optional configuration
        """
        super().__init__(framework, config)
        self.network_visualizer = NetworkVisualizer(framework, config)
        self.matrix_visualizer = MatrixVisualizer(framework, config)
        self.analysis_report = AnalysisReport(framework)
    
    def generate_overview_dashboard(self, output_dir: Union[str, Path]) -> Dict[str, Path]:
        """
        Generate an overview dashboard with key visualizations.
        
        Args:
            output_dir: Output directory for dashboard files
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        output_path = Path(output_dir)
        os.makedirs(output_path, exist_ok=True)
        
        self.logger.info("Generating overview dashboard...")
        
        # Create a collection of visualizations
        visualizations = {}
        
        # Generate network visualization
        network_path = output_path / "network_overview.png"
        fig = self.network_visualizer.visualize_full_network(
            file_path=network_path, 
            color_by="type"
        )
        visualizations["network_overview"] = network_path
        
        # Generate domain network visualization
        domain_network_path = output_path / "domain_network.png"
        fig = self.network_visualizer.visualize_domain_network(
            file_path=domain_network_path
        )
        visualizations["domain_network"] = domain_network_path
        
        # Generate relationship matrix visualizations
        for pair in [("property", "process"), ("property", "perspective"), ("process", "perspective")]:
            matrix_path = output_path / f"matrix_{pair[0]}_{pair[1]}.png"
            fig = self.matrix_visualizer.visualize_relationship_matrix(
                file_path=matrix_path,
                pattern_type_x=pair[0],
                pattern_type_y=pair[1]
            )
            visualizations[f"matrix_{pair[0]}_{pair[1]}"] = matrix_path
        
        # Generate domain similarity visualization
        domain_sim_path = output_path / "domain_similarity.png"
        fig = self.matrix_visualizer.visualize_domain_similarity(
            file_path=domain_sim_path
        )
        visualizations["domain_similarity"] = domain_sim_path
        
        # Generate a summary report
        summary_path = output_path / "summary_report.json"
        self.analysis_report.run_analysis()
        self.analysis_report.export_to_json(summary_path)
        visualizations["summary_report"] = summary_path
        
        self.logger.info(f"Overview dashboard generated at {output_path}")
        return visualizations
    
    def generate_domain_dashboard(self, domain: str, output_dir: Union[str, Path]) -> Dict[str, Path]:
        """
        Generate a dashboard focused on a specific domain.
        
        Args:
            domain: Domain name
            output_dir: Output directory for dashboard files
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        output_path = Path(output_dir)
        os.makedirs(output_path, exist_ok=True)
        
        self.logger.info(f"Generating dashboard for domain '{domain}'...")
        
        # Check if domain exists
        domains = set()
        for pattern in self.framework._patterns.values():
            pattern_domain = getattr(pattern, "domain", None)
            if pattern_domain:
                domains.add(pattern_domain)
        
        if domain not in domains:
            self.logger.warning(f"Domain '{domain}' not found")
            return {}
        
        # Create a collection of visualizations
        visualizations = {}
        
        # Create a summary visualization of pattern counts
        fig, ax = self.setup_figure()
        
        # Count patterns by type for this domain
        pattern_counts = {"property": 0, "process": 0, "perspective": 0}
        for pattern in self.framework._patterns.values():
            pattern_domain = getattr(pattern, "domain", None)
            if pattern_domain == domain and pattern.type in pattern_counts:
                pattern_counts[pattern.type] += 1
        
        # Create a bar chart
        sns.barplot(
            x=list(pattern_counts.keys()),
            y=list(pattern_counts.values()),
            hue=list(pattern_counts.keys()),
            palette=self.get_pattern_type_colors().values(),
            legend=False,
            ax=ax
        )
        
        ax.set_title(f"Pattern Distribution for Domain: {domain}")
        ax.set_xlabel("Pattern Type")
        ax.set_ylabel("Count")
        
        pattern_dist_path = output_path / "pattern_distribution.png"
        self.save_figure(fig, pattern_dist_path)
        visualizations["pattern_distribution"] = pattern_dist_path
        
        # Generate similarity matrices for this domain's patterns
        for pattern_type in ["property", "process", "perspective"]:
            sim_matrix_path = output_path / f"{pattern_type}_similarity.png"
            
            # Filter patterns to this domain
            domain_patterns = []
            for pattern in self.framework.get_patterns_by_type(pattern_type):
                if getattr(pattern, "domain", None) == domain:
                    domain_patterns.append(pattern)
            
            if domain_patterns:
                # Create a custom similarity matrix for these patterns
                n = len(domain_patterns)
                similarity_matrix = np.zeros((n, n))
                
                # Create a mapping from pattern ID to index
                pattern_map = {p.id: i for i, p in enumerate(domain_patterns)}
                
                # Calculate similarity based on shared relationships
                for rel in self.framework._relationships.values():
                    rel_pattern_id = getattr(rel, f"{pattern_type}_id", None)
                    if rel_pattern_id in pattern_map:
                        pattern_idx = pattern_map[rel_pattern_id]
                        similarity_matrix[pattern_idx, pattern_idx] += 1
                        
                        # Find other patterns in this relationship
                        for other_type in ["property", "process", "perspective"]:
                            other_id = getattr(rel, f"{other_type}_id", None)
                            if other_id:
                                # Check if this other pattern is also of the same type and domain
                                other_pattern = self.framework.get_pattern(other_id)
                                if (other_pattern and other_pattern.type == pattern_type and
                                    getattr(other_pattern, "domain", None) == domain and
                                    other_id != rel_pattern_id and other_id in pattern_map):
                                    other_idx = pattern_map[other_id]
                                    similarity_matrix[pattern_idx, other_idx] += 1
                                    similarity_matrix[other_idx, pattern_idx] += 1
                
                # Normalize similarity matrix
                row_sums = similarity_matrix.sum(axis=1)
                # Only divide by row_sums where it's not zero to avoid warnings
                mask = row_sums != 0
                similarity_matrix_normalized = np.zeros_like(similarity_matrix, dtype=float)
                if mask.any():  # Only perform division if there are non-zero elements
                    similarity_matrix_normalized[mask] = similarity_matrix[mask] / row_sums[mask, np.newaxis]
                similarity_matrix = np.nan_to_num(similarity_matrix_normalized)
                
                # Create figure
                fig_size = max(8, n * 0.3)
                fig, ax = plt.subplots(figsize=(fig_size, fig_size))
                
                # Get pattern names
                pattern_names = [p.name for p in domain_patterns]
                
                # Create heatmap
                sns.heatmap(similarity_matrix, annot=True, cmap="viridis", ax=ax, 
                           xticklabels=pattern_names, yticklabels=pattern_names,
                           cbar_kws={'label': 'Similarity'})
                
                ax.set_title(f"{pattern_type.capitalize()} Similarity in Domain: {domain}")
                
                plt.xticks(rotation=45, ha='right')
                plt.yticks(rotation=0)
                
                self.save_figure(fig, sim_matrix_path, tight_layout=False)
                visualizations[f"{pattern_type}_similarity"] = sim_matrix_path
        
        # Create a network visualization focused on this domain
        G = self.network_visualizer.network_analyzer.get_graph("full")
        
        # Filter to only nodes in this domain
        domain_nodes = []
        for node in G.nodes:
            node_data = G.nodes[node]
            if node_data.get("domain") == domain:
                domain_nodes.append(node)
        
        if domain_nodes:
            domain_subgraph = G.subgraph(domain_nodes)
            
            # Create figure
            fig, ax = self.setup_figure()
            
            # Get node positions
            pos = nx.spring_layout(domain_subgraph, seed=42)
            
            # Get node colors by type
            type_colors = self.get_pattern_type_colors()
            node_colors = [type_colors.get(domain_subgraph.nodes[n].get("type", "unknown"), "#cccccc") for n in domain_subgraph.nodes]
            
            # Draw the network
            nx.draw_networkx_edges(domain_subgraph, pos, alpha=0.7, edge_color="#999999")
            nx.draw_networkx_nodes(domain_subgraph, pos, node_color=node_colors, node_size=self.node_size)
            
            # Create shorter labels
            labels = {}
            for node in domain_subgraph.nodes:
                node_data = domain_subgraph.nodes[node]
                name = node_data.get('name', str(node))
                if len(name) > 20:
                    name = name[:17] + "..."
                labels[node] = name
            
            nx.draw_networkx_labels(domain_subgraph, pos, labels=labels, font_size=8)
            
            # Add legend
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, 
                           label=pattern_type.capitalize(), markersize=10)
                for pattern_type, color in type_colors.items()
            ]
            ax.legend(handles=legend_elements, loc='upper right')
            
            ax.set_title(f"Network Visualization for Domain: {domain}")
            ax.axis('off')
            
            domain_network_path = output_path / "domain_network.png"
            self.save_figure(fig, domain_network_path)
            visualizations["domain_network"] = domain_network_path
        
        self.logger.info(f"Domain dashboard generated at {output_path}")
        return visualizations
    
    def generate_comparative_dashboard(self, domains: List[str], output_dir: Union[str, Path]) -> Dict[str, Path]:
        """
        Generate a dashboard comparing multiple domains.
        
        Args:
            domains: List of domain names to compare
            output_dir: Output directory for dashboard files
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        output_path = Path(output_dir)
        os.makedirs(output_path, exist_ok=True)
        
        self.logger.info(f"Generating comparative dashboard for domains: {domains}")
        
        # Create a collection of visualizations
        visualizations = {}
        
        # Generate domain metrics visualization
        domain_metrics_path = output_path / "domain_metrics.png"
        fig = self.matrix_visualizer.visualize_domain_metrics(
            file_path=domain_metrics_path,
            normalize=True
        )
        visualizations["domain_metrics"] = domain_metrics_path
        
        # Generate domain similarity matrix
        domain_similarity_path = output_path / "domain_similarity.png"
        fig = self.matrix_visualizer.visualize_domain_similarity(
            file_path=domain_similarity_path
        )
        visualizations["domain_similarity"] = domain_similarity_path
        
        # Generate domain network
        domain_network_path = output_path / "domain_network.png"
        fig = self.network_visualizer.visualize_domain_network(
            file_path=domain_network_path
        )
        visualizations["domain_network"] = domain_network_path
        
        # Generate pattern correlation matrix
        correlation_path = output_path / "pattern_correlation.png"
        fig = self.matrix_visualizer.visualize_pattern_correlation(
            file_path=correlation_path
        )
        visualizations["pattern_correlation"] = correlation_path
        
        # Generate comparison of pattern distributions across domains
        fig, ax = self.setup_figure()
        
        # Count patterns by type and domain
        pattern_counts = {}
        for domain in domains:
            pattern_counts[domain] = {"property": 0, "process": 0, "perspective": 0}
        
        for pattern in self.framework._patterns.values():
            pattern_domain = getattr(pattern, "domain", None)
            if pattern_domain in pattern_counts and pattern.type in pattern_counts[pattern_domain]:
                pattern_counts[pattern_domain][pattern.type] += 1
        
        # Prepare data for plotting
        data = []
        for domain, counts in pattern_counts.items():
            for pattern_type, count in counts.items():
                data.append({
                    "Domain": domain,
                    "Pattern Type": pattern_type.capitalize(),
                    "Count": count
                })
        
        # Create DataFrame
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Create grouped bar chart
        sns.barplot(
            data=df,
            x="Domain",
            y="Count",
            hue="Pattern Type",
            palette=self.get_pattern_type_colors().values(),
            ax=ax
        )
        
        ax.set_title("Pattern Distribution Across Domains")
        ax.set_xlabel("Domain")
        ax.set_ylabel("Count")
        
        # Rotate x-axis labels if many domains
        if len(domains) > 3:
            plt.xticks(rotation=45, ha='right')
        
        pattern_dist_path = output_path / "comparative_pattern_distribution.png"
        self.save_figure(fig, pattern_dist_path)
        visualizations["comparative_pattern_distribution"] = pattern_dist_path
        
        self.logger.info(f"Comparative dashboard generated at {output_path}")
        return visualizations
    
    def generate_html_report(self, visualizations: Dict[str, Path], output_file: Union[str, Path]) -> None:
        """
        Generate an HTML report from dashboard visualizations.
        
        Args:
            visualizations: Dictionary mapping visualization names to file paths
            output_file: Output HTML file path
        """
        output_path = Path(output_file)
        os.makedirs(output_path.parent, exist_ok=True)
        
        self.logger.info(f"Generating HTML report at {output_path}")
        
        # Create a simple HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>P3IF Analysis Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                h1, h2, h3 {{
                    color: #333;
                }}
                .visualization {{
                    margin-bottom: 30px;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 10px;
                    border-top: 1px solid #ddd;
                    color: #777;
                    font-size: 0.8em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>P3IF Analysis Report</h1>
                <p>Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <div class="visualization-container">
        """
        
        # Add visualizations to the report
        for name, path in visualizations.items():
            if path.exists():
                # Make the path relative to the HTML file
                rel_path = os.path.relpath(path, output_path.parent)
                
                # Create a nicer title
                title = " ".join(word.capitalize() for word in name.replace('_', ' ').split())
                
                html_content += f"""
                    <div class="visualization">
                        <h2>{title}</h2>
                        <img src="{rel_path}" alt="{name}">
                    </div>
                """
        
        # Close the HTML
        html_content += """
                </div>
                
                <div class="footer">
                    <p>Generated using P3IF Framework</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Write the HTML file
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML report generated at {output_path}")

    def generate_interactive_filters(self, filters: List[Dict[str, Any]]) -> str:
        """
        Generate HTML for interactive filters.
        
        Args:
            filters: List of filter configurations, each with id, name, and options
            
        Returns:
            HTML string for the filters
        """
        html = '<div class="filter-container">\n'
        
        for filter_config in filters:
            filter_id = filter_config.get("id", "")
            filter_name = filter_config.get("name", "")
            filter_options = filter_config.get("options", [])
            
            html += f'  <div class="filter" id="{filter_id}-filter">\n'
            html += f'    <label for="{filter_id}">{filter_name}:</label>\n'
            html += f'    <select id="{filter_id}" name="{filter_id}" class="filter-select">\n'
            html += f'      <option value="">All</option>\n'
            
            for option in filter_options:
                html += f'      <option value="{option}">{option}</option>\n'
            
            html += '    </select>\n'
            html += '  </div>\n'
        
        html += '</div>\n'
        return html

    def generate_full_dashboard(self, 
                           output_file: str, 
                           title: str = "Full Dashboard with Dataset Selector", 
                           datasets: List[Dict[str, str]] = None) -> Path:
        """
        Generate a complete dashboard with multiple components and an optional dataset selector.
        
        Args:
            output_file: Path to save the dashboard HTML
            title: Dashboard title
            datasets: List of dataset options (each with id and name)
            
        Returns:
            Path to the generated dashboard HTML file
        """
        # Create output directory if it doesn't exist
        output_path = Path(output_file)
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create visualizations directory for assets
        viz_dir = output_dir / "visualizations"
        viz_dir.mkdir(exist_ok=True)
        
        # Create overview directory for visualization images
        overview_dir = viz_dir / "overview"
        overview_dir.mkdir(exist_ok=True)
        
        # Create assets directory
        assets_dir = output_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        assets_js_dir = assets_dir / "js"
        assets_js_dir.mkdir(exist_ok=True)
        
        # Create test datasets if none provided
        if not datasets:
            datasets = [
                {"id": "dataset1", "name": "Test Dataset 1"},
                {"id": "dataset2", "name": "Test Dataset 2"},
                {"id": "dataset3", "name": "Test Dataset 3"}
            ]
        
        # Generate HTML
        dataset_selector_html = ""
        if datasets:
            dataset_selector_html = """
                <div id="dataset-selector">
                    <label for="dataset-select">Select Dataset:</label>
                    <select id="dataset-select" onchange="changeDataset(this.value)">
            """
            
            for dataset in datasets:
                dataset_selector_html += f'<option value="{dataset["id"]}">{dataset["name"]}</option>\n'
            
            dataset_selector_html += """
                    </select>
                </div>
            """
        
        # Generate HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .dashboard-container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                .section {{
                    margin-bottom: 30px;
                }}
                .viz-panel {{
                    margin-bottom: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                h1, h2, h3 {{
                    color: #333;
                }}
                #dataset-selector {{
                    margin-bottom: 20px;
                    padding: 10px;
                    background-color: #f0f0f0;
                    border-radius: 5px;
                }}
                .dashboard-controls {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }}
                .overview-section {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .filter-section {{
                    background-color: #f8f8f8;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .filter-group {{
                    margin-bottom: 10px;
                }}
                
                /* Responsive design */
                @media (max-width: 1200px) {{
                    .dashboard-container {{
                        max-width: 95%;
                    }}
                }}
                
                @media (max-width: 992px) {{
                    .overview-section {{
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    }}
                }}
                
                @media (max-width: 768px) {{
                    .dashboard-controls {{
                        flex-direction: column;
                        align-items: flex-start;
                    }}
                    
                    .overview-section {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .filter-section {{
                        display: flex;
                        flex-direction: column;
                    }}
                }}
                
                @media (max-width: 576px) {{
                    body {{
                        padding: 10px;
                    }}
                    
                    .dashboard-container {{
                        padding: 10px;
                    }}
                    
                    .viz-panel {{
                        padding: 10px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="dashboard-container">
                <h1>{title}</h1>
        
                {dataset_selector_html}
            
                <div class="filter-section" id="filter-section">
                    <h3>Filters</h3>
                    <div class="row">
                        <div class="filter-group">
                            <label for="filter-domain">Domain:</label>
                            <select id="filter-domain" onclick="updateFilters('domain', this.value)">
                                <option value="all">All Domains</option>
                                <option value="domain1">Domain 1</option>
                                <option value="domain2">Domain 2</option>
                                <option value="domain3">Domain 3</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label for="filter-property">Property:</label>
                            <select id="filter-property" onclick="updateFilters('property', this.value)">
                                <option value="all">All Properties</option>
                                <option value="property1">Property 1</option>
                                <option value="property2">Property 2</option>
                                <option value="property3">Property 3</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label for="filter-process">Process:</label>
                            <select id="filter-process" onclick="updateFilters('process', this.value)">
                                <option value="all">All Processes</option>
                                <option value="process1">Process 1</option>
                                <option value="process2">Process 2</option>
                                <option value="process3">Process 3</option>
                            </select>
                        </div>
                    </div>
                </div>
        
                <div class="section" id="overview-section">
                    <h2>Framework Overview</h2>
                    <div class="overview-section">
        
                        <div class="viz-panel" onclick="showDetailedView('network_overview')">
                            <h3>Network Overview</h3>
                            <img src="visualizations/overview/network_overview.png" alt="network_overview">
                        </div>
            
                        <div class="viz-panel" onclick="showDetailedView('domain_network')">
                            <h3>Domain Network</h3>
                            <img src="visualizations/overview/domain_network.png" alt="domain_network">
                        </div>
            
                        <div class="viz-panel" onclick="showDetailedView('matrix_property_process')">
                            <h3>Matrix Property Process</h3>
                            <img src="visualizations/overview/matrix_property_process.png" alt="matrix_property_process">
                        </div>
            
                        <div class="viz-panel" onclick="showDetailedView('matrix_property_perspective')">
                            <h3>Matrix Property Perspective</h3>
                            <img src="visualizations/overview/matrix_property_perspective.png" alt="matrix_property_perspective">
                        </div>
            
                        <div class="viz-panel" onclick="showDetailedView('matrix_process_perspective')">
                            <h3>Matrix Process Perspective</h3>
                            <img src="visualizations/overview/matrix_process_perspective.png" alt="matrix_process_perspective">
                        </div>
            
                        <div class="viz-panel" onclick="showDetailedView('domain_similarity')">
                            <h3>Domain Similarity</h3>
                            <img src="visualizations/overview/domain_similarity.png" alt="domain_similarity">
                        </div>
            
                    </div>
                </div>
        
                <div class="section" id="details-section">
                    <h2>Detailed Metrics</h2>
                    <div id="details-chart" class="chart-container">
                        <!-- Populated by JavaScript -->
                    </div>
                </div>
                
                <div class="section" id="metrics-section">
                    <h2>Key Metrics</h2>
                    <div id="metrics-chart" class="chart-container">
                        <!-- Populated by JavaScript -->
                    </div>
                </div>
            </div>
        
            <script>
                function changeDataset(datasetId) {{
                    console.log("Dataset changed to: " + datasetId);
                    // In a real implementation, this would load data for the selected dataset
                    // For now, just log the change
                }}
                
                function updateFilters(filterType, value) {{
                    console.log("Filter updated: " + filterType + " = " + value);
                    // This would update the visualizations based on filter selection
                }}
                
                function showDetailedView(vizId) {{
                    console.log("Showing detailed view for: " + vizId);
                    // This would show a detailed view of the visualization
                }}
                
                // Initialize on load
                document.addEventListener('DOMContentLoaded', function() {{
                    // Additional initialization code would go here
                    console.log("Dashboard initialized");
                    
                    // Add click handlers to visualization panels
                    document.querySelectorAll('.viz-panel').forEach(panel => {{
                        panel.onclick = function() {{
                            console.log('Clicked on panel: ' + this.querySelector('h3').innerText);
                        }};
                    }});
                }});
            </script>
        </body>
        </html>
        """
        
        # Write HTML to file
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        return output_path 