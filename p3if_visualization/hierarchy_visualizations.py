#!/usr/bin/env python3
"""
P3IF Hierarchical Visualizations

Generates hierarchical structure diagrams showing the organization of
Properties, Processes, and Perspectives in tree and organizational chart formats.
"""
import logging
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
import networkx as nx
from pathlib import Path
from typing import Dict, Any
import numpy as np

from p3if_methods.framework import P3IFFramework
from p3if_methods.models import Property, Process, Perspective

logger = logging.getLogger(__name__)


def generate_hierarchical_visualizations(small_framework: P3IFFramework,
                                      large_framework: P3IFFramework,
                                      session_path: Path):
    """Generate all hierarchical visualizations."""
    logger.info("🌳 Generating hierarchical visualizations...")

    # Color scheme for P3IF components
    colors = {
        'property': '#FF6B6B',      # Red
        'process': '#4ECDC4',       # Cyan
        'perspective': '#45B7D1'    # Blue
    }

    # Generate P3IF hierarchy diagrams
    _create_p3if_hierarchy(small_framework, session_path, "small_p3if_hierarchy",
                          "Small Dataset - P3IF Hierarchy", colors)
    _create_p3if_hierarchy(large_framework, session_path, "large_p3if_hierarchy",
                          "Large Dataset - P3IF Hierarchy", colors)

    # Generate domain hierarchies
    _create_domain_hierarchy(small_framework, session_path, "small_domain_hierarchy",
                            "Small Dataset - Domain Hierarchy", colors)
    _create_domain_hierarchy(large_framework, session_path, "large_domain_hierarchy",
                            "Large Dataset - Domain Hierarchy", colors)

    # Generate component type hierarchies
    _create_component_type_hierarchy(small_framework, session_path, "small_component_hierarchy",
                                   "Small Dataset - Component Type Hierarchy", colors)
    _create_component_type_hierarchy(large_framework, session_path, "large_component_hierarchy",
                                   "Large Dataset - Component Type Hierarchy", colors)

    # Generate relationship hierarchies
    _create_relationship_hierarchy(small_framework, session_path, "small_relationship_hierarchy",
                                  "Small Dataset - Relationship Hierarchy", colors)
    _create_relationship_hierarchy(large_framework, session_path, "large_relationship_hierarchy",
                                  "Large Dataset - Relationship Hierarchy", colors)


def _create_p3if_hierarchy(framework: P3IFFramework,
                         session_path: Path,
                         filename: str,
                         title: str,
                         colors: Dict[str, str]):
    """Create a hierarchical visualization of the P3IF framework."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))

    # Get patterns by type
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    # Create P3IF tree structure
    _draw_p3if_tree(ax1, properties, processes, perspectives, colors)
    ax1.set_title('P3IF Component Tree', fontsize=12, fontweight='bold')

    # Create domain organization chart
    _draw_domain_org_chart(ax2, framework, colors)
    ax2.set_title('Domain Organization', fontsize=12, fontweight='bold')

    # Create relationship dependency tree
    _draw_relationship_tree(ax3, framework, colors)
    ax3.set_title('Relationship Dependencies', fontsize=12, fontweight='bold')

    # Create comprehensive summary
    _draw_hierarchy_summary(ax4, properties, processes, perspectives, framework, colors)
    ax4.set_title('Hierarchy Summary', fontsize=12, fontweight='bold')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    hierarchies_dir = session_path / "visualizations" / "hierarchies"
    hierarchies_dir.mkdir(parents=True, exist_ok=True)
    output_path = hierarchies_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _draw_p3if_tree(ax, properties: list, processes: list, perspectives: list, colors: Dict[str, str]):
    """Draw a tree structure showing P3IF component organization."""
    ax.axis('off')

    # Remove axes
    ax.set_xlim(-1, 3)
    ax.set_ylim(-1, 2)

    # Draw P3IF root
    ax.add_patch(Circle((0.5, 1.5), 0.15, color='black', alpha=0.8))
    ax.text(0.5, 1.5, 'P3IF', ha='center', va='center', fontweight='bold', color='white', fontsize=10)

    # Properties branch
    ax.add_patch(Rectangle((0.2, 1.0), 0.6, 0.2, color=colors['property'], alpha=0.8))
    ax.text(0.5, 1.1, f'Properties ({len(properties)})', ha='center', va='center', fontweight='bold')

    # Processes branch
    ax.add_patch(Rectangle((0.2, 0.6), 0.6, 0.2, color=colors['process'], alpha=0.8))
    ax.text(0.5, 0.7, f'Processes ({len(processes)})', ha='center', va='center', fontweight='bold')

    # Perspectives branch
    ax.add_patch(Rectangle((0.2, 0.2), 0.6, 0.2, color=colors['perspective'], alpha=0.8))
    ax.text(0.5, 0.3, f'Perspectives ({len(perspectives)})', ha='center', va='center', fontweight='bold')

    # Draw connecting lines
    ax.plot([0.5, 0.5], [1.35, 1.05], 'k-', alpha=0.6, linewidth=2)  # To Properties
    ax.plot([0.5, 0.5], [1.35, 0.65], 'k-', alpha=0.6, linewidth=2)  # To Processes
    ax.plot([0.5, 0.5], [1.35, 0.25], 'k-', alpha=0.6, linewidth=2)  # To Perspectives

    # Add property details
    y_pos = 0.9
    for i, prop in enumerate(properties[:3]):  # Show first 3 properties
        ax.add_patch(FancyBboxPatch((1.0, y_pos - 0.05), 0.8, 0.08,
                                  boxstyle="round,pad=0.02", facecolor=colors['property'], alpha=0.6))
        ax.text(1.4, y_pos, prop.name[:15], fontsize=8, ha='center', va='center')
        y_pos -= 0.1

    # Add process details
    y_pos = 0.6
    for i, proc in enumerate(processes[:3]):  # Show first 3 processes
        ax.add_patch(FancyBboxPatch((1.0, y_pos - 0.05), 0.8, 0.08,
                                  boxstyle="round,pad=0.02", facecolor=colors['process'], alpha=0.6))
        ax.text(1.4, y_pos, proc.name[:15], fontsize=8, ha='center', va='center')
        y_pos -= 0.1

    # Add perspective details
    y_pos = 0.2
    for i, persp in enumerate(perspectives[:3]):  # Show first 3 perspectives
        ax.add_patch(FancyBboxPatch((1.0, y_pos - 0.05), 0.8, 0.08,
                                  boxstyle="round,pad=0.02", facecolor=colors['perspective'], alpha=0.6))
        ax.text(1.4, y_pos, persp.name[:15], fontsize=8, ha='center', va='center')
        y_pos -= 0.1


def _draw_domain_org_chart(ax, framework: P3IFFramework, colors: Dict[str, str]):
    """Draw an organizational chart showing domain structure."""
    ax.axis('off')

    # Get unique domains
    domains = list(set(p.domain for p in framework._patterns.values()))

    if not domains:
        ax.text(0.5, 0.5, 'No domains found', ha='center', va='center', transform=ax.transAxes)
        return

    # Position domains
    n_domains = len(domains)
    y_spacing = 0.8 / max(n_domains, 1)

    for i, domain in enumerate(domains):
        y_pos = 0.8 - i * y_spacing

        # Domain header
        ax.add_patch(Rectangle((0.1, y_pos), 0.8, 0.1, color='lightgray', alpha=0.8))
        ax.text(0.5, y_pos + 0.05, domain, ha='center', va='center', fontweight='bold')

        # Get patterns in this domain
        domain_properties = [p for p in framework._patterns.values()
                           if p.domain == domain and isinstance(p, Property)]
        domain_processes = [p for p in framework._patterns.values()
                          if p.domain == domain and isinstance(p, Process)]
        domain_perspectives = [p for p in framework._patterns.values()
                             if p.domain == domain and isinstance(p, Perspective)]

        # Add pattern counts
        x_pos = 0.15
        if domain_properties:
            ax.add_patch(Circle((x_pos, y_pos - 0.05), 0.03, color=colors['property'], alpha=0.8))
            ax.text(x_pos + 0.05, y_pos - 0.05, f"P: {len(domain_properties)}",
                   fontsize=8, ha='left', va='center')

        x_pos = 0.4
        if domain_processes:
            ax.add_patch(Circle((x_pos, y_pos - 0.05), 0.03, color=colors['process'], alpha=0.8))
            ax.text(x_pos + 0.05, y_pos - 0.05, f"Proc: {len(domain_processes)}",
                   fontsize=8, ha='left', va='center')

        x_pos = 0.7
        if domain_perspectives:
            ax.add_patch(Circle((x_pos, y_pos - 0.05), 0.03, color=colors['perspective'], alpha=0.8))
            ax.text(x_pos + 0.05, y_pos - 0.05, f"Persp: {len(domain_perspectives)}",
                   fontsize=8, ha='left', va='center')


def _draw_relationship_tree(ax, framework: P3IFFramework, colors: Dict[str, str]):
    """Draw a tree showing relationship dependencies."""
    ax.axis('off')

    # Create graph for relationships
    G = nx.DiGraph()

    # Add relationship nodes
    for i, rel in enumerate(framework._relationships.values()):
        rel_id = f"R{i}"
        G.add_node(rel_id, strength=rel.strength, confidence=rel.confidence)

        # Connect to related patterns
        connected_patterns = []

        if rel.property_id:
            prop_name = next((p.name for p in framework._patterns.values()
                            if p.id == rel.property_id and isinstance(p, Property)), "Unknown")
            connected_patterns.append(f"P: {prop_name[:10]}")

        if rel.process_id:
            proc_name = next((p.name for p in framework._patterns.values()
                            if p.id == rel.process_id and isinstance(p, Process)), "Unknown")
            connected_patterns.append(f"Proc: {proc_name[:10]}")

        if rel.perspective_id:
            persp_name = next((p.name for p in framework._patterns.values()
                             if p.id == rel.perspective_id and isinstance(p, Perspective)), "Unknown")
            connected_patterns.append(f"Persp: {persp_name[:10]}")

        for pattern in connected_patterns:
            G.add_edge(rel_id, pattern)

    if len(G.nodes()) == 0:
        ax.text(0.5, 0.5, 'No relationships', ha='center', va='center', transform=ax.transAxes)
        return

    # Position nodes
    pos = nx.spring_layout(G, seed=42)

    # Draw nodes by type
    rel_nodes = [n for n in G.nodes() if n.startswith('R')]
    prop_nodes = [n for n in G.nodes() if n.startswith('P:')]
    proc_nodes = [n for n in G.nodes() if n.startswith('Proc:')]
    persp_nodes = [n for n in G.nodes() if n.startswith('Persp:')]

    if rel_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=rel_nodes, node_color='lightgray',
                             node_shape='s', node_size=200, ax=ax)

    if prop_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=prop_nodes, node_color=colors['property'],
                             node_size=150, alpha=0.8, ax=ax)

    if proc_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=proc_nodes, node_color=colors['process'],
                             node_size=150, alpha=0.8, ax=ax)

    if persp_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=persp_nodes, node_color=colors['perspective'],
                             node_size=150, alpha=0.8, ax=ax)

    # Draw edges
    if G.edges():
        nx.draw_networkx_edges(G, pos, alpha=0.5, arrows=True, arrowsize=10, ax=ax)

    # Labels
    labels = {n: n for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)


def _draw_hierarchy_summary(ax, properties: list, processes: list, perspectives: list,
                           framework: P3IFFramework, colors: Dict[str, str]):
    """Draw a comprehensive summary of the hierarchy."""
    ax.axis('off')

    # Calculate statistics
    total_patterns = len(properties) + len(processes) + len(perspectives)
    total_relationships = len(framework._relationships)

    # Create summary boxes
    summary_data = [
        ('Total Components', str(total_patterns), 'lightblue'),
        ('Properties', str(len(properties)), colors['property']),
        ('Processes', str(len(processes)), colors['process']),
        ('Perspectives', str(len(perspectives)), colors['perspective']),
        ('Relationships', str(total_relationships), 'lightgreen'),
    ]

    y_pos = 0.8
    for label, value, color in summary_data:
        ax.add_patch(FancyBboxPatch((0.1, y_pos), 0.8, 0.15,
                                  boxstyle="round,pad=0.02", facecolor=color, alpha=0.8))
        ax.text(0.2, y_pos + 0.07, label, fontsize=10, fontweight='bold')
        ax.text(0.7, y_pos + 0.07, value, fontsize=12, fontweight='bold', ha='right')
        y_pos -= 0.2

    # Add hierarchy description
    description = """
    P3IF Framework Hierarchy:

    • Properties (P): Data attributes and characteristics
      Define what data is captured and how it's structured

    • Processes (P): Actions, workflows, and procedures
      Define how work is performed and data flows

    • Perspectives (P): Viewpoints, contexts, and frameworks
      Define how information is interpreted and used

    • Relationships: Connections between P, P, P components
      Define how components interact and influence each other

    Together they form the comprehensive P3IF framework
    for modeling complex systems and their interactions.
    """

    ax.text(0.1, 0.1, description, fontsize=9, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))


def _create_domain_hierarchy(framework: P3IFFramework,
                           session_path: Path,
                           filename: str,
                           title: str,
                           colors: Dict[str, str]):
    """Create a hierarchical visualization organized by domains."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.axis('off')

    # Get unique domains
    domains = list(set(p.domain for p in framework._patterns.values()))

    if not domains:
        ax.text(0.5, 0.5, 'No domains found', ha='center', va='center', transform=ax.transAxes)
        return

    # Position domains vertically
    n_domains = len(domains)
    y_spacing = 0.9 / max(n_domains, 1)

    for i, domain in enumerate(domains):
        y_pos = 0.9 - i * y_spacing

        # Domain header
        ax.add_patch(Rectangle((0.05, y_pos), 0.9, 0.15, color='lightgray', alpha=0.8, linewidth=2))
        ax.text(0.5, y_pos + 0.075, domain, ha='center', va='center', fontweight='bold', fontsize=12)

        # Get patterns in this domain
        domain_properties = [p for p in framework._patterns.values()
                           if p.domain == domain and isinstance(p, Property)]
        domain_processes = [p for p in framework._patterns.values()
                          if p.domain == domain and isinstance(p, Process)]
        domain_perspectives = [p for p in framework._patterns.values()
                             if p.domain == domain and isinstance(p, Perspective)]

        # Add component counts
        x_pos = 0.1
        if domain_properties:
            ax.add_patch(Circle((x_pos, y_pos - 0.03), 0.02, color=colors['property'], alpha=0.9))
            ax.text(x_pos + 0.03, y_pos - 0.03, f"Properties: {len(domain_properties)}",
                   fontsize=9, ha='left', va='center')

        x_pos = 0.4
        if domain_processes:
            ax.add_patch(Circle((x_pos, y_pos - 0.03), 0.02, color=colors['process'], alpha=0.9))
            ax.text(x_pos + 0.03, y_pos - 0.03, f"Processes: {len(domain_processes)}",
                   fontsize=9, ha='left', va='center')

        x_pos = 0.7
        if domain_perspectives:
            ax.add_patch(Circle((x_pos, y_pos - 0.03), 0.02, color=colors['perspective'], alpha=0.9))
            ax.text(x_pos + 0.03, y_pos - 0.03, f"Perspectives: {len(domain_perspectives)}",
                   fontsize=9, ha='left', va='center')

        # Add pattern names (first few)
        pattern_y = y_pos - 0.08
        patterns_added = 0

        for prop in domain_properties[:2]:  # First 2 properties
            ax.add_patch(FancyBboxPatch((0.1, pattern_y), 0.25, 0.04,
                                      boxstyle="round,pad=0.01", facecolor=colors['property'], alpha=0.7))
            ax.text(0.225, pattern_y + 0.02, prop.name[:12], fontsize=7, ha='center', va='center')
            pattern_y -= 0.05
            patterns_added += 1

        pattern_y = y_pos - 0.08
        for proc in domain_processes[:2]:  # First 2 processes
            ax.add_patch(FancyBboxPatch((0.4, pattern_y), 0.25, 0.04,
                                      boxstyle="round,pad=0.01", facecolor=colors['process'], alpha=0.7))
            ax.text(0.525, pattern_y + 0.02, proc.name[:12], fontsize=7, ha='center', va='center')
            pattern_y -= 0.05
            patterns_added += 1

        pattern_y = y_pos - 0.08
        for persp in domain_perspectives[:2]:  # First 2 perspectives
            ax.add_patch(FancyBboxPatch((0.7, pattern_y), 0.25, 0.04,
                                      boxstyle="round,pad=0.01", facecolor=colors['perspective'], alpha=0.7))
            ax.text(0.825, pattern_y + 0.02, persp.name[:12], fontsize=7, ha='center', va='center')
            pattern_y -= 0.05
            patterns_added += 1

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()

    # Save
    hierarchies_dir = session_path / "visualizations" / "hierarchies"
    hierarchies_dir.mkdir(parents=True, exist_ok=True)
    output_path = hierarchies_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_component_type_hierarchy(framework: P3IFFramework,
                                   session_path: Path,
                                   filename: str,
                                   title: str,
                                   colors: Dict[str, str]):
    """Create a hierarchy based on component types."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.axis('off')

    # Get patterns by type
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    # Create hierarchy levels
    levels = [
        ('Framework Level', 'P3IF Framework', 0.8),
        ('Component Types', f'Properties ({len(properties)}), Processes ({len(processes)}), Perspectives ({len(perspectives)})', 0.6),
        ('Individual Components', f'Total: {len(properties + processes + perspectives)} components', 0.4)
    ]

    for level_name, level_desc, y_pos in levels:
        # Level header
        ax.add_patch(Rectangle((0.1, y_pos), 0.8, 0.1, color='lightblue', alpha=0.8))
        ax.text(0.5, y_pos + 0.05, f"{level_name}: {level_desc}",
               ha='center', va='center', fontweight='bold')

    # Add component type details
    y_pos = 0.3
    for comp_type, comp_list, color in [('Properties', properties, colors['property']),
                                       ('Processes', processes, colors['process']),
                                       ('Perspectives', perspectives, colors['perspective'])]:

        ax.add_patch(Rectangle((0.1, y_pos), 0.8, 0.08, color=color, alpha=0.8))
        ax.text(0.5, y_pos + 0.04, f"{comp_type} ({len(comp_list)})",
               ha='center', va='center', fontweight='bold')

        # Add individual component names
        comp_y = y_pos - 0.06
        for i, comp in enumerate(comp_list[:3]):  # Show first 3
            ax.add_patch(FancyBboxPatch((0.15 + i * 0.25, comp_y), 0.2, 0.04,
                                      boxstyle="round,pad=0.01", facecolor=color, alpha=0.6))
            ax.text(0.25 + i * 0.25, comp_y + 0.02, comp.name[:10],
                   fontsize=7, ha='center', va='center')

        y_pos -= 0.15

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()

    # Save
    hierarchies_dir = session_path / "visualizations" / "hierarchies"
    hierarchies_dir.mkdir(parents=True, exist_ok=True)
    output_path = hierarchies_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_relationship_hierarchy(framework: P3IFFramework,
                                 session_path: Path,
                                 filename: str,
                                 title: str,
                                 colors: Dict[str, str]):
    """Create a hierarchy showing relationship organization."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # Relationship count by strength
    strengths = [float(rel.strength) if hasattr(rel.strength, '__float__') else 0.5
                for rel in framework._relationships.values()]

    ax1.hist(strengths, bins=10, alpha=0.7, color='lightcoral')
    ax1.set_title('Relationship Strength Distribution')
    ax1.set_xlabel('Strength')
    ax1.set_ylabel('Count')

    # Relationship types
    rel_types = {}
    for rel in framework._relationships.values():
        rel_type = getattr(rel, 'relationship_type', 'general')
        rel_types[rel_type] = rel_types.get(rel_type, 0) + 1

    if rel_types:
        ax2.bar(rel_types.keys(), rel_types.values(), alpha=0.7, color='lightblue')
        ax2.set_title('Relationship Types')
        ax2.set_xlabel('Type')
        ax2.set_ylabel('Count')
        ax2.tick_params(axis='x', rotation=45)

    # Confidence distribution
    confidences = [float(rel.confidence) if hasattr(rel.confidence, '__float__') else 1.0
                  for rel in framework._relationships.values()]

    ax3.hist(confidences, bins=10, alpha=0.7, color='lightgreen')
    ax3.set_title('Relationship Confidence Distribution')
    ax3.set_xlabel('Confidence')
    ax3.set_ylabel('Count')

    # Relationship summary
    ax4.axis('off')
    summary_text = f"""
    Relationship Hierarchy Summary:

    Total Relationships: {len(framework._relationships)}

    Strength Statistics:
    • Average: {np.mean(strengths)".2f"}
    • Min: {min(strengths)".2f"}
    • Max: {max(strengths)".2f"}

    Confidence Statistics:
    • Average: {np.mean(confidences)".2f"}
    • Min: {min(confidences)".2f"}
    • Max: {max(confidences)".2f"}

    Relationship Types: {len(rel_types)}
    """

    ax4.text(0.1, 0.8, summary_text, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    ax4.set_title('Relationship Summary')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    hierarchies_dir = session_path / "visualizations" / "hierarchies"
    hierarchies_dir.mkdir(parents=True, exist_ok=True)
    output_path = hierarchies_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")
