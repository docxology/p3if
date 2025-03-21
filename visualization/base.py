"""
P3IF Base Visualizer

This module provides the base visualization class for P3IF data.
"""
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import os
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
import time
import threading

from p3if.core.framework import P3IFFramework
from p3if.utils.config import Config


class Visualizer:
    """Base class for all P3IF visualizers."""
    
    def __init__(self, framework: P3IFFramework, config: Optional[Config] = None):
        """
        Initialize the visualizer.
        
        Args:
            framework: P3IF framework instance
            config: Optional configuration
        """
        self.framework = framework
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        
        # Set up default visualization settings
        self._setup_visualization_defaults()
    
    def _setup_visualization_defaults(self) -> None:
        """Set up default visualization settings."""
        # Get theme configuration
        theme_name = self.config.get("visualization.default_style", "modern")
        theme = self.config.get(f"visualization.themes.{theme_name}", {})
        
        # Set default values if not specified in config
        self.colormap = theme.get("colormap", "viridis")
        self.node_size = theme.get("node_size", 50)
        self.edge_width = theme.get("edge_width", 1.5)
        self.figsize = theme.get("figsize", (12, 8))
        self.dpi = theme.get("dpi", 100)
        
        # Configure seaborn and matplotlib
        sns.set_theme(style="whitegrid")
        plt.rcParams["figure.figsize"] = self.figsize
        plt.rcParams["figure.dpi"] = self.dpi
    
    def save_figure(self, fig: plt.Figure, file_path: Union[str, Path], 
                    title: Optional[str] = None, tight_layout: bool = True) -> None:
        """
        Save a matplotlib figure to a file.
        
        Args:
            fig: Matplotlib figure
            file_path: Path to save the figure
            title: Optional title for the figure
            tight_layout: Whether to apply tight layout
        """
        # Set a timeout for the figure saving operation
        MAX_SAVE_TIME = 30  # seconds
        
        if title:
            fig.suptitle(title, fontsize=16, y=0.98)
        
        if tight_layout:
            fig.tight_layout(rect=[0, 0, 1, 0.95] if title else [0, 0, 1, 1])
        
        path = Path(file_path)
        os.makedirs(path.parent, exist_ok=True)
        
        # Use a thread with a timeout to save the figure
        save_completed = False
        save_thread = None
        
        def _save_figure():
            nonlocal save_completed
            try:
                fig.savefig(path, dpi=self.dpi, bbox_inches="tight")
                save_completed = True
            except Exception as e:
                self.logger.error(f"Error saving figure to {path}: {e}")
        
        try:
            save_thread = threading.Thread(target=_save_figure)
            save_thread.daemon = True
            save_thread.start()
            
            # Wait for the save to complete or timeout
            save_thread.join(timeout=MAX_SAVE_TIME)
            
            if save_completed:
                self.logger.info(f"Figure saved to {path}")
            else:
                self.logger.warning(f"Figure save operation timed out after {MAX_SAVE_TIME} seconds: {path}")
        finally:
            plt.close(fig)
    
    def get_color_palette(self, n_colors: int) -> List[str]:
        """
        Get a color palette for visualization.
        
        Args:
            n_colors: Number of colors to generate
            
        Returns:
            List of color strings
        """
        return sns.color_palette(self.colormap, n_colors=n_colors).as_hex()
    
    def get_domain_colors(self) -> Dict[str, str]:
        """
        Get a consistent color mapping for domains.
        
        Returns:
            Dictionary mapping domain names to color strings
        """
        # Get all domains from patterns
        domains = set()
        for pattern in self.framework._patterns.values():
            domain = getattr(pattern, "domain", None)
            if domain:
                domains.add(domain)
        
        # Generate colors
        domain_list = sorted(domains)
        colors = self.get_color_palette(len(domain_list))
        
        return dict(zip(domain_list, colors))
    
    def get_pattern_type_colors(self) -> Dict[str, str]:
        """
        Get a consistent color mapping for pattern types.
        
        Returns:
            Dictionary mapping pattern types to color strings
        """
        pattern_types = ["property", "process", "perspective"]
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]  # Default colors for pattern types
        
        return dict(zip(pattern_types, colors))
    
    def setup_figure(self, nrows: int = 1, ncols: int = 1, 
                     figsize: Optional[Tuple[float, float]] = None) -> Tuple[plt.Figure, Any]:
        """
        Set up a matplotlib figure and axes.
        
        Args:
            nrows: Number of rows
            ncols: Number of columns
            figsize: Optional figure size
            
        Returns:
            Tuple of (figure, axes)
        """
        fig_size = figsize or self.figsize
        if nrows > 1 or ncols > 1:
            # Adjust figure size for subplots
            width, height = fig_size
            fig_size = (width * ncols, height * nrows)
        
        fig, axes = plt.subplots(nrows, ncols, figsize=fig_size)
        return fig, axes 