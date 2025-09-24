#!/usr/bin/env python3
"""
P3IF Network Visualizations

Generates network graphs showing relationships between Properties, Processes, and Perspectives.
"""
import logging
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
from typing import Dict, Any
import pandas as pd

from p3if_methods.framework import P3IFFramework
from p3if_methods.models import Property, Process, Perspective

logger = logging.getLogger(__name__)


def generate_network_visualizations(small_framework: P3IFFramework,
                                  large_framework: P3IFFramework,
                                  session_path: Path):
    """Generate all network visualizations."""
    logger.info("🕸️ Generating network visualizations...")

    # Color scheme for P3IF components
    colors = {
        'property': '#FF6B6B',      # Red
        'process': '#4ECDC4',       # Cyan
        'perspective': '#45B7D1'    # Blue
    }

    # Generate general network graphs
    _create_general_network_graph(small_framework, session_path, "small_network", "Small P3IF Network", colors)
    _create_general_network_graph(large_framework, session_path, "large_network", "Large P3IF Network", colors)

    # Generate component-specific networks
    _create_component_specific_networks(small_framework, session_path, colors)
    _create_component_specific_networks(large_framework, session_path, colors)

    # Generate domain-specific networks
    _create_domain_specific_networks(small_framework, session_path, colors)
    _create_domain_specific_networks(large_framework, session_path, colors)


def _create_general_network_graph(framework: P3IFFramework,
                                session_path: Path,
                                filename: str,
                                title: str,
                                colors: Dict[str, str]):
    """Create a general network graph showing all P3IF components."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))

    # Create graph
    G = nx.Graph()

    # Add nodes
    for pattern_id, pattern in framework._patterns.items():
        G.add_node(pattern_id,
                  name=pattern.name,
                  type=pattern.type.value,
                  domain=pattern.domain)

    # Add edges based on relationships
    for rel_id, relationship in framework._relationships.items():
        connected_patterns = []

        if relationship.property_id:
            connected_patterns.append(relationship.property_id)
        if relationship.process_id:
            connected_patterns.append(relationship.process_id)
        if relationship.perspective_id:
            connected_patterns.append(relationship.perspective_id)

        # Connect patterns that are in relationships together
        for i in range(len(connected_patterns)):
            for j in range(i + 1, len(connected_patterns)):
                G.add_edge(connected_patterns[i], connected_patterns[j],
                          strength=relationship.strength,
                          confidence=relationship.confidence)

    if len(G.nodes()) == 0:
        ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
    else:
        # Layout
        if len(G.nodes()) < 30:
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        else:
            pos = nx.circular_layout(G)

        # Draw nodes by type
        for pattern_type in ['property', 'process', 'perspective']:
            nodes = [n for n, d in G.nodes(data=True) if d.get('type') == pattern_type]
            if nodes:
                nx.draw_networkx_nodes(G, pos, nodelist=nodes,
                                     node_color=colors[pattern_type],
                                     node_size=400, alpha=0.8, ax=ax)

        # Draw edges with varying width based on strength
        if G.edges():
            edges = G.edges(data=True)
            edge_widths = [d.get('strength', 1.0) * 2 for u, v, d in edges]
            nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, ax=ax)

        # Labels for small graphs
        if len(G.nodes()) <= 12:
            labels = {n: d['name'][:12] for n, d in G.nodes(data=True)}
            nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')

    # Legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['property'],
                  markersize=10, label='Properties'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['process'],
                  markersize=10, label='Processes'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['perspective'],
                  markersize=10, label='Perspectives')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()

    # Save
    networks_dir = session_path / "visualizations" / "networks"
    networks_dir.mkdir(parents=True, exist_ok=True)
    output_path = networks_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_component_specific_networks(framework: P3IFFramework,
                                       session_path: Path,
                                       colors: Dict[str, str]):
    """Create networks specific to each P3IF component type."""
    # Properties network
    _create_component_network(framework, session_path, "properties", "property",
                            "Properties Network", colors)

    # Processes network
    _create_component_network(framework, session_path, "processes", "process",
                            "Processes Network", colors)

    # Perspectives network
    _create_component_network(framework, session_path, "perspectives", "perspective",
                            "Perspectives Network", colors)


def _create_component_network(framework: P3IFFramework,
                            session_path: Path,
                            component_type: str,
                            pattern_type: str,
                            title: str,
                            colors: Dict[str, str]):
    """Create a network showing relationships for a specific component type."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    # Create graph with only the specified component type
    G = nx.Graph()

    # Add nodes of the specified type
    component_nodes = []
    for pattern_id, pattern in framework._patterns.items():
        if pattern.type.value == pattern_type:
            G.add_node(pattern_id,
                      name=pattern.name,
                      type=pattern.type.value,
                      domain=pattern.domain)
            component_nodes.append(pattern_id)

    # Add edges between components of this type if they're in relationships
    for rel_id, relationship in framework._relationships.items():
        connected_components = []

        if relationship.property_id and relationship.property_id in component_nodes:
            connected_components.append(relationship.property_id)
        if relationship.process_id and relationship.process_id in component_nodes:
            connected_components.append(relationship.process_id)
        if relationship.perspective_id and relationship.perspective_id in component_nodes:
            connected_components.append(relationship.perspective_id)

        # Connect components that are in the same relationship
        for i in range(len(connected_components)):
            for j in range(i + 1, len(connected_components)):
                G.add_edge(connected_components[i], connected_components[j],
                          strength=relationship.strength,
                          confidence=relationship.confidence)

    if len(G.nodes()) == 0:
        ax.text(0.5, 0.5, f'No {component_type}', ha='center', va='center', transform=ax.transAxes)
    else:
        # Layout
        if len(G.nodes()) < 20:
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        else:
            pos = nx.circular_layout(G)

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, nodelist=component_nodes,
                             node_color=colors[pattern_type],
                             node_size=500, alpha=0.8, ax=ax)

        # Draw edges
        if G.edges():
            edges = G.edges(data=True)
            edge_widths = [d.get('strength', 1.0) * 3 for u, v, d in edges]
            nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.6, ax=ax)

        # Labels
        labels = {n: d['name'][:15] for n, d in G.nodes(data=True)}
        nx.draw_networkx_labels(G, pos, labels, font_size=9, ax=ax)

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')

    plt.tight_layout()

    # Save
    networks_dir = session_path / "visualizations" / "networks"
    networks_dir.mkdir(parents=True, exist_ok=True)
    output_path = networks_dir / f"{component_type}_network.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_domain_specific_networks(framework: P3IFFramework,
                                   session_path: Path,
                                   colors: Dict[str, str]):
    """Create networks specific to each domain."""
    # Get unique domains
    domains = set(pattern.domain for pattern in framework._patterns.values())

    for domain in domains:
        _create_domain_network(framework, session_path, domain, colors)


def _create_domain_network(framework: P3IFFramework,
                         session_path: Path,
                         domain: str,
                         colors: Dict[str, str]):
    """Create a network showing relationships within a specific domain."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    # Create graph with only patterns from this domain
    G = nx.Graph()

    # Add nodes from this domain
    domain_nodes = []
    for pattern_id, pattern in framework._patterns.items():
        if pattern.domain == domain:
            G.add_node(pattern_id,
                      name=pattern.name,
                      type=pattern.type.value,
                      domain=pattern.domain)
            domain_nodes.append(pattern_id)

    # Add edges between domain patterns that are in relationships
    for rel_id, relationship in framework._relationships.items():
        connected_patterns = []

        if relationship.property_id and relationship.property_id in domain_nodes:
            connected_patterns.append(relationship.property_id)
        if relationship.process_id and relationship.process_id in domain_nodes:
            connected_patterns.append(relationship.process_id)
        if relationship.perspective_id and relationship.perspective_id in domain_nodes:
            connected_patterns.append(relationship.perspective_id)

        # Connect patterns that are in the same relationship
        for i in range(len(connected_patterns)):
            for j in range(i + 1, len(connected_patterns)):
                G.add_edge(connected_patterns[i], connected_patterns[j],
                          strength=relationship.strength,
                          confidence=relationship.confidence)

    if len(G.nodes()) == 0:
        ax.text(0.5, 0.5, f'No patterns in {domain}', ha='center', va='center', transform=ax.transAxes)
    else:
        # Layout
        if len(G.nodes()) < 15:
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        else:
            pos = nx.circular_layout(G)

        # Draw nodes by type
        for pattern_type in ['property', 'process', 'perspective']:
            nodes = [n for n, d in G.nodes(data=True) if d.get('type') == pattern_type]
            if nodes:
                nx.draw_networkx_nodes(G, pos, nodelist=nodes,
                                     node_color=colors[pattern_type],
                                     node_size=400, alpha=0.8, ax=ax)

        # Draw edges
        if G.edges():
            edges = G.edges(data=True)
            edge_widths = [d.get('strength', 1.0) * 2 for u, v, d in edges]
            nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, ax=ax)

        # Labels
        labels = {n: d['name'][:12] for n, d in G.nodes(data=True)}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)

    ax.set_title(f"{domain.title()} Domain Network", fontsize=14, fontweight='bold')
    ax.axis('off')

    plt.tight_layout()

    # Save
    networks_dir = session_path / "visualizations" / "networks"
    networks_dir.mkdir(parents=True, exist_ok=True)
    output_path = networks_dir / f"{domain.lower().replace(' ', '_')}_network.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")
