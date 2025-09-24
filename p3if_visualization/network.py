"""
P3IF Network Visualizer

This module provides network visualization capabilities for P3IF data.
"""
from typing import Dict, List, Any, Optional, Union, Tuple, Set
import logging
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pathlib import Path
import numpy as np

from p3if_methods.framework import P3IFFramework
from .base import Visualizer
from utils.config import Config
from p3if_methods.analysis.network import NetworkAnalyzer


class NetworkVisualizer(Visualizer):
    """Network visualizer for P3IF data."""
    
    def __init__(self, framework: P3IFFramework, config: Optional[Config] = None):
        """
        Initialize network visualizer.
        
        Args:
            framework: P3IF framework instance
            config: Optional configuration
        """
        super().__init__(framework, config)
        self.network_analyzer = NetworkAnalyzer(framework)
    
    def visualize_full_network(self, file_path: Optional[Union[str, Path]] = None,
                               layout: str = "spring", color_by: str = "type", 
                               min_edge_width: float = 1.0, max_edge_width: float = 5.0,
                               show_labels: bool = True) -> Optional[Figure]:
        """
        Visualize the full P3IF network.
        
        Args:
            file_path: Optional path to save the visualization
            layout: Network layout algorithm
            color_by: How to color nodes (type or domain)
            min_edge_width: Minimum edge width
            max_edge_width: Maximum edge width
            show_labels: Whether to show node labels
            
        Returns:
            Matplotlib figure if file_path is None
        """
        G = self.network_analyzer.get_graph("full")
        
        if len(G.nodes) == 0:
            self.logger.warning("Empty graph, nothing to visualize")
            return None
        
        # Get node positions using the specified layout
        if layout == "spring":
            pos = nx.spring_layout(G, seed=42)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "shell":
            pos = nx.shell_layout(G)
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G)
        else:
            self.logger.warning(f"Unknown layout: {layout}, using spring layout")
            pos = nx.spring_layout(G, seed=42)
        
        # Get node colors
        node_colors = []
        if color_by == "type":
            type_colors = self.get_pattern_type_colors()
            node_colors = [type_colors.get(G.nodes[n].get("type", "unknown"), "#cccccc") for n in G.nodes]
        elif color_by == "domain":
            domain_colors = self.get_domain_colors()
            node_colors = [domain_colors.get(G.nodes[n].get("domain", "unknown"), "#cccccc") for n in G.nodes]
        
        # Get edge widths
        edge_weights = [G[u][v].get('weight', 0.5) for u, v in G.edges]
        if edge_weights:
            # Normalize edge widths
            min_weight = min(edge_weights)
            max_weight = max(edge_weights)
            if min_weight == max_weight:
                edge_widths = [min_edge_width] * len(edge_weights)
            else:
                edge_widths = [
                    min_edge_width + (w - min_weight) / (max_weight - min_weight) * (max_edge_width - min_edge_width)
                    for w in edge_weights
                ]
        else:
            edge_widths = []
        
        # Create figure
        fig, ax = self.setup_figure()
        
        # Draw the network
        nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.7, edge_color="#999999")
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=self.node_size)
        
        if show_labels:
            # Create shorter labels
            labels = {}
            for node in G.nodes:
                node_data = G.nodes[node]
                name = node_data.get('name', str(node))
                if len(name) > 20:
                    name = name[:17] + "..."
                labels[node] = name
                
            nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
        
        # Add legend
        if color_by == "type":
            type_colors = self.get_pattern_type_colors()
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, 
                           label=pattern_type.capitalize(), markersize=10)
                for pattern_type, color in type_colors.items()
            ]
            ax.legend(handles=legend_elements, loc='upper right')
        elif color_by == "domain":
            domain_colors = self.get_domain_colors()
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, 
                           label=domain, markersize=10)
                for domain, color in domain_colors.items()
            ]
            if len(legend_elements) <= 15:  # Only show legend if not too many domains
                ax.legend(handles=legend_elements, loc='upper right')
        
        ax.set_title(f"P3IF Network Visualization (Layout: {layout}, Color by: {color_by})")
        ax.axis('off')
        
        if file_path:
            self.save_figure(fig, file_path)
            return None
        else:
            return fig
    
    def visualize_domain_network(self, file_path: Optional[Union[str, Path]] = None,
                                layout: str = "spring", min_edge_width: float = 2.0, 
                                max_edge_width: float = 10.0) -> Optional[Figure]:
        """
        Visualize the domain-level network.
        
        Args:
            file_path: Optional path to save the visualization
            layout: Network layout algorithm
            min_edge_width: Minimum edge width
            max_edge_width: Maximum edge width
            
        Returns:
            Matplotlib figure if file_path is None
        """
        G = self.network_analyzer.get_graph("domain")
        
        if len(G.nodes) == 0:
            self.logger.warning("Empty domain graph, nothing to visualize")
            return None
        
        # Get node positions using the specified layout
        if layout == "spring":
            pos = nx.spring_layout(G, seed=42)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "shell":
            pos = nx.shell_layout(G)
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G)
        else:
            self.logger.warning(f"Unknown layout: {layout}, using spring layout")
            pos = nx.spring_layout(G, seed=42)
        
        # Get node sizes based on the number of patterns in each domain
        domain_sizes = {}
        for pattern in self.framework._patterns.values():
            domain = getattr(pattern, "domain", None)
            if domain:
                domain_sizes[domain] = domain_sizes.get(domain, 0) + 1
        
        # Normalize node sizes
        node_sizes = []
        for node in G.nodes:
            size = domain_sizes.get(node, 0)
            # Scale node size between 100 and 1000
            node_sizes.append(100 + size * 20)
        
        # Get edge widths
        edge_weights = [G[u][v].get('weight', 0.5) for u, v in G.edges]
        if edge_weights:
            # Normalize edge widths
            min_weight = min(edge_weights)
            max_weight = max(edge_weights)
            if min_weight == max_weight:
                edge_widths = [min_edge_width] * len(edge_weights)
            else:
                edge_widths = [
                    min_edge_width + (w - min_weight) / (max_weight - min_weight) * (max_edge_width - min_edge_width)
                    for w in edge_weights
                ]
        else:
            edge_widths = []
        
        # Get domain colors
        domain_colors = self.get_domain_colors()
        node_colors = [domain_colors.get(node, "#cccccc") for node in G.nodes]
        
        # Create figure
        fig, ax = self.setup_figure()
        
        # Draw the network
        nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.7, edge_color="#999999")
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        # Add edge labels for weights
        if len(G.edges) <= 20:  # Only show edge labels if not too many edges
            edge_labels = {(u, v): f"{G[u][v].get('weight', 0):.2f}" for u, v in G.edges}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
        ax.set_title("Domain Interaction Network")
        ax.axis('off')
        
        if file_path:
            self.save_figure(fig, file_path)
            return None
        else:
            return fig
    
    def visualize_communities(self, file_path: Optional[Union[str, Path]] = None,
                             graph_type: str = "full", algorithm: str = "louvain") -> Optional[Figure]:
        """
        Visualize communities in the network.
        
        Args:
            file_path: Optional path to save the visualization
            graph_type: Type of graph to visualize communities for
            algorithm: Community detection algorithm
            
        Returns:
            Matplotlib figure if file_path is None
        """
        # Get communities
        communities = self.network_analyzer.get_communities(graph_type, algorithm)
        
        if not communities.get("communities"):
            self.logger.warning(f"No communities found for {graph_type} graph using {algorithm} algorithm")
            return None
        
        # Get the graph
        G = self.network_analyzer.get_graph(graph_type)
        
        # Get node positions
        pos = nx.spring_layout(G, seed=42)
        
        # Create a mapping from node ID to community ID
        node_community = {}
        for comm in communities.get("communities", []):
            for node in comm.get("nodes", []):
                node_community[node.get("id")] = comm.get("id")
        
        # Get colors for communities
        community_ids = sorted(set(node_community.values()))
        community_colors = self.get_color_palette(len(community_ids))
        community_color_map = dict(zip(community_ids, community_colors))
        
        # Get node colors based on community
        node_colors = [community_color_map.get(node_community.get(node, -1), "#cccccc") for node in G.nodes]
        
        # Create figure
        fig, ax = self.setup_figure()
        
        # Draw the network
        nx.draw_networkx_edges(G, pos, alpha=0.2, edge_color="#999999")
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=self.node_size)
        
        # Add legend for communities
        if len(community_ids) <= 15:  # Only show legend if not too many communities
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=community_color_map[comm_id], 
                           label=f"Community {comm_id}", markersize=10)
                for comm_id in community_ids
            ]
            ax.legend(handles=legend_elements, loc='upper right')
        
        ax.set_title(f"Community Detection ({algorithm})")
        ax.axis('off')
        
        if file_path:
            self.save_figure(fig, file_path)
            return None
        else:
            return fig
    
    def visualize_centrality(self, file_path: Optional[Union[str, Path]] = None,
                            graph_type: str = "full", measure: str = "degree") -> Optional[Figure]:
        """
        Visualize node centrality in the network.
        
        Args:
            file_path: Optional path to save the visualization
            graph_type: Type of graph to visualize centrality for
            measure: Centrality measure to visualize
            
        Returns:
            Matplotlib figure if file_path is None
        """
        # Get the graph
        G = self.network_analyzer.get_graph(graph_type)
        
        # Get centrality measures
        centrality_measures = self.network_analyzer.get_centrality_measures(graph_type)
        
        if measure not in centrality_measures or not centrality_measures[measure]:
            self.logger.warning(f"No {measure} centrality data found for {graph_type} graph")
            return None
        
        # Create a mapping from node ID to centrality value
        centrality_values = {}
        for node_data in centrality_measures[measure]:
            centrality_values[node_data.get("id")] = node_data.get("value", 0)
        
        # Get node positions
        pos = nx.spring_layout(G, seed=42)
        
        # Get node sizes based on centrality value
        node_sizes = []
        for node in G.nodes:
            value = centrality_values.get(node, 0)
            # Scale node size between 10 and 500
            node_sizes.append(10 + value * 3000)
        
        # Get node colors based on domain or type
        if graph_type == "domain":
            node_colors = list(range(len(G.nodes)))  # Just use a gradient for domains
        else:
            type_colors = self.get_pattern_type_colors()
            node_colors = [type_colors.get(G.nodes[n].get("type", "unknown"), "#cccccc") for n in G.nodes]
        
        # Create figure
        fig, ax = self.setup_figure()
        
        # Draw the network
        nx.draw_networkx_edges(G, pos, alpha=0.2, edge_color="#999999")
        nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, cmap=plt.cm.viridis if graph_type == "domain" else None)
        
        # Add labels for top nodes
        top_nodes = sorted(centrality_values.items(), key=lambda x: x[1], reverse=True)[:5]
        top_node_ids = [node_id for node_id, _ in top_nodes]
        
        labels = {}
        for node in top_node_ids:
            if node in G.nodes:
                if graph_type == "domain":
                    labels[node] = node  # Domain name is the node ID
                else:
                    name = G.nodes[node].get('name', str(node))
                    if len(name) > 20:
                        name = name[:17] + "..."
                    labels[node] = name
        
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold')
        
        # Add a colorbar for domain graph
        if graph_type == "domain":
            plt.colorbar(nodes, ax=ax, label=f"{measure.capitalize()} Centrality")
        
        ax.set_title(f"{measure.capitalize()} Centrality Visualization")
        ax.axis('off')
        
        if file_path:
            self.save_figure(fig, file_path)
            return None
        else:
            return fig 