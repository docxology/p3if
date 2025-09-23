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
import datetime
import os

from core.framework import P3IFFramework
from core.models import BasePattern
from visualization.base import Visualizer
from utils.config import Config
from analysis.basic import BasicAnalyzer
from analysis.meta import MetaAnalyzer


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
    
    def visualize_relationship_matrix(
        self,
        file_path: Union[str, Path],
        pattern_type_x: str,
        pattern_type_y: str,
        relationship_type: Optional[str] = None,
        cmap: str = "YlOrRd",
        top_n: Optional[int] = 100,
        min_relationship_strength: float = 0.0,
        title: Optional[str] = None,
        annotate: Optional[bool] = None,
        font_size: int = 8,
        max_patterns: int = 25,
        use_progressive_rendering: bool = True
    ) -> None:
        """
        Visualize a matrix of relationships between two pattern types.
        
        Args:
            file_path: Path to save the visualization
            pattern_type_x: Pattern type for the x-axis
            pattern_type_y: Pattern type for the y-axis
            relationship_type: Type of relationship to visualize
            cmap: Colormap to use
            top_n: Number of top relationships to include
            min_relationship_strength: Minimum relationship strength to include
            title: Title for the visualization
            annotate: Whether to annotate the heatmap with strength values
            font_size: Font size for annotations
            max_patterns: Maximum number of patterns to include on each axis
            use_progressive_rendering: Whether to use progressive rendering for large matrices
        """
        if pattern_type_x not in ["property", "process", "perspective"] or \
           pattern_type_y not in ["property", "process", "perspective"]:
            self.logger.warning("Invalid pattern types")
            return
        
        # Get patterns for each pattern type
        patterns_x = self.framework.get_patterns_by_type(pattern_type_x)
        patterns_y = self.framework.get_patterns_by_type(pattern_type_y)
        
        # If either list is too large, limit to the most connected patterns
        if len(patterns_x) > max_patterns:
            self.logger.info(f"Limiting {pattern_type_x} patterns from {len(patterns_x)} to {max_patterns}")
            # Sort patterns by number of relationships (most connected first)
            patterns_x = sorted(
                patterns_x,
                key=lambda p: sum(1 for r in self.framework._relationships.values() if 
                              (p.type == "property" and r.property_id == p.id) or
                              (p.type == "process" and r.process_id == p.id) or
                              (p.type == "perspective" and r.perspective_id == p.id)),
                reverse=True
            )[:max_patterns]
        
        if len(patterns_y) > max_patterns:
            self.logger.info(f"Limiting {pattern_type_y} patterns from {len(patterns_y)} to {max_patterns}")
            patterns_y = sorted(
                patterns_y,
                key=lambda p: sum(1 for r in self.framework._relationships.values() if 
                              (p.type == "property" and r.property_id == p.id) or
                              (p.type == "process" and r.process_id == p.id) or
                              (p.type == "perspective" and r.perspective_id == p.id)),
                reverse=True
            )[:max_patterns]
        
        # Check if we have patterns of both types
        if not patterns_x or not patterns_y:
            self.logger.warning(f"No patterns found for {pattern_type_x} or {pattern_type_y}")
            return
        
        # Calculate matrix dimensions
        matrix_size = len(patterns_x) * len(patterns_y)
        matrix_is_large = matrix_size > 400
        
        # Determine if we should use progressive rendering for large matrices
        if use_progressive_rendering and matrix_is_large:
            self.logger.info(f"Using progressive rendering for large matrix ({len(patterns_x)}x{len(patterns_y)} = {matrix_size} cells)")
            return self.visualize_relationship_matrix_progressive(
                file_path=file_path,
                pattern_type_x=pattern_type_x,
                pattern_type_y=pattern_type_y,
                patterns_x=patterns_x,
                patterns_y=patterns_y,
                relationship_type=relationship_type,
                cmap=cmap,
                min_relationship_strength=min_relationship_strength,
                title=title,
                font_size=font_size
            )
        
        # Create mapping from pattern IDs to indices
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
        x_labels = [name[:15] + "..." if len(name) > 18 else name for name in x_names]
        y_labels = [name[:15] + "..." if len(name) > 18 else name for name in y_names]
        
        # Create figure with optimized size
        fig_height = min(max(8, len(patterns_y) * 0.25), 20)  # Cap height at 20
        fig_width = min(max(10, len(patterns_x) * 0.25), 24)  # Cap width at 24
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Determine whether to show annotations based on matrix size
        if annotate is None:
            # Auto-determine whether to show annotations
            annotate = matrix_size <= 400
        
        # Create heatmap
        sns.heatmap(matrix, annot=annotate, cmap=cmap, ax=ax, 
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
    
    def visualize_domain_similarity(self, file_path: Union[str, Path] = None,
                                 min_similarity: float = 0.0,
                                 normalize: bool = True,
                                 max_domains: int = 30) -> Optional[Figure]:
        """
        Visualize similarity between domains.
        
        Args:
            file_path: Optional path to save the visualization
            min_similarity: Minimum similarity to include
            normalize: Whether to normalize similarity values
            max_domains: Maximum number of domains to include
            
        Returns:
            Matplotlib figure if file_path is None
        """
        # Get all domains
        domains = set()
        for pattern in self.framework._patterns.values():
            domain = getattr(pattern, "domain", None)
            if domain:
                domains.add(domain)
        
        domains = list(domains)
        
        if not domains:
            self.logger.warning("No domains found")
            return None
        
        # Limit domains if too many
        if len(domains) > max_domains:
            self.logger.warning(f"Too many domains ({len(domains)}), limiting to {max_domains}")
            
            # Find domains with most patterns
            domain_pattern_counts = {}
            for pattern in self.framework._patterns.values():
                domain = getattr(pattern, "domain", None)
                if domain:
                    domain_pattern_counts[domain] = domain_pattern_counts.get(domain, 0) + 1
            
            # Sort domains by pattern count
            domains = sorted(domains, key=lambda d: domain_pattern_counts.get(d, 0), reverse=True)[:max_domains]
        
        # Create similarity matrix
        n = len(domains)
        similarity = np.zeros((n, n))
        domain_to_idx = {domain: i for i, domain in enumerate(domains)}
        
        # Calculate similarity
        # Process in batches to avoid timeouts
        BATCH_SIZE = 5
        for i in range(0, n, BATCH_SIZE):
            batch_end = min(i + BATCH_SIZE, n)
            batch_domains = domains[i:batch_end]
            
            for domain1 in batch_domains:
                domain1_idx = domain_to_idx[domain1]
                
                # Get patterns for domain1
                domain1_patterns = set()
                for pattern in self.framework._patterns.values():
                    if getattr(pattern, "domain", None) == domain1:
                        domain1_patterns.add(pattern.id)
                
                # Calculate intersection with all other domains
                for domain2 in domains:
                    domain2_idx = domain_to_idx[domain2]
                    
                    # Set diagonal to 1.0
                    if domain1 == domain2:
                        similarity[domain1_idx, domain2_idx] = 1.0
                        continue
                    
                    # Get patterns for domain2
                    domain2_patterns = set()
                    for pattern in self.framework._patterns.values():
                        if getattr(pattern, "domain", None) == domain2:
                            domain2_patterns.add(pattern.id)
                    
                    # Calculate Jaccard similarity
                    if domain1_patterns and domain2_patterns:
                        intersection = len(domain1_patterns.intersection(domain2_patterns))
                        union = len(domain1_patterns.union(domain2_patterns))
                        sim = intersection / union if union > 0 else 0.0
                        similarity[domain1_idx, domain2_idx] = sim
        
        # Create figure
        fig_width = min(24, max(8, n * 0.5))
        fig_height = min(20, max(6, n * 0.5))
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Create heatmap
        mask = similarity < min_similarity if min_similarity > 0 else None
        sns.heatmap(similarity, annot=n <= 20, cmap="viridis", 
                   xticklabels=domains, yticklabels=domains, 
                   mask=mask, ax=ax,
                   cbar_kws={'label': 'Similarity'})
        
        ax.set_title("Domain Similarity")
        
        # Rotate x labels for better readability
        plt.xticks(rotation=45, ha="right")
        
        # Save figure if path provided
        if file_path:
            self.save_figure(fig, file_path)
            return None
        else:
            return fig
    
    def visualize_domain_metrics(self, file_path: str,
                                domains: List[str],
                                metrics: Optional[List[str]] = None,
                                cmap: str = "viridis",
                                title: Optional[str] = None,
                                font_size: int = 10,
                                normalize: bool = False) -> Figure:
        """
        Create a domain metrics matrix visualization.
        
        Args:
            file_path: Path to save the visualization
            domains: List of domains to visualize
            metrics: List of metrics to include (default: pattern_count, relationship_count)
            cmap: Colormap to use
            title: Title for the plot
            font_size: Font size for axis labels
            normalize: Whether to normalize the metrics
            
        Returns:
            Matplotlib Figure object
        """
        # Default metrics if not specified
        if metrics is None:
            metrics = ["pattern_count", "relationship_count", "average_strength"]
        
        # Create domain metrics data
        domain_metrics = {}
        
        for domain in domains:
            # Get patterns for this domain
            domain_patterns = []
            for pattern in self.framework._patterns.values():
                if getattr(pattern, "domain", None) == domain:
                    domain_patterns.append(pattern)
            
            # Count patterns by type
            pattern_counts = {
                "property": 0,
                "process": 0,
                "perspective": 0
            }
            
            for pattern in domain_patterns:
                if pattern.type in pattern_counts:
                    pattern_counts[pattern.type] += 1
            
            # Count relationships and calculate average strength
            relationship_count = 0
            total_strength = 0.0
            
            for rel in self.framework._relationships.values():
                rel_patterns = []
                
                # Check if this relationship involves a pattern from this domain
                # Look at property_id, process_id, and perspective_id instead of pattern_a_id and pattern_b_id
                if rel.property_id:
                    pattern = self.framework.get_pattern(rel.property_id)
                    if pattern and getattr(pattern, "domain", None) == domain:
                        rel_patterns.append(pattern)
                
                if rel.process_id:
                    pattern = self.framework.get_pattern(rel.process_id)
                    if pattern and getattr(pattern, "domain", None) == domain:
                        rel_patterns.append(pattern)
                
                if rel.perspective_id:
                    pattern = self.framework.get_pattern(rel.perspective_id)
                    if pattern and getattr(pattern, "domain", None) == domain:
                        rel_patterns.append(pattern)
                
                # If this relationship connects at least two patterns in this domain
                if len(rel_patterns) >= 2:
                    relationship_count += 1
                    total_strength += rel.strength
            
            # Calculate average relationship strength
            avg_strength = total_strength / relationship_count if relationship_count > 0 else 0.0
            
            # Store metrics for this domain
            domain_metrics[domain] = {
                "pattern_count": sum(pattern_counts.values()),
                "property_count": pattern_counts["property"],
                "process_count": pattern_counts["process"],
                "perspective_count": pattern_counts["perspective"],
                "relationship_count": relationship_count,
                "average_strength": avg_strength
            }
        
        # Create metrics matrix
        metrics_matrix = np.zeros((len(domains), len(metrics)))
        for i, domain in enumerate(domains):
            for j, metric in enumerate(metrics):
                metrics_matrix[i, j] = domain_metrics[domain].get(metric, 0)
        
        # Normalize if requested
        if normalize:
            # Normalize each column (metric) independently
            for j in range(metrics_matrix.shape[1]):
                col = metrics_matrix[:, j]
                col_min, col_max = col.min(), col.max()
                if col_max > col_min:
                    metrics_matrix[:, j] = (col - col_min) / (col_max - col_min)
        
        # Create figure
        fig_width = min(24, max(8, len(metrics) * 0.7))
        fig_height = min(20, max(6, len(domains) * 0.5))
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Create heatmap
        sns.heatmap(metrics_matrix, annot=True, cmap=cmap, 
                   xticklabels=metrics, yticklabels=domains, ax=ax,
                   cbar_kws={'label': 'Value'})
        
        ax.set_title(title or "Domain Metrics")
        
        # Rotate x labels for better readability
        plt.xticks(rotation=45, ha="right")
        
        # Save figure if path provided
        if file_path:
            self.save_figure(fig, file_path)
            return None
        else:
            return fig
    
    def visualize_pattern_correlation(self, file_path: Union[str, Path] = None,
                                    min_correlation: float = 0.0,
                                    max_patterns: int = 100) -> Optional[Figure]:
        """
        Create a correlation matrix visualization between patterns.
        
        Args:
            file_path: Path to save the visualization
            min_correlation: Minimum correlation value to include in the visualization
            max_patterns: Maximum number of patterns to include
            
        Returns:
            Matplotlib Figure object if file_path is None, otherwise None
        """
        # Get all patterns
        patterns = list(self.framework._patterns.values())
        
        # Limit number of patterns if necessary
        if len(patterns) > max_patterns:
            self.logger.info(f"Limiting patterns from {len(patterns)} to {max_patterns}")
            # Sort patterns by number of relationships (most connected first)
            patterns = sorted(
                patterns,
                key=lambda p: sum(1 for r in self.framework._relationships.values() if 
                              (p.type == "property" and r.property_id == p.id) or
                              (p.type == "process" and r.process_id == p.id) or
                              (p.type == "perspective" and r.perspective_id == p.id)),
                reverse=True
            )[:max_patterns]
        
        n = len(patterns)
        correlation = np.zeros((n, n))
        pattern_labels = [f"{p.type[0].upper()}: {p.name}" for p in patterns]
        
        # Calculate correlation between patterns
        for i, pattern1 in enumerate(patterns):
            for j, pattern2 in enumerate(patterns):
                if i == j:
                    correlation[i, j] = 1.0  # Self-correlation
                    continue
                
                # Find all relationships between these patterns
                related = 0
                for rel in self.framework._relationships.values():
                    if ((rel.property_id == pattern1.id and 
                         (rel.process_id == pattern2.id or rel.perspective_id == pattern2.id)) or
                        (rel.process_id == pattern1.id and 
                         (rel.property_id == pattern2.id or rel.perspective_id == pattern2.id)) or
                        (rel.perspective_id == pattern1.id and 
                         (rel.property_id == pattern2.id or rel.process_id == pattern2.id))):
                        related = 1
                        correlation[i, j] = rel.strength
                        break
        
        # Create figure
        fig_width = min(24, max(8, n * 0.25))
        fig_height = min(20, max(6, n * 0.25))
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Create heatmap
        mask = correlation < min_correlation if min_correlation > 0 else None
        sns.heatmap(correlation, annot=n <= 20, cmap="viridis", 
                   xticklabels=pattern_labels, yticklabels=pattern_labels, 
                   mask=mask, ax=ax,
                   cbar_kws={'label': 'Correlation'})
        
        ax.set_title("Pattern Correlation Matrix")
        
        # Rotate x labels for better readability
        plt.xticks(rotation=45, ha="right")
        
        # Save figure if path provided
        if file_path:
            self.save_figure(fig, file_path)
            return None
        else:
            return fig
    
    def visualize_relationship_matrix_progressive(
        self,
        file_path: Union[str, Path],
        pattern_type_x: str,
        pattern_type_y: str,
        patterns_x: List[BasePattern],
        patterns_y: List[BasePattern],
        relationship_type: Optional[str] = None,
        cmap: str = "YlOrRd",
        min_relationship_strength: float = 0.0,
        title: Optional[str] = None,
        font_size: int = 8
    ) -> None:
        """
        Visualize a large matrix using progressive rendering to avoid timeouts.
        This breaks down large matrices into smaller chunks.
        
        Args:
            file_path: Path to save the visualization
            pattern_type_x: Pattern type for the x-axis
            pattern_type_y: Pattern type for the y-axis
            patterns_x: List of patterns for x-axis
            patterns_y: List of patterns for y-axis
            relationship_type: Type of relationship to visualize
            cmap: Colormap to use
            min_relationship_strength: Minimum relationship strength to include
            title: Title for the visualization
            font_size: Font size for annotations
        """
        logger = logging.getLogger(__name__)
        framework = self.framework
        
        # Create the figure with appropriate size
        # Cap the width and height to reasonable values
        max_width = 24
        max_height = 20
        width = min(max_width, 6 + len(patterns_x) * 0.3)
        height = min(max_height, 6 + len(patterns_y) * 0.3)
        
        fig, ax = plt.subplots(figsize=(width, height))
        
        # Create the matrix with zeros
        matrix = np.zeros((len(patterns_y), len(patterns_x)))
        
        # Create mapping from pattern IDs to indices
        pattern_x_to_idx = {p.id: i for i, p in enumerate(patterns_x)}
        pattern_y_to_idx = {p.id: i for i, p in enumerate(patterns_y)}
        
        # Create heatmap with empty data
        im = ax.imshow(matrix, cmap=plt.get_cmap(cmap), vmin=0, vmax=1)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Relationship Strength")
        
        # Initialize cells processed counter
        cells_processed = 0
        
        # Loop through each cell and progressively build the matrix
        for i, pattern_x in enumerate(patterns_x):
            for j, pattern_y in enumerate(patterns_y):
                # Find relationships involving these patterns
                relationship_strength = 0.0
                
                # Find all relationships involving both patterns
                for rel in framework._relationships.values():
                    # Check if this relationship involves both patterns
                    x_match = ((pattern_type_x == "property" and rel.property_id == pattern_x.id) or
                              (pattern_type_x == "process" and rel.process_id == pattern_x.id) or
                              (pattern_type_x == "perspective" and rel.perspective_id == pattern_x.id))
                    
                    y_match = ((pattern_type_y == "property" and rel.property_id == pattern_y.id) or
                              (pattern_type_y == "process" and rel.process_id == pattern_y.id) or
                              (pattern_type_y == "perspective" and rel.perspective_id == pattern_y.id))
                    
                    if x_match and y_match and rel.strength >= min_relationship_strength:
                        relationship_strength = max(relationship_strength, rel.strength)
                
                # Update the matrix
                matrix[i, j] = relationship_strength
                
                # Periodically update the visualization (e.g., every 100 cells)
                cells_processed += 1
                if cells_processed % 100 == 0:
                    # Update the visualization
                    im.set_array(matrix)
                    fig.canvas.draw_idle()
                    plt.pause(0.001)  # Allow the GUI to update
        
        # Create labels for the axes
        x_labels = [p.name[:15] + "..." if len(p.name) > 15 else p.name for p in patterns_x]
        y_labels = [p.name[:15] + "..." if len(p.name) > 15 else p.name for p in patterns_y]
        
        # Create the heatmap
        sns.heatmap(
            matrix,
            annot=len(patterns_x) * len(patterns_y) <= 400,  # Only annotate if matrix is small enough
            fmt=".2f",
            cmap=cmap,
            xticklabels=x_labels,
            yticklabels=y_labels,
            ax=ax,
            annot_kws={"size": font_size},
            cbar_kws={"shrink": 0.8}
        )
        
        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45, ha="right")
        
        # Set the title if provided
        if title:
            plt.title(title)
        else:
            plt.title(f"Relationship Matrix: {pattern_type_y} to {pattern_type_x}")
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the figure
        self.save_figure(fig, file_path) 