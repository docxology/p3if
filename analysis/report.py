"""
P3IF Analysis Report

This module provides report generation functionality for P3IF analysis results.
"""
from typing import Dict, List, Any, Optional, Union
import logging
import json
import os
from pathlib import Path
import datetime

from core.framework import P3IFFramework
from analysis.basic import BasicAnalyzer
from analysis.network import NetworkAnalyzer
from analysis.meta import MetaAnalyzer


class AnalysisReport:
    """Generator for P3IF analysis reports."""
    
    def __init__(self, framework: P3IFFramework):
        """
        Initialize analysis report generator.
        
        Args:
            framework: P3IF framework instance
        """
        self.framework = framework
        self.logger = logging.getLogger(__name__)
        
        # Initialize analyzers
        self.basic_analyzer = BasicAnalyzer(framework)
        self.network_analyzer = NetworkAnalyzer(framework)
        self.meta_analyzer = MetaAnalyzer(framework)
        
        # Analysis results cache
        self._results = None
    
    def run_analysis(self, include_basic: bool = True, include_network: bool = True, 
                    include_meta: bool = True) -> Dict[str, Any]:
        """
        Run comprehensive analysis on the framework.
        
        Args:
            include_basic: Whether to include basic analysis
            include_network: Whether to include network analysis
            include_meta: Whether to include meta-analysis
            
        Returns:
            Dictionary containing all analysis results
        """
        results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "summary": {
                "num_patterns": len(self.framework._patterns),
                "num_relationships": len(self.framework._relationships)
            }
        }
        
        if include_basic:
            self.logger.info("Running basic analysis...")
            results["basic"] = self.basic_analyzer.run_full_analysis()
        
        if include_network:
            self.logger.info("Running network analysis...")
            results["network"] = self.network_analyzer.run_full_analysis()
        
        if include_meta:
            self.logger.info("Running meta-analysis...")
            results["meta"] = self.meta_analyzer.run_full_analysis()
        
        self._results = results
        return results
    
    def export_to_json(self, file_path: Union[str, Path]) -> None:
        """
        Export analysis results to a JSON file.
        
        Args:
            file_path: Path to output file
        """
        if self._results is None:
            self.logger.warning("No analysis results available. Running analysis...")
            self.run_analysis()
        
        path = Path(file_path)
        os.makedirs(path.parent, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self._results, f, indent=2)
        
        self.logger.info(f"Analysis report exported to {path}")
    
    def get_domain_summary(self) -> Dict[str, Any]:
        """
        Get a summary of domain statistics.
        
        Returns:
            Dictionary containing domain summary
        """
        if self._results is None or "meta" not in self._results:
            self.logger.warning("Meta-analysis results not available. Running analysis...")
            self.run_analysis(include_basic=False, include_network=False, include_meta=True)
        
        # Extract domain information from meta-analysis
        domain_comparison = self._results.get("meta", {}).get("domain_comparison", {})
        cross_domain = self._results.get("meta", {}).get("cross_domain_relationships", {})
        
        domains = domain_comparison.get("domains", [])
        metrics = domain_comparison.get("metrics", [])
        data = domain_comparison.get("data", [])
        
        # Reformat for easy consumption
        domain_stats = {}
        for i, domain in enumerate(domains):
            if i < len(data):
                domain_data = {}
                for j, metric in enumerate(metrics):
                    if j < len(data[i]):
                        domain_data[metric] = data[i][j]
                domain_stats[domain] = domain_data
        
        return {
            "domains": domains,
            "domain_stats": domain_stats,
            "cross_domain_count": cross_domain.get("count", 0),
            "domain_pairs": cross_domain.get("domain_pairs", [])
        }
    
    def get_top_patterns(self, top_n: int = 10) -> Dict[str, Any]:
        """
        Get the top patterns by connectivity.
        
        Args:
            top_n: Number of top patterns to return
            
        Returns:
            Dictionary containing top patterns
        """
        if self._results is None or "basic" not in self._results:
            self.logger.warning("Basic analysis results not available. Running analysis...")
            self.run_analysis(include_basic=True, include_network=False, include_meta=False)
        
        # Get most connected patterns
        connected_patterns = self._results.get("basic", {}).get("most_connected_patterns", {})
        strongest_relationships = self._results.get("basic", {}).get("strongest_relationships", [])
        
        # Get up to top_n patterns for each type
        result = {}
        for pattern_type, patterns in connected_patterns.items():
            result[pattern_type] = patterns[:top_n]
        
        return {
            "most_connected": result,
            "strongest_relationships": strongest_relationships[:top_n]
        }
    
    def get_network_summary(self) -> Dict[str, Any]:
        """
        Get a summary of network analysis results.
        
        Returns:
            Dictionary containing network summary
        """
        if self._results is None or "network" not in self._results:
            self.logger.warning("Network analysis results not available. Running analysis...")
            self.run_analysis(include_basic=False, include_network=True, include_meta=False)
        
        # Extract relevant network metrics
        statistics = self._results.get("network", {}).get("statistics", {})
        centrality = self._results.get("network", {}).get("centrality", {})
        communities = self._results.get("network", {}).get("communities", {})
        
        full_stats = statistics.get("full", {})
        domain_stats = statistics.get("domain", {})
        
        # Get top nodes by degree centrality
        top_nodes = {}
        for graph_type, measures in centrality.items():
            if "degree" in measures:
                top_nodes[graph_type] = measures["degree"][:5]  # Top 5 nodes
        
        # Get community summary
        community_summary = {}
        for graph_type, comm_data in communities.items():
            community_summary[graph_type] = {
                "count": comm_data.get("count", 0),
                "algorithm": comm_data.get("algorithm", {}).get("name", "unknown"),
                "modularity": comm_data.get("algorithm", {}).get("modularity", 0),
                "largest_communities": [
                    {
                        "id": c["id"],
                        "size": c["size"],
                        "node_types": self._count_node_types(c["nodes"])
                    }
                    for c in comm_data.get("communities", [])[:3]  # Top 3 communities
                ]
            }
        
        return {
            "full_network": full_stats,
            "domain_network": domain_stats,
            "top_central_nodes": top_nodes,
            "communities": community_summary
        }
    
    def _count_node_types(self, nodes: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count the number of nodes by type."""
        type_counts = {}
        for node in nodes:
            node_type = node.get("type", "unknown")
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        return type_counts
    
    def get_common_patterns_across_domains(self) -> Dict[str, Any]:
        """
        Get patterns that are common across multiple domains.
        
        Returns:
            Dictionary containing common patterns
        """
        if self._results is None or "meta" not in self._results:
            self.logger.warning("Meta-analysis results not available. Running analysis...")
            self.run_analysis(include_basic=False, include_network=False, include_meta=True)
        
        # Extract common patterns from meta-analysis
        common_patterns = self._results.get("meta", {}).get("common_patterns", {}).get("common_patterns", {})
        
        # Keep only the top patterns for each type
        top_common = {}
        for pattern_type, patterns in common_patterns.items():
            # Sort by count (in case they're not already sorted)
            sorted_patterns = sorted(patterns, key=lambda x: x["count"], reverse=True)
            top_common[pattern_type] = sorted_patterns[:10]  # Top 10 common patterns
        
        return {"common_patterns": top_common} 