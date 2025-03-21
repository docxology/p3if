"""
P3IF Meta-Analyzer

This module provides meta-analysis capabilities for P3IF data across domains.
"""
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import logging
import numpy as np
import pandas as pd
from collections import defaultdict, Counter

from core.framework import P3IFFramework
from core.models import Pattern, Relationship
from data.domains import DomainManager


class MetaAnalyzer:
    """Meta-analyzer for P3IF data across domains."""
    
    def __init__(self, framework: P3IFFramework):
        """
        Initialize meta-analyzer.
        
        Args:
            framework: P3IF framework instance
        """
        self.framework = framework
        self.domain_manager = DomainManager(framework)
        self.logger = logging.getLogger(__name__)
    
    def get_domain_comparison(self) -> Dict[str, Any]:
        """
        Compare domains in the framework.
        
        Returns:
            Dictionary with domain comparison data
        """
        domains = self.domain_manager.get_domains()
        if not domains:
            return {"domains": [], "metrics": [], "data": []}
        
        # Get statistics for each domain
        domain_stats = self.domain_manager.get_domain_statistics()
        
        # Convert to a format suitable for visualization
        metrics = ["num_properties", "num_processes", "num_perspectives", "num_relationships"]
        data = []
        
        for domain, stats in domain_stats.items():
            domain_data = [stats.get(metric, 0) for metric in metrics]
            data.append(domain_data)
        
        # Calculate domain similarity matrix
        similarity_matrix = self._calculate_domain_similarity_matrix(domains)
        
        return {
            "domains": list(domains),
            "metrics": metrics,
            "data": data,
            "similarity_matrix": similarity_matrix
        }
    
    def _calculate_domain_similarity_matrix(self, domains: Set[str]) -> List[List[float]]:
        """
        Calculate similarity matrix between domains.
        
        Args:
            domains: Set of domain names
            
        Returns:
            2D list representing the similarity matrix
        """
        domain_list = list(domains)
        n = len(domain_list)
        similarity_matrix = np.zeros((n, n))
        
        # Get patterns by domain
        patterns_by_domain = {
            domain: self.domain_manager.get_patterns_by_domain(domain)
            for domain in domain_list
        }
        
        # Calculate Jaccard similarity for pattern names
        for i in range(n):
            for j in range(n):
                domain_i = domain_list[i]
                domain_j = domain_list[j]
                
                # Skip self-comparison
                if i == j:
                    similarity_matrix[i, j] = 1.0
                    continue
                
                # Get all pattern names for each domain
                names_i = set()
                names_j = set()
                
                for pattern_type in ["property", "process", "perspective"]:
                    names_i.update(p.name.lower() for p in patterns_by_domain[domain_i][pattern_type])
                    names_j.update(p.name.lower() for p in patterns_by_domain[domain_j][pattern_type])
                
                # Calculate Jaccard similarity
                intersection = len(names_i.intersection(names_j))
                union = len(names_i.union(names_j))
                
                if union > 0:
                    similarity_matrix[i, j] = intersection / union
        
        return similarity_matrix.tolist()
    
    def get_cross_domain_relationships(self) -> Dict[str, Any]:
        """
        Analyze relationships that span multiple domains.
        
        Returns:
            Dictionary with cross-domain relationship analysis
        """
        cross_domain_rels = self.domain_manager.get_cross_domain_relationships()
        
        if not cross_domain_rels:
            return {
                "count": 0,
                "domain_pairs": [],
                "strongest_connections": []
            }
        
        # Analyze domain pairs
        domain_pairs = defaultdict(list)
        for rel in cross_domain_rels:
            domains = rel["domains"]
            domains.sort()  # Ensure consistent ordering
            
            for i in range(len(domains)):
                for j in range(i+1, len(domains)):
                    pair = (domains[i], domains[j])
                    domain_pairs[pair].append(rel)
        
        # Calculate strength statistics for each domain pair
        pair_stats = []
        for pair, relationships in domain_pairs.items():
            strengths = [rel["strength"] for rel in relationships]
            
            pair_stats.append({
                "domain1": pair[0],
                "domain2": pair[1],
                "relationship_count": len(relationships),
                "avg_strength": sum(strengths) / len(strengths) if strengths else 0,
                "max_strength": max(strengths) if strengths else 0,
                "min_strength": min(strengths) if strengths else 0
            })
        
        # Sort by relationship count
        pair_stats.sort(key=lambda x: x["relationship_count"], reverse=True)
        
        # Get strongest connections
        strongest_connections = sorted(
            cross_domain_rels,
            key=lambda x: x["strength"],
            reverse=True
        )[:10]  # Top 10 strongest connections
        
        return {
            "count": len(cross_domain_rels),
            "domain_pairs": pair_stats,
            "strongest_connections": strongest_connections
        }
    
    def get_pattern_correlation_matrix(self) -> Dict[str, Any]:
        """
        Generate correlation matrix between pattern types across domains.
        
        Returns:
            Dictionary with correlation matrix data
        """
        domains = self.domain_manager.get_domains()
        if not domains:
            return {"correlation_matrix": []}
        
        # Get statistics for each domain
        domain_stats = self.domain_manager.get_domain_statistics()
        
        # Create dataframe for correlation calculation
        data = {
            "domain": [],
            "num_properties": [],
            "num_processes": [],
            "num_perspectives": [],
            "num_relationships": []
        }
        
        for domain, stats in domain_stats.items():
            data["domain"].append(domain)
            data["num_properties"].append(stats.get("num_properties", 0))
            data["num_processes"].append(stats.get("num_processes", 0))
            data["num_perspectives"].append(stats.get("num_perspectives", 0))
            data["num_relationships"].append(stats.get("num_relationships", 0))
        
        df = pd.DataFrame(data)
        
        # Calculate correlation matrix
        corr_columns = ["num_properties", "num_processes", "num_perspectives", "num_relationships"]
        correlation_matrix = df[corr_columns].corr().values.tolist()
        
        return {
            "features": corr_columns,
            "correlation_matrix": correlation_matrix
        }
    
    def get_common_patterns(self) -> Dict[str, Any]:
        """
        Find common patterns across domains.
        
        Returns:
            Dictionary with common pattern analysis
        """
        domains = self.domain_manager.get_domains()
        if not domains:
            return {"common_patterns": []}
        
        # Get all pattern names by type and domain
        all_pattern_names = {
            "property": defaultdict(list),
            "process": defaultdict(list),
            "perspective": defaultdict(list)
        }
        
        for domain in domains:
            patterns = self.domain_manager.get_patterns_by_domain(domain)
            for pattern_type, pattern_list in patterns.items():
                all_pattern_names[pattern_type][domain] = [p.name.lower() for p in pattern_list]
        
        # Find common names across domains for each pattern type
        common_patterns = {}
        
        for pattern_type, domain_patterns in all_pattern_names.items():
            # Count occurrences of each pattern name
            name_counts = Counter()
            for domain, names in domain_patterns.items():
                name_counts.update(names)
            
            # Get patterns that appear in multiple domains
            multi_domain_patterns = [
                {"name": name, "count": count}
                for name, count in name_counts.items()
                if count > 1
            ]
            
            # Sort by frequency
            multi_domain_patterns.sort(key=lambda x: x["count"], reverse=True)
            
            common_patterns[pattern_type] = multi_domain_patterns
        
        return {"common_patterns": common_patterns}
    
    def get_cross_domain_similarity(self) -> Dict[str, Any]:
        """
        Analyze similarity of pattern types across domains.
        
        Returns:
            Dictionary with similarity analysis
        """
        domains = list(self.domain_manager.get_domains())
        if not domains:
            return {"similarities": {}}
        
        similarities = {}
        
        for pattern_type in ["property", "process", "perspective"]:
            # Create domain x domain matrix for this pattern type
            n = len(domains)
            similarity_matrix = np.zeros((n, n))
            
            # Calculate similarity based on name overlap
            for i in range(n):
                for j in range(i, n):  # Only upper triangle (including diagonal)
                    domain_i = domains[i]
                    domain_j = domains[j]
                    
                    patterns_i = self.domain_manager.get_patterns_by_domain(domain_i)[pattern_type]
                    patterns_j = self.domain_manager.get_patterns_by_domain(domain_j)[pattern_type]
                    
                    names_i = set(p.name.lower() for p in patterns_i)
                    names_j = set(p.name.lower() for p in patterns_j)
                    
                    # Calculate Jaccard similarity
                    intersection = len(names_i.intersection(names_j))
                    union = len(names_i.union(names_j))
                    
                    similarity = intersection / union if union > 0 else 0
                    
                    # Fill both upper and lower triangle
                    similarity_matrix[i, j] = similarity
                    similarity_matrix[j, i] = similarity
            
            similarities[pattern_type] = {
                "domains": domains,
                "similarity_matrix": similarity_matrix.tolist()
            }
        
        return {"similarities": similarities}
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Run a full meta-analysis.
        
        Returns:
            Dictionary containing all meta-analysis results
        """
        return {
            "domain_comparison": self.get_domain_comparison(),
            "cross_domain_relationships": self.get_cross_domain_relationships(),
            "pattern_correlation": self.get_pattern_correlation_matrix(),
            "common_patterns": self.get_common_patterns(),
            "cross_domain_similarity": self.get_cross_domain_similarity()
        } 