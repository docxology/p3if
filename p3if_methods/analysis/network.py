"""
P3IF Network Analyzer

This module provides network analysis capabilities for P3IF data.
"""
from typing import Dict, List, Any, Optional, Tuple, Set
import logging
import networkx as nx
import numpy as np
from collections import defaultdict

from p3if_methods.framework import P3IFFramework
from p3if_methods.models import BasePattern, Relationship


class NetworkAnalyzer:
    """Network analyzer for P3IF data."""
    
    def __init__(self, framework: P3IFFramework):
        """
        Initialize network analyzer.
        
        Args:
            framework: P3IF framework instance
        """
        self.framework = framework
        self.logger = logging.getLogger(__name__)
        self._graph = None
        self._graph_type = None
    
    def _build_graph(self, graph_type: str = "full") -> nx.Graph:
        """
        Build a NetworkX graph from the framework data.
        
        Args:
            graph_type: Type of graph to build (full, bipartite, or domain)
            
        Returns:
            NetworkX graph
        """
        self._graph_type = graph_type
        
        if graph_type == "full":
            # Create a full graph with all patterns as nodes
            G = nx.Graph()
            
            # Add all patterns as nodes
            for pattern_id, pattern in self.framework._patterns.items():
                G.add_node(
                    pattern_id, 
                    name=pattern.name, 
                    type=pattern.type,
                    domain=getattr(pattern, "domain", None)
                )
            
            # Add relationships as edges
            for rel_id, rel in self.framework._relationships.items():
                # Construct a list of the pattern IDs in this relationship
                patterns = []
                if rel.property_id:
                    patterns.append(rel.property_id)
                if rel.process_id:
                    patterns.append(rel.process_id)
                if rel.perspective_id:
                    patterns.append(rel.perspective_id)
                
                # Add edges between all pattern pairs
                for i in range(len(patterns)):
                    for j in range(i+1, len(patterns)):
                        G.add_edge(
                            patterns[i], 
                            patterns[j], 
                            weight=rel.strength,
                            relationship_id=rel_id
                        )
        
        elif graph_type == "bipartite":
            # Create a bipartite graph with patterns and relationships as nodes
            G = nx.Graph()
            
            # Add patterns as nodes in one set
            for pattern_id, pattern in self.framework._patterns.items():
                G.add_node(
                    pattern_id, 
                    name=pattern.name, 
                    type=pattern.type,
                    domain=getattr(pattern, "domain", None),
                    bipartite=0  # Patterns are in set 0
                )
            
            # Add relationships as nodes in the other set
            for rel_id, rel in self.framework._relationships.items():
                G.add_node(
                    f"rel_{rel_id}", 
                    strength=rel.strength,
                    bipartite=1  # Relationships are in set 1
                )
                
                # Connect the relationship to its patterns
                if rel.property_id:
                    G.add_edge(f"rel_{rel_id}", rel.property_id)
                if rel.process_id:
                    G.add_edge(f"rel_{rel_id}", rel.process_id)
                if rel.perspective_id:
                    G.add_edge(f"rel_{rel_id}", rel.perspective_id)
        
        elif graph_type == "domain":
            # Create a graph with domains as nodes
            G = nx.Graph()
            
            # Get all domains
            domains = set()
            for pattern in self.framework._patterns.values():
                domain = getattr(pattern, "domain", None)
                if domain:
                    domains.add(domain)
            
            # Add domains as nodes
            for domain in domains:
                G.add_node(domain, type="domain")
            
            # Add edges between domains that share relationships
            domain_connections = defaultdict(float)
            for rel in self.framework._relationships.values():
                rel_domains = set()
                
                for pattern_id in [rel.property_id, rel.process_id, rel.perspective_id]:
                    if pattern_id:
                        pattern = self.framework.get_pattern(pattern_id)
                        if pattern and hasattr(pattern, "domain") and pattern.domain:
                            rel_domains.add(pattern.domain)
                
                # Add connections between all domain pairs
                domains_list = list(rel_domains)
                for i in range(len(domains_list)):
                    for j in range(i+1, len(domains_list)):
                        domain_pair = tuple(sorted([domains_list[i], domains_list[j]]))
                        domain_connections[domain_pair] += rel.strength
            
            # Add edges to the graph
            for (domain1, domain2), strength in domain_connections.items():
                G.add_edge(domain1, domain2, weight=strength)
                
        else:
            raise ValueError(f"Unknown graph type: {graph_type}")
        
        self._graph = G
        return G
    
    def get_graph(self, graph_type: str = "full") -> nx.Graph:
        """
        Get a NetworkX graph representing the framework data.
        
        Args:
            graph_type: Type of graph to get
            
        Returns:
            NetworkX graph
        """
        if self._graph is None or self._graph_type != graph_type:
            return self._build_graph(graph_type)
        return self._graph
    
    def get_network_statistics(self, graph_type: str = "full") -> Dict[str, Any]:
        """
        Get statistics about the network.
        
        Args:
            graph_type: Type of graph to analyze
            
        Returns:
            Dictionary of network statistics
        """
        G = self.get_graph(graph_type)
        
        stats = {
            "num_nodes": G.number_of_nodes(),
            "num_edges": G.number_of_edges(),
            "density": nx.density(G),
            "avg_degree": sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0
        }
        
        # Calculate connected components
        components = list(nx.connected_components(G))
        stats["num_components"] = len(components)
        stats["largest_component_size"] = len(max(components, key=len)) if components else 0
        
        # Calculate clustering coefficient (only for non-bipartite graphs)
        if graph_type != "bipartite":
            try:
                stats["avg_clustering"] = nx.average_clustering(G)
            except:
                stats["avg_clustering"] = 0
        
        # Calculate diameter and average path length for the largest component
        if components:
            largest_component = max(components, key=len)
            largest_subgraph = G.subgraph(largest_component)
            
            try:
                stats["diameter"] = nx.diameter(largest_subgraph)
                stats["avg_path_length"] = nx.average_shortest_path_length(largest_subgraph)
            except:
                stats["diameter"] = 0
                stats["avg_path_length"] = 0
        else:
            stats["diameter"] = 0
            stats["avg_path_length"] = 0
        
        return stats
    
    def get_centrality_measures(self, graph_type: str = "full", top_n: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get centrality measures for nodes in the network.
        
        Args:
            graph_type: Type of graph to analyze
            top_n: Number of top nodes to return for each measure
            
        Returns:
            Dictionary mapping centrality measures to lists of node details
        """
        G = self.get_graph(graph_type)
        
        # Calculate centrality measures
        centrality_functions = {
            "degree": nx.degree_centrality,
            "betweenness": nx.betweenness_centrality,
            "closeness": nx.closeness_centrality,
            "eigenvector": nx.eigenvector_centrality_numpy
        }
        
        result = {}
        for measure_name, measure_func in centrality_functions.items():
            try:
                centrality = measure_func(G)
                
                # Sort nodes by centrality value
                sorted_nodes = sorted(
                    centrality.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # Get top N nodes
                top_nodes = []
                for node_id, value in sorted_nodes[:top_n]:
                    node_info = {"id": node_id, "value": value}
                    
                    # Add node attributes
                    if graph_type == "full" or (graph_type == "bipartite" and not str(node_id).startswith("rel_")):
                        # This is a pattern node
                        pattern = self.framework.get_pattern(node_id)
                        if pattern:
                            node_info.update({
                                "name": pattern.name,
                                "type": pattern.type,
                                "domain": getattr(pattern, "domain", None)
                            })
                    elif graph_type == "domain":
                        node_info["name"] = node_id
                    
                    top_nodes.append(node_info)
                
                result[measure_name] = top_nodes
            except Exception as e:
                self.logger.warning(f"Failed to calculate {measure_name} centrality: {e}")
                result[measure_name] = []
        
        return result
    
    def get_communities(self, graph_type: str = "full", algorithm: str = "louvain") -> Dict[str, Any]:
        """
        Detect communities in the network.
        
        Args:
            graph_type: Type of graph to analyze
            algorithm: Community detection algorithm to use (louvain, girvan_newman, label_propagation)
            
        Returns:
            Dictionary with community detection results
        """
        G = self.get_graph(graph_type)
        
        communities = []
        algorithm_info = {"name": algorithm}
        
        try:
            if algorithm == "louvain":
                try:
                    from community import best_partition
                    partition = best_partition(G)
                    
                    # Group nodes by community
                    community_groups = defaultdict(list)
                    for node, community_id in partition.items():
                        community_groups[community_id].append(node)
                    
                    communities = list(community_groups.values())
                    algorithm_info["modularity"] = self._calculate_modularity(G, communities)
                    
                except ImportError:
                    self.logger.warning("Failed to import 'community' module. Using label propagation instead.")
                    algorithm = "label_propagation"
            
            if algorithm == "girvan_newman":
                # Use Girvan-Newman algorithm (returns generator of communities)
                comp = nx.community.girvan_newman(G)
                
                # Get communities with the highest modularity
                best_communities = None
                best_modularity = -1
                
                # Check the first few iterations for best modularity
                for i, iteration in enumerate(comp):
                    if i >= 10:  # Limit the number of iterations to check
                        break
                    
                    iter_communities = list(iteration)
                    modularity = self._calculate_modularity(G, iter_communities)
                    
                    if modularity > best_modularity:
                        best_modularity = modularity
                        best_communities = iter_communities
                
                if best_communities:
                    communities = best_communities
                    algorithm_info["modularity"] = best_modularity
            
            if algorithm == "label_propagation":
                # Use Label Propagation algorithm
                comp = nx.community.label_propagation_communities(G)
                communities = list(comp)
                algorithm_info["modularity"] = self._calculate_modularity(G, communities)
        
        except Exception as e:
            self.logger.error(f"Error detecting communities: {e}")
            communities = []
        
        # Convert communities to a suitable format
        formatted_communities = []
        for i, community in enumerate(communities):
            community_nodes = []
            for node_id in community:
                node_info = {"id": node_id}
                
                # Add node attributes
                if graph_type == "full" or (graph_type == "bipartite" and not str(node_id).startswith("rel_")):
                    # This is a pattern node
                    pattern = self.framework.get_pattern(node_id)
                    if pattern:
                        node_info.update({
                            "name": pattern.name,
                            "type": pattern.type,
                            "domain": getattr(pattern, "domain", None)
                        })
                elif graph_type == "domain":
                    node_info["name"] = node_id
                
                community_nodes.append(node_info)
            
            formatted_communities.append({
                "id": i,
                "size": len(community),
                "nodes": community_nodes
            })
        
        # Sort communities by size
        formatted_communities.sort(key=lambda c: c["size"], reverse=True)
        
        return {
            "algorithm": algorithm_info,
            "count": len(formatted_communities),
            "communities": formatted_communities
        }
    
    def _calculate_modularity(self, G: nx.Graph, communities: List[Set]) -> float:
        """
        Calculate modularity of a network partition.
        
        Args:
            G: NetworkX graph
            communities: List of sets of nodes representing communities
            
        Returns:
            Modularity value
        """
        try:
            return nx.community.modularity(G, communities)
        except:
            # Fall back to manual calculation if NetworkX function fails
            m = G.number_of_edges()
            if m == 0:
                return 0
                
            modularity = 0
            for community in communities:
                for i in community:
                    for j in community:
                        if i != j:
                            if G.has_edge(i, j):
                                modularity += 1
                            
                            ki = G.degree(i)
                            kj = G.degree(j)
                            modularity -= ki * kj / (2 * m)
            
            return modularity / (2 * m)
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Run a full network analysis.
        
        Returns:
            Dictionary containing all analysis results
        """
        return {
            "statistics": {
                "full": self.get_network_statistics("full"),
                "domain": self.get_network_statistics("domain")
            },
            "centrality": {
                "full": self.get_centrality_measures("full"),
                "domain": self.get_centrality_measures("domain")
            },
            "communities": {
                "full": self.get_communities("full"),
                "domain": self.get_communities("domain")
            }
        } 