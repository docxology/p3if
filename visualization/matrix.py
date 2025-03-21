"""
P3IF Matrix Visualizer

This module provides matrix visualization capabilities for P3IF data.
"""
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
from pathlib import Path
import numpy as np
import pandas as pd

from p3if.core.framework import P3IFFramework
from p3if.visualization.base import Visualizer
from p3if.utils.config import Config
from p3if.analysis.basic import BasicAnalyzer
from p3if.analysis.meta import MetaAnalyzer


class MatrixVisualizer(Visualizer):
    """Matrix visualizer for P3IF data."""
    
    def __init__(self, framework: P3IFFramework, config: Optional[Config] = None):
        """
        Initialize matrix visualizer.
        
        Args:
            framework: P3IF framework instance
            config: Optional configuration
        """
        super().__init__(framework, config)
        self.basic_analyzer = BasicAnalyzer(framework)
        self.meta_analyzer = MetaAnalyzer(framework)
    
    def visualize_relationship_matrix(self, file_path: Optional[Union[str, Path]] = None,
                                     pattern_type_x: str = "property", 
                                     pattern_type_y: str = "process",
                                     cmap: str = "YlOrRd") -> Optional[Figure]:
        """
        Visualize a matrix of relationships between two pattern types.
        
        Args:
            file_path: Optional path to save the visualization
            pattern_type_x: Pattern type for x-axis
            pattern_type_y: Pattern type for y-axis
            cmap: Colormap for the heatmap
            
        Returns:
            Matplotlib figure if file_path is None
        """
        if pattern_type_x not in ["property", "process", "perspective"] or \
           pattern_type_y not in ["property", "process", "perspective"]:
            self.logger.warning("Invalid pattern types")
            return None
        
        # Get patterns
        patterns_x = self.framework.get_patterns_by_type(pattern_type_x)
        patterns_y = self.framework.get_patterns_by_type(pattern_type_y)
        
        if not patterns_x or not patterns_y:
            self.logger.warning(f"No patterns found for {pattern_type_x} or {pattern_type_y}")
            return None
        
        # Create a mapping from pattern ID to index
        x_map = {p.id: i for i, p in enumerate(patterns_x)}
        y_map = {p.id: i for i, p in enumerate(patterns_y)}
        
        # Create a matrix
        matrix = np.zeros((len(patterns_y), len(patterns_x)))
        
        # Fill the matrix with relationship strengths
        for rel in self.framework._relationships.values():
            x_id = getattr(rel, f"{pattern_type_x}_id", None)
            y_id = getattr(rel, f"{pattern_type_y}_id", None)
            
            if x_id in x_map and y_id in y_map:
                matrix[y_map[y_id], x_map[x_id]] = rel.strength
        
        # Get pattern names
        x_names = [p.name for p in patterns_x]
        y_names = [p.name for p in patterns_y]
        
        # Shorten long names
        x_labels = [name[:20] + "..." if len(name) > 23 else name for name in x_names]
        y_labels = [name[:20] + "..." if len(name) > 23 else name for name in y_names]
        
        # Create figure
        fig_height = max(8, len(patterns_y) * 0.3)
        fig_width = max(10, len(patterns_x) * 0.3)
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Create heatmap
        sns.heatmap(matrix, annot=True, cmap=cmap, ax=ax, 
                   xticklabels=x_labels, yticklabels=y_labels,
                   cbar_kws={'label': 'Relationship Strength'})
        
        ax.set_title(f"Relationship Matrix: {pattern_type_x.capitalize()} × {pattern_type_y.capitalize()}")
        ax.set_xlabel(pattern_type_x.capitalize())
        ax.set_ylabel(pattern_type_y.capitalize())
        
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        if file_path:
            self.save_figure(fig, file_path, tight_layout=False)
            return None
        else:
            return fig
    
    def visualize_similarity_matrix(self, file_path: Optional[Union[str, Path]] = None,
                                  pattern_type: str = "property", 
                                  cmap: str = "viridis") -> Optional[Figure]:
        """
        Visualize a similarity matrix for patterns of a specific type.
        
        Args:
            file_path: Optional path to save the visualization
            pattern_type: Pattern type to visualize similarity for
            cmap: Colormap for the heatmap
            
        Returns:
            Matplotlib figure if file_path is None
        """
        if pattern_type not in ["property", "process", "perspective"]:
            self.logger.warning("Invalid pattern type")
            return None
        
        # Get similarity matrix
        similarity_data = self.basic_analyzer.get_pattern_similarity_matrix(pattern_type)
        
        if not similarity_data["patterns"]:
            self.logger.warning(f"No patterns found for {pattern_type}")
            return None
        
        # Extract matrix and pattern information
        matrix = np.array(similarity_data["matrix"])
        patterns = similarity_data["patterns"]
        
        # Get pattern names
        pattern_names = [p["name"] for p in patterns]
        
        # Get pattern domains for coloring
        pattern_domains = [p.get("domain") for p in patterns]
        unique_domains = sorted(set(d for d in pattern_domains if d))
        domain_to_idx = {domain: i for i, domain in enumerate(unique_domains)}
        
        # Create domain color mapping
        domain_colors = self.get_domain_colors()
        
        # Create figure
        fig_size = max(8, len(patterns) * 0.3)
        fig, ax = plt.subplots(figsize=(fig_size, fig_size))
        
        # Create heatmap
        im = sns.heatmap(matrix, annot=False, cmap=cmap, ax=ax, 
                       xticklabels=pattern_names, yticklabels=pattern_names,
                       cbar_kws={'label': 'Similarity'})
        
        # Color the tick labels by domain
        if pattern_domains and any(pattern_domains):
            for i, domain in enumerate(pattern_domains):
                if domain:
                    color = domain_colors.get(domain, "#000000")
                    plt.setp(ax.get_xticklabels()[i], color=color)
                    plt.setp(ax.get_yticklabels()[i], color=color)
        
        ax.set_title(f"Similarity Matrix: {pattern_type.capitalize()}")
        
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        if file_path:
            self.save_figure(fig, file_path, tight_layout=False)
            return None
        else:
            return fig
    
    def visualize_domain_similarity(self, file_path: Optional[Union[str, Path]] = None,
                                  cmap: str = "YlGnBu") -> Optional[Figure]:
        """
        Visualize a similarity matrix between domains.
        
        Args:
            file_path: Optional path to save the visualization
            cmap: Colormap for the heatmap
            
        Returns:
            Matplotlib figure if file_path is None
        """
        # Get domain comparison data
        domain_data = self.meta_analyzer.get_domain_comparison()
        
        if not domain_data["domains"]:
            self.logger.warning("No domains found")
            return None
        
        # Extract similarity matrix and domain names
        similarity_matrix = np.array(domain_data["similarity_matrix"])
        domains = domain_data["domains"]
        
        # Create figure
        fig_size = max(8, len(domains) * 0.5)
        fig, ax = plt.subplots(figsize=(fig_size, fig_size))
        
        # Create heatmap
        sns.heatmap(similarity_matrix, annot=True, cmap=cmap, ax=ax, 
                   xticklabels=domains, yticklabels=domains,
                   cbar_kws={'label': 'Similarity'})
        
        ax.set_title("Domain Similarity Matrix")
        
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        if file_path:
            self.save_figure(fig, file_path, tight_layout=False)
            return None
        else:
            return fig
    
    def visualize_pattern_correlation(self, file_path: Optional[Union[str, Path]] = None,
                                    cmap: str = "coolwarm") -> Optional[Figure]:
        """
        Visualize correlation matrix between pattern metrics across domains.
        
        Args:
            file_path: Optional path to save the visualization
            cmap: Colormap for the heatmap
            
        Returns:
            Matplotlib figure if file_path is None
        """
        # Get pattern correlation data
        correlation_data = self.meta_analyzer.get_pattern_correlation_matrix()
        
        if not correlation_data.get("correlation_matrix"):
            self.logger.warning("No correlation data found")
            return None
        
        # Extract correlation matrix and feature names
        correlation_matrix = np.array(correlation_data["correlation_matrix"])
        features = correlation_data["features"]
        
        # Create pretty labels
        pretty_labels = [f.replace("num_", "").capitalize() for f in features]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create heatmap
        sns.heatmap(correlation_matrix, annot=True, cmap=cmap, ax=ax, 
                   xticklabels=pretty_labels, yticklabels=pretty_labels,
                   vmin=-1, vmax=1, center=0, 
                   cbar_kws={'label': 'Correlation'})
        
        ax.set_title("Correlation Matrix Between Pattern Metrics")
        
        if file_path:
            self.save_figure(fig, file_path)
            return None
        else:
            return fig
    
    def visualize_domain_metrics(self, file_path: Optional[Union[str, Path]] = None,
                               normalize: bool = True) -> Optional[Figure]:
        """
        Visualize metrics for each domain.
        
        Args:
            file_path: Optional path to save the visualization
            normalize: Whether to normalize values for each metric
            
        Returns:
            Matplotlib figure if file_path is None
        """
        # Get domain comparison data
        domain_data = self.meta_analyzer.get_domain_comparison()
        
        if not domain_data["domains"]:
            self.logger.warning("No domains found")
            return None
        
        # Extract domains, metrics, and data
        domains = domain_data["domains"]
        metrics = domain_data["metrics"]
        data = np.array(domain_data["data"])
        
        if normalize:
            # Normalize each column (metric) to 0-1 range
            for j in range(data.shape[1]):
                column = data[:, j]
                min_val = np.min(column)
                max_val = np.max(column)
                if max_val > min_val:
                    data[:, j] = (column - min_val) / (max_val - min_val)
        
        # Create pretty labels
        pretty_metrics = [m.replace("num_", "").capitalize() for m in metrics]
        
        # Create figure
        fig_width = max(10, len(domains) * 0.5)
        fig, ax = plt.subplots(figsize=(fig_width, 8))
        
        # Create heatmap
        im = sns.heatmap(data.T, annot=True, cmap="YlGnBu", ax=ax, 
                       xticklabels=domains, yticklabels=pretty_metrics,
                       cbar_kws={'label': 'Normalized Value' if normalize else 'Value'})
        
        # Display actual values in cells if not normalized
        if not normalize:
            for i in range(len(pretty_metrics)):
                for j in range(len(domains)):
                    text = ax.text(j + 0.5, i + 0.5, f"{data[j, i]:.0f}",
                                ha="center", va="center", color="black")
        
        ax.set_title("Domain Metrics Comparison")
        ax.set_xlabel("Domains")
        ax.set_ylabel("Metrics")
        
        plt.xticks(rotation=45, ha='right')
        
        if file_path:
            self.save_figure(fig, file_path)
            return None
        else:
            return fig 