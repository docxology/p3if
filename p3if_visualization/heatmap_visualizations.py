#!/usr/bin/env python3
"""
P3IF Heatmap Visualizations

Generates heatmaps showing relationships between Properties, Processes, and Perspectives,
and domain relationships.
"""
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, Any
import pandas as pd

from p3if_methods.framework import P3IFFramework
from p3if_methods.models import Property, Process, Perspective

logger = logging.getLogger(__name__)


def generate_heatmap_visualizations(small_framework: P3IFFramework,
                                  large_framework: P3IFFramework,
                                  session_path: Path):
    """Generate all heatmap visualizations."""
    logger.info("🔥 Generating heatmap visualizations...")

    # Color scheme for P3IF components
    colors = {
        'property': '#FF6B6B',      # Red
        'process': '#4ECDC4',       # Cyan
        'perspective': '#45B7D1'    # Blue
    }

    # Generate P3IF relationship heatmaps
    _create_p3if_relationship_heatmap(small_framework, session_path, "small_relationship_heatmap",
                                    "Small Dataset - P3IF Relationship Heatmap", colors)
    _create_p3if_relationship_heatmap(large_framework, session_path, "large_relationship_heatmap",
                                    "Large Dataset - P3IF Relationship Heatmap", colors)

    # Generate domain heatmaps
    _create_domain_heatmap(small_framework, session_path, "small_domain_heatmap",
                          "Small Dataset - Domain Heatmap", colors)
    _create_domain_heatmap(large_framework, session_path, "large_domain_heatmap",
                          "Large Dataset - Domain Heatmap", colors)

    # Generate component strength heatmaps
    _create_component_strength_heatmap(small_framework, session_path, "small_strength_heatmap",
                                     "Small Dataset - Component Strength Heatmap", colors)
    _create_component_strength_heatmap(large_framework, session_path, "large_strength_heatmap",
                                     "Large Dataset - Component Strength Heatmap", colors)


def _create_p3if_relationship_heatmap(framework: P3IFFramework,
                                    session_path: Path,
                                    filename: str,
                                    title: str,
                                    colors: Dict[str, str]):
    """Create a heatmap showing relationships between P3IF components."""
    # Get all patterns organized by type
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    if not (properties and processes and perspectives):
        logger.warning(f"Insufficient data for relationship heatmap: {filename}")
        return

    # Create matrices for relationships
    n_props = len(properties)
    n_procs = len(processes)
    n_persps = len(perspectives)

    # Initialize relationship matrices
    prop_proc_matrix = np.zeros((n_props, n_procs))
    prop_persp_matrix = np.zeros((n_props, n_persps))
    proc_persp_matrix = np.zeros((n_procs, n_persps))

    # Fill matrices based on relationships
    for rel in framework._relationships.values():
        prop_idx, proc_idx, persp_idx = None, None, None

        # Find indices
        if rel.property_id:
            for i, p in enumerate(properties):
                if p.id == rel.property_id:
                    prop_idx = i
                    break

        if rel.process_id:
            for i, p in enumerate(processes):
                if p.id == rel.process_id:
                    proc_idx = i
                    break

        if rel.perspective_id:
            for i, p in enumerate(perspectives):
                if p.id == rel.perspective_id:
                    persp_idx = i
                    break

        # Update matrices
        strength = float(rel.strength) if hasattr(rel.strength, '__float__') else 0.5

        if prop_idx is not None and proc_idx is not None:
            prop_proc_matrix[prop_idx, proc_idx] = strength

        if prop_idx is not None and persp_idx is not None:
            prop_persp_matrix[prop_idx, persp_idx] = strength

        if proc_idx is not None and persp_idx is not None:
            proc_persp_matrix[proc_idx, persp_idx] = strength

    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))

    # Property-Process heatmap
    if np.any(prop_proc_matrix > 0):
        sns.heatmap(prop_proc_matrix, ax=ax1, cmap='Reds', annot=True, fmt='.2f',
                   xticklabels=[p.name[:12] for p in processes],
                   yticklabels=[p.name[:12] for p in properties])
        ax1.set_title('Properties ↔ Processes', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Processes')
        ax1.set_ylabel('Properties')
    else:
        ax1.text(0.5, 0.5, 'No P-P relationships', ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Properties ↔ Processes', fontsize=12, fontweight='bold')

    # Property-Perspective heatmap
    if np.any(prop_persp_matrix > 0):
        sns.heatmap(prop_persp_matrix, ax=ax2, cmap='Blues', annot=True, fmt='.2f',
                   xticklabels=[p.name[:12] for p in perspectives],
                   yticklabels=[p.name[:12] for p in properties])
        ax2.set_title('Properties ↔ Perspectives', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Perspectives')
        ax2.set_ylabel('Properties')
    else:
        ax2.text(0.5, 0.5, 'No P-Persp relationships', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Properties ↔ Perspectives', fontsize=12, fontweight='bold')

    # Process-Perspective heatmap
    if np.any(proc_persp_matrix > 0):
        sns.heatmap(proc_persp_matrix, ax=ax3, cmap='Greens', annot=True, fmt='.2f',
                   xticklabels=[p.name[:12] for p in perspectives],
                   yticklabels=[p.name[:12] for p in processes])
        ax3.set_title('Processes ↔ Perspectives', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Perspectives')
        ax3.set_ylabel('Processes')
    else:
        ax3.text(0.5, 0.5, 'No Proc-Persp relationships', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Processes ↔ Perspectives', fontsize=12, fontweight='bold')

    # Combined relationship summary
    ax4.axis('off')
    summary_text = f"""
    P3IF Relationship Summary:

    Properties: {len(properties)}
    Processes: {len(processes)}
    Perspectives: {len(perspectives)}

    Total Relationships: {len(framework._relationships)}

    Relationship Types:
    • Property-Process: {np.count_nonzero(prop_proc_matrix > 0)}
    • Property-Perspective: {np.count_nonzero(prop_persp_matrix > 0)}
    • Process-Perspective: {np.count_nonzero(proc_persp_matrix > 0)}

    Average Strength:
    • P-P: {np.mean(prop_proc_matrix[prop_proc_matrix > 0]):.2f}
    • P-Persp: {np.mean(prop_persp_matrix[prop_persp_matrix > 0]):.2f}
    • Proc-Persp: {np.mean(proc_persp_matrix[proc_persp_matrix > 0]):.2f}
    """
    ax4.text(0.1, 0.9, summary_text, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    ax4.set_title('Relationship Summary', fontsize=12, fontweight='bold')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    heatmaps_dir = session_path / "visualizations" / "heatmaps"
    heatmaps_dir.mkdir(parents=True, exist_ok=True)
    output_path = heatmaps_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_domain_heatmap(framework: P3IFFramework,
                         session_path: Path,
                         filename: str,
                         title: str,
                         colors: Dict[str, str]):
    """Create a heatmap showing domain relationships."""
    # Get unique domains
    domains = list(set(p.domain for p in framework._patterns.values()))

    if len(domains) < 2:
        logger.warning(f"Insufficient domains for heatmap: {filename}")
        return

    # Create domain relationship matrix
    n_domains = len(domains)
    domain_matrix = np.zeros((n_domains, n_domains))

    # Count relationships between domains
    for rel in framework._relationships.values():
        domain1, domain2, domain3 = None, None, None

        # Find domains for connected patterns
        if rel.property_id:
            for p in framework._patterns.values():
                if p.id == rel.property_id:
                    domain1 = p.domain
                    break

        if rel.process_id:
            for p in framework._patterns.values():
                if p.id == rel.process_id:
                    domain2 = p.domain
                    break

        if rel.perspective_id:
            for p in framework._patterns.values():
                if p.id == rel.perspective_id:
                    domain3 = p.domain
                    break

        # Update matrix
        domains_in_rel = [d for d in [domain1, domain2, domain3] if d]
        if len(domains_in_rel) >= 2:
            for i in range(len(domains_in_rel)):
                for j in range(i + 1, len(domains_in_rel)):
                    idx1 = domains.index(domains_in_rel[i])
                    idx2 = domains.index(domains_in_rel[j])
                    domain_matrix[idx1, idx2] += 1
                    domain_matrix[idx2, idx1] += 1  # Symmetric

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Domain relationship heatmap
    if np.any(domain_matrix > 0):
        sns.heatmap(domain_matrix, ax=ax1, cmap='YlOrRd', annot=True, fmt='g',
                   xticklabels=domains, yticklabels=domains, square=True)
        ax1.set_title('Domain Relationships', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Domains')
        ax1.set_ylabel('Domains')
    else:
        ax1.text(0.5, 0.5, 'No domain relationships', ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Domain Relationships', fontsize=12, fontweight='bold')

    # Domain pattern counts
    domain_counts = {}
    for domain in domains:
        props = len([p for p in framework._patterns.values()
                   if p.domain == domain and isinstance(p, Property)])
        procs = len([p for p in framework._patterns.values()
                    if p.domain == domain and isinstance(p, Process)])
        persps = len([p for p in framework._patterns.values()
                     if p.domain == domain and isinstance(p, Perspective)])

        domain_counts[domain] = {'Properties': props, 'Processes': procs, 'Perspectives': persps}

    df = pd.DataFrame(domain_counts).T
    df.plot(kind='bar', stacked=True, ax=ax2, color=[colors['property'], colors['process'], colors['perspective']])
    ax2.set_title('Pattern Distribution by Domain', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Domains')
    ax2.set_ylabel('Count')
    ax2.legend(title='Component Type')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    heatmaps_dir = session_path / "visualizations" / "heatmaps"
    heatmaps_dir.mkdir(parents=True, exist_ok=True)
    output_path = heatmaps_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_component_strength_heatmap(framework: P3IFFramework,
                                     session_path: Path,
                                     filename: str,
                                     title: str,
                                     colors: Dict[str, str]):
    """Create a heatmap showing component strength relationships."""
    # Get all patterns organized by type
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    if not (properties and processes and perspectives):
        logger.warning(f"Insufficient data for strength heatmap: {filename}")
        return

    # Create strength matrix between all components
    all_patterns = properties + processes + perspectives
    n_patterns = len(all_patterns)
    strength_matrix = np.zeros((n_patterns, n_patterns))

    # Fill matrix with relationship strengths
    for rel in framework._relationships.values():
        indices = []

        if rel.property_id:
            for i, p in enumerate(all_patterns):
                if p.id == rel.property_id:
                    indices.append(i)
                    break

        if rel.process_id:
            for i, p in enumerate(all_patterns):
                if p.id == rel.process_id:
                    indices.append(i)
                    break

        if rel.perspective_id:
            for i, p in enumerate(all_patterns):
                if p.id == rel.perspective_id:
                    indices.append(i)
                    break

        # Update strength matrix
        strength = float(rel.strength) if hasattr(rel.strength, '__float__') else 0.5
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                strength_matrix[indices[i], indices[j]] = strength
                strength_matrix[indices[j], indices[i]] = strength

    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    # Create labels
    labels = [p.name[:15] for p in all_patterns]
    pattern_types = [type(p).__name__ for p in all_patterns]

    # Create color mapping for types
    color_map = []
    for p_type in pattern_types:
        if p_type == 'Property':
            color_map.append(colors['property'])
        elif p_type == 'Process':
            color_map.append(colors['process'])
        else:  # Perspective
            color_map.append(colors['perspective'])

    if np.any(strength_matrix > 0):
        # Create heatmap
        sns.heatmap(strength_matrix, ax=ax, cmap='RdYlBu_r', annot=True, fmt='.2f',
                   xticklabels=labels, yticklabels=labels, square=True)

        # Add colored borders to show component types
        for i in range(n_patterns):
            ax.add_patch(plt.Rectangle((i, i), 1, 1, fill=False,
                                     edgecolor=color_map[i], linewidth=3))

        ax.set_title('Component Relationship Strengths', fontsize=14, fontweight='bold')
        ax.set_xlabel('Patterns')
        ax.set_ylabel('Patterns')
    else:
        ax.text(0.5, 0.5, 'No relationship strengths found',
               ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Component Relationship Strengths', fontsize=14, fontweight='bold')

    # Add legend for colors
    legend_elements = [
        plt.Line2D([0], [0], color=colors['property'], linewidth=3, label='Properties'),
        plt.Line2D([0], [0], color=colors['process'], linewidth=3, label='Processes'),
        plt.Line2D([0], [0], color=colors['perspective'], linewidth=3, label='Perspectives')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    heatmaps_dir = session_path / "visualizations" / "heatmaps"
    heatmaps_dir.mkdir(parents=True, exist_ok=True)
    output_path = heatmaps_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")
