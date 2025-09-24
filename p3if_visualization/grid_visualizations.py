#!/usr/bin/env python3
"""
P3IF 2D Grid Visualizations

Generates 2D grid visualizations showing combinations of Properties, Processes, and Perspectives
with proper P3IF labeling and data integration.
"""
import logging
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from pathlib import Path
from typing import Dict, Any
import itertools

from p3if_methods.framework import P3IFFramework
from p3if_methods.models import Property, Process, Perspective

logger = logging.getLogger(__name__)


def generate_grid_visualizations(small_framework: P3IFFramework,
                               large_framework: P3IFFramework,
                               session_path: Path):
    """Generate all grid visualizations."""
    logger.info("🔲 Generating grid visualizations...")

    # Color scheme for P3IF components
    colors = {
        'property': '#FF6B6B',      # Red
        'process': '#4ECDC4',       # Cyan
        'perspective': '#45B7D1'    # Blue
    }

    # Generate P3IF component grid
    _create_p3if_component_grid(small_framework, session_path, "small_p3if_grid",
                               "Small Dataset - P3IF Component Grid", colors)
    _create_p3if_component_grid(large_framework, session_path, "large_p3if_grid",
                               "Large Dataset - P3IF Component Grid", colors)

    # Generate relationship grid
    _create_relationship_grid(small_framework, session_path, "small_relationship_grid",
                             "Small Dataset - Relationship Grid", colors)
    _create_relationship_grid(large_framework, session_path, "large_relationship_grid",
                             "Large Dataset - Relationship Grid", colors)

    # Generate domain grid
    _create_domain_grid(small_framework, session_path, "small_domain_grid",
                       "Small Dataset - Domain Grid", colors)
    _create_domain_grid(large_framework, session_path, "large_domain_grid",
                       "Large Dataset - Domain Grid", colors)

    # Generate comprehensive P3IF matrix
    _create_comprehensive_p3if_matrix(small_framework, large_framework, session_path,
                                    "comprehensive_p3if_matrix", "Comprehensive P3IF Matrix", colors)


def _create_p3if_component_grid(framework: P3IFFramework,
                              session_path: Path,
                              filename: str,
                              title: str,
                              colors: Dict[str, str]):
    """Create a 2D grid showing all P3IF components organized by type."""
    # Get components by type
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    # Determine grid dimensions
    n_props = len(properties)
    n_procs = len(processes)
    n_persps = len(perspectives)

    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))

    # Main grid
    ax_main = plt.subplot2grid((3, 3), (0, 0), colspan=2, rowspan=2)

    # Properties vs Processes grid
    ax_prop_proc = plt.subplot2grid((3, 3), (0, 2))

    # Processes vs Perspectives grid
    ax_proc_persp = plt.subplot2grid((3, 3), (1, 2))

    # Properties vs Perspectives grid
    ax_prop_persp = plt.subplot2grid((3, 3), (2, 0), colspan=2)

    # Summary statistics
    ax_summary = plt.subplot2grid((3, 3), (2, 2))

    # Create main P3IF grid
    _draw_main_p3if_grid(ax_main, properties, processes, perspectives, colors)

    # Create component pair grids
    _draw_component_pair_grid(ax_prop_proc, properties, processes, "Properties", "Processes",
                             colors['property'], colors['process'])
    _draw_component_pair_grid(ax_proc_persp, processes, perspectives, "Processes", "Perspectives",
                             colors['process'], colors['perspective'])
    _draw_component_pair_grid(ax_prop_persp, properties, perspectives, "Properties", "Perspectives",
                             colors['property'], colors['perspective'])

    # Add summary
    _add_grid_summary(ax_summary, framework, colors)

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    grids_dir = session_path / "visualizations" / "grids"
    grids_dir.mkdir(parents=True, exist_ok=True)
    output_path = grids_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _draw_main_p3if_grid(ax, properties: list, processes: list, perspectives: list, colors: Dict[str, str]):
    """Draw the main P3IF component grid."""
    ax.axis('off')

    # Draw title
    ax.text(0.5, 0.95, 'P3IF Component Grid', ha='center', va='center',
           fontweight='bold', fontsize=14)

    # Calculate positions
    margin = 0.1
    cell_width = (1 - 2*margin) / 3
    cell_height = (0.8 - margin) / 3

    # Draw component sections
    sections = [
        ('Properties (P)', properties, colors['property'], 0),
        ('Processes (P)', processes, colors['process'], 1),
        ('Perspectives (P)', perspectives, colors['perspective'], 2)
    ]

    for section_name, components, color, row in sections:
        # Section header
        x = margin + row * cell_width
        y = margin + 0.8
        ax.add_patch(patches.Rectangle((x, y), cell_width, 0.1, facecolor=color, alpha=0.8))
        ax.text(x + cell_width/2, y + 0.05, f'{section_name} ({len(components)})',
               ha='center', va='center', fontweight='bold', fontsize=10)

        # Draw components
        for i, component in enumerate(components[:4]):  # Show up to 4 components
            comp_y = y - 0.15 - i * 0.15
            ax.add_patch(patches.Circle((x + cell_width/2, comp_y), 0.03,
                                      facecolor=color, alpha=0.8))
            ax.text(x + cell_width/2 + 0.05, comp_y, component.name[:12],
                   fontsize=8, ha='left', va='center')

    # Draw connecting arrows
    ax.arrow(0.3, 0.4, 0.1, 0, head_width=0.02, head_length=0.02, fc='black', alpha=0.6)
    ax.arrow(0.4, 0.3, 0, 0.1, head_width=0.02, head_length=0.02, fc='black', alpha=0.6)
    ax.arrow(0.5, 0.4, 0.1, 0, head_width=0.02, head_length=0.02, fc='black', alpha=0.6)

    # Add P3IF label
    ax.text(0.5, 0.5, 'P³', ha='center', va='center', fontweight='bold', fontsize=24)


def _draw_component_pair_grid(ax, comp1_list: list, comp2_list: list,
                             comp1_name: str, comp2_name: str,
                             color1: str, color2: str):
    """Draw a grid showing relationships between two component types."""
    ax.axis('off')

    # Determine grid size
    n1 = min(len(comp1_list), 4)
    n2 = min(len(comp2_list), 4)

    # Create grid
    for i in range(n1):
        for j in range(n2):
            x = 0.1 + j * 0.2
            y = 0.8 - i * 0.15

            # Draw cell
            ax.add_patch(patches.Rectangle((x, y), 0.15, 0.1,
                                         facecolor='lightgray', alpha=0.5, edgecolor='black'))

            # Add component names
            comp1 = comp1_list[i]
            comp2 = comp2_list[j]

            ax.text(x + 0.075, y + 0.07, comp1.name[:8], fontsize=6,
                   ha='center', va='center', fontweight='bold')
            ax.text(x + 0.075, y + 0.03, comp2.name[:8], fontsize=6,
                   ha='center', va='center', fontweight='bold')

            # Add colored dots
            ax.add_patch(patches.Circle((x + 0.03, y + 0.05), 0.015, facecolor=color1, alpha=0.8))
            ax.add_patch(patches.Circle((x + 0.12, y + 0.05), 0.015, facecolor=color2, alpha=0.8))

    # Add labels
    ax.text(0.5, 0.95, f'{comp1_name} × {comp2_name}', ha='center', va='center',
           fontweight='bold', fontsize=10)
    ax.text(0.5, 0.05, f'{n1} × {n2} = {n1 * n2} possible combinations',
           ha='center', va='center', fontsize=8)


def _add_grid_summary(ax, framework: P3IFFramework, colors: Dict[str, str]):
    """Add summary statistics to the grid."""
    ax.axis('off')

    # Get statistics
    properties = len([p for p in framework._patterns.values() if isinstance(p, Property)])
    processes = len([p for p in framework._patterns.values() if isinstance(p, Process)])
    perspectives = len([p for p in framework._patterns.values() if isinstance(p, Perspective)])
    relationships = len(framework._relationships)

    # Calculate theoretical maximums
    max_p_p = properties * processes
    max_p_persp = properties * perspectives
    max_proc_persp = processes * perspectives

    summary_data = [
        (f'Properties (P): {properties}', colors['property']),
        (f'Processes (P): {processes}', colors['process']),
        (f'Perspectives (P): {perspectives}', colors['perspective']),
        (f'Relationships: {relationships}', 'lightgreen'),
        ('', ''),
        ('Theoretical Maxima:', 'lightblue'),
        (f'P × P: {max_p_p}', 'lightcoral'),
        (f'P × P: {max_p_persp}', 'lightcoral'),
        (f'P × P: {max_proc_persp}', 'lightcoral')
    ]

    y_pos = 0.9
    for text, color in summary_data:
        if text:
            ax.add_patch(patches.Rectangle((0.1, y_pos), 0.8, 0.08,
                                         facecolor=color, alpha=0.8))
            ax.text(0.5, y_pos + 0.04, text, ha='center', va='center',
                   fontweight='bold', fontsize=10)
        y_pos -= 0.1


def _create_relationship_grid(framework: P3IFFramework,
                            session_path: Path,
                            filename: str,
                            title: str,
                            colors: Dict[str, str]):
    """Create a grid showing relationship patterns."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))

    # Get relationships by type
    rel_types = {}
    for rel in framework._relationships.values():
        rel_type = getattr(rel, 'relationship_type', 'general')
        if rel_type not in rel_types:
            rel_types[rel_type] = []
        rel_types[rel_type].append(rel)

    # Relationship type distribution
    if rel_types:
        types = list(rel_types.keys())
        counts = [len(rels) for rels in rel_types.values()]

        ax1.bar(types, counts, color=[colors['property'], colors['process'], colors['perspective']], alpha=0.8)
        ax1.set_title('Relationship Types')
        ax1.set_xlabel('Type')
        ax1.set_ylabel('Count')
        ax1.tick_params(axis='x', rotation=45)

    # Relationship strength grid
    strengths = [float(rel.strength) if hasattr(rel.strength, '__float__') else 0.5
                for rel in framework._relationships.values()]

    if strengths:
        ax2.hist(strengths, bins=10, alpha=0.7, color=colors['process'])
        ax2.set_title('Relationship Strength Distribution')
        ax2.set_xlabel('Strength')
        ax2.set_ylabel('Frequency')
        ax2.axvline(np.mean(strengths), color='red', linestyle='--', alpha=0.8,
                   label=f'Mean: {np.mean(strengths):.2f}')
        ax2.legend()

    # Relationship confidence grid
    confidences = [float(rel.confidence) if hasattr(rel.confidence, '__float__') else 1.0
                  for rel in framework._relationships.values()]

    if confidences:
        ax3.hist(confidences, bins=10, alpha=0.7, color=colors['perspective'])
        ax3.set_title('Relationship Confidence Distribution')
        ax3.set_xlabel('Confidence')
        ax3.set_ylabel('Frequency')
        ax3.axvline(np.mean(confidences), color='red', linestyle='--', alpha=0.8,
                   label=f'Mean: {np.mean(confidences):.2f}')
        ax3.legend()

    # Relationship summary
    ax4.axis('off')

    total_rels = len(framework._relationships)
    avg_strength = np.mean(strengths) if strengths else 0
    avg_confidence = np.mean(confidences) if confidences else 0

    summary_text = f"""
    Relationship Grid Summary:

    Total Relationships: {total_rels}

    Strength Statistics:
    • Average: {avg_strength:.2f}
    • Min: {min(strengths):.2f}
    • Max: {max(strengths):.2f}

    Confidence Statistics:
    • Average: {avg_confidence:.2f}
    • Min: {min(confidences):.2f}
    • Max: {max(confidences):.2f}

    Relationship Types: {len(rel_types)}
    """

    ax4.text(0.1, 0.8, summary_text, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    ax4.set_title('Relationship Summary')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    grids_dir = session_path / "visualizations" / "grids"
    grids_dir.mkdir(parents=True, exist_ok=True)
    output_path = grids_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_domain_grid(framework: P3IFFramework,
                      session_path: Path,
                      filename: str,
                      title: str,
                      colors: Dict[str, str]):
    """Create a grid showing domain organization."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.axis('off')

    # Get unique domains
    domains = list(set(p.domain for p in framework._patterns.values()))

    if not domains:
        ax.text(0.5, 0.5, 'No domains found', ha='center', va='center', transform=ax.transAxes)
        return

    # Create domain grid
    n_domains = len(domains)
    cols = min(3, n_domains)
    rows = (n_domains + cols - 1) // cols

    for i, domain in enumerate(domains):
        row = i // cols
        col = i % cols

        x = 0.1 + col * 0.3
        y = 0.8 - row * 0.25

        # Domain header
        ax.add_patch(patches.Rectangle((x, y), 0.25, 0.1, facecolor='lightgray', alpha=0.8))
        ax.text(x + 0.125, y + 0.05, domain, ha='center', va='center', fontweight='bold')

        # Get patterns in this domain
        domain_properties = [p for p in framework._patterns.values()
                           if p.domain == domain and isinstance(p, Property)]
        domain_processes = [p for p in framework._patterns.values()
                          if p.domain == domain and isinstance(p, Process)]
        domain_perspectives = [p for p in framework._patterns.values()
                             if p.domain == domain and isinstance(p, Perspective)]

        # Add pattern counts
        pattern_y = y - 0.05
        if domain_properties:
            ax.add_patch(patches.Circle((x + 0.05, pattern_y), 0.02, facecolor=colors['property'], alpha=0.8))
            ax.text(x + 0.08, pattern_y, f"P: {len(domain_properties)}", fontsize=8)

        if domain_processes:
            ax.add_patch(patches.Circle((x + 0.15, pattern_y), 0.02, facecolor=colors['process'], alpha=0.8))
            ax.text(x + 0.18, pattern_y, f"Proc: {len(domain_processes)}", fontsize=8)

        if domain_perspectives:
            ax.add_patch(patches.Circle((x + 0.05, pattern_y - 0.03), 0.02, facecolor=colors['perspective'], alpha=0.8))
            ax.text(x + 0.08, pattern_y - 0.03, f"Persp: {len(domain_perspectives)}", fontsize=8)

        # Add pattern names (first few)
        pattern_y = y - 0.1
        patterns_added = 0

        for prop in domain_properties[:2]:
            ax.add_patch(patches.FancyBboxPatch((x + 0.05, pattern_y), 0.15, 0.04,
                                              boxstyle="round,pad=0.01", facecolor=colors['property'], alpha=0.7))
            ax.text(x + 0.125, pattern_y + 0.02, prop.name[:10], fontsize=7, ha='center', va='center')
            pattern_y -= 0.05
            patterns_added += 1

        pattern_y = y - 0.1
        for proc in domain_processes[:2]:
            ax.add_patch(patches.FancyBboxPatch((x + 0.05, pattern_y), 0.15, 0.04,
                                              boxstyle="round,pad=0.01", facecolor=colors['process'], alpha=0.7))
            ax.text(x + 0.125, pattern_y + 0.02, proc.name[:10], fontsize=7, ha='center', va='center')
            pattern_y -= 0.05
            patterns_added += 1

        pattern_y = y - 0.1
        for persp in domain_perspectives[:2]:
            ax.add_patch(patches.FancyBboxPatch((x + 0.05, pattern_y), 0.15, 0.04,
                                              boxstyle="round,pad=0.01", facecolor=colors['perspective'], alpha=0.7))
            ax.text(x + 0.125, pattern_y + 0.02, persp.name[:10], fontsize=7, ha='center', va='center')
            pattern_y -= 0.05
            patterns_added += 1

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()

    # Save
    grids_dir = session_path / "visualizations" / "grids"
    grids_dir.mkdir(parents=True, exist_ok=True)
    output_path = grids_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_comprehensive_p3if_matrix(small_framework: P3IFFramework,
                                   large_framework: P3IFFramework,
                                   session_path: Path,
                                   filename: str,
                                   title: str,
                                   colors: Dict[str, str]):
    """Create a comprehensive matrix showing all P3IF combinations."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))

    # Calculate comprehensive statistics
    small_stats = _calculate_framework_grid_stats(small_framework)
    large_stats = _calculate_framework_grid_stats(large_framework)

    # Component matrix
    datasets = ['Small', 'Large']
    components = ['Properties', 'Processes', 'Perspectives']

    small_matrix = [
        [small_stats['properties'], small_stats['prop_proc_rels'], small_stats['prop_persp_rels']],
        [small_stats['prop_proc_rels'], small_stats['processes'], small_stats['proc_persp_rels']],
        [small_stats['prop_persp_rels'], small_stats['proc_persp_rels'], small_stats['perspectives']]
    ]

    large_matrix = [
        [large_stats['properties'], large_stats['prop_proc_rels'], large_stats['prop_persp_rels']],
        [large_stats['prop_proc_rels'], large_stats['processes'], large_stats['proc_persp_rels']],
        [large_stats['prop_persp_rels'], large_stats['proc_persp_rels'], large_stats['perspectives']]
    ]

    # Small dataset matrix
    im1 = ax1.imshow(small_matrix, cmap='Reds', alpha=0.8)
    ax1.set_title('Small Dataset - P3IF Matrix')
    ax1.set_xticks(range(len(components)))
    ax1.set_yticks(range(len(components)))
    ax1.set_xticklabels(components, rotation=45)
    ax1.set_yticklabels(components)

    for i in range(len(components)):
        for j in range(len(components)):
            text = ax1.text(j, i, small_matrix[i][j], ha='center', va='center',
                          color='black', fontweight='bold')

    # Large dataset matrix
    im2 = ax2.imshow(large_matrix, cmap='Blues', alpha=0.8)
    ax2.set_title('Large Dataset - P3IF Matrix')
    ax2.set_xticks(range(len(components)))
    ax2.set_yticks(range(len(components)))
    ax2.set_xticklabels(components, rotation=45)
    ax2.set_yticklabels(components)

    for i in range(len(components)):
        for j in range(len(components)):
            text = ax2.text(j, i, large_matrix[i][j], ha='center', va='center',
                          color='white', fontweight='bold')

    # Comparison bar chart
    x = np.arange(len(datasets))
    width = 0.25

    ax3.bar(x - width, [small_stats['total_patterns'], large_stats['total_patterns']],
           width, label='Total Patterns', color=colors['property'], alpha=0.8)
    ax3.bar(x, [small_stats['total_relationships'], large_stats['total_relationships']],
           width, label='Total Relationships', color=colors['process'], alpha=0.8)
    ax3.bar(x + width, [small_stats['domains'], large_stats['domains']],
           width, label='Domains', color=colors['perspective'], alpha=0.8)

    ax3.set_xlabel('Dataset')
    ax3.set_ylabel('Count')
    ax3.set_title('Dataset Comparison')
    ax3.set_xticks(x)
    ax3.set_xticklabels(datasets)
    ax3.legend()

    # Summary
    ax4.axis('off')

    summary_text = f"""
    Comprehensive P3IF Matrix Summary:

    Small Dataset:
    • Total Patterns: {small_stats['total_patterns']}
    • Total Relationships: {small_stats['total_relationships']}
    • Properties: {small_stats['properties']}
    • Processes: {small_stats['processes']}
    • Perspectives: {small_stats['perspectives']}
    • Domains: {small_stats['domains']}

    Large Dataset:
    • Total Patterns: {large_stats['total_patterns']}
    • Total Relationships: {large_stats['total_relationships']}
    • Properties: {large_stats['properties']}
    • Processes: {large_stats['processes']}
    • Perspectives: {large_stats['perspectives']}
    • Domains: {large_stats['domains']}

    Matrix shows:
    • Diagonal: Component counts
    • Off-diagonal: Relationships between types
    """

    ax4.text(0.1, 0.9, summary_text, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    ax4.set_title('Matrix Summary')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    grids_dir = session_path / "visualizations" / "grids"
    grids_dir.mkdir(parents=True, exist_ok=True)
    output_path = grids_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _calculate_framework_grid_stats(framework: P3IFFramework) -> Dict[str, Any]:
    """Calculate comprehensive statistics for grid visualization."""
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    # Count relationships by type
    prop_proc_rels = 0
    prop_persp_rels = 0
    proc_persp_rels = 0

    for rel in framework._relationships.values():
        has_prop = rel.property_id is not None
        has_proc = rel.process_id is not None
        has_persp = rel.perspective_id is not None

        if has_prop and has_proc:
            prop_proc_rels += 1
        if has_prop and has_persp:
            prop_persp_rels += 1
        if has_proc and has_persp:
            proc_persp_rels += 1

    domains = len(set(p.domain for p in framework._patterns.values()))

    return {
        'total_patterns': len(framework._patterns),
        'total_relationships': len(framework._relationships),
        'properties': len(properties),
        'processes': len(processes),
        'perspectives': len(perspectives),
        'prop_proc_rels': prop_proc_rels,
        'prop_persp_rels': prop_persp_rels,
        'proc_persp_rels': proc_persp_rels,
        'domains': domains
    }
