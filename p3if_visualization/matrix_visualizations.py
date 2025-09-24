#!/usr/bin/env python3
"""
P3IF Matrix Visualizations

Generates matrix visualizations showing relationships between Properties,
Processes, and Perspectives in tabular and heatmap formats.
"""
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from matplotlib.table import Table

from p3if_methods.framework import P3IFFramework
from p3if_methods.models import Property, Process, Perspective

logger = logging.getLogger(__name__)


def generate_matrix_visualizations(small_framework: P3IFFramework,
                                 large_framework: P3IFFramework,
                                 session_path: Path):
    """Generate all matrix visualizations."""
    logger.info("📊 Generating matrix visualizations...")

    # Color scheme for P3IF components
    colors = {
        'property': '#FF6B6B',      # Red
        'process': '#4ECDC4',       # Cyan
        'perspective': '#45B7D1'    # Blue
    }

    # Generate adjacency matrices
    _create_adjacency_matrix(small_framework, session_path, "small_adjacency_matrix",
                            "Small Dataset - Adjacency Matrix", colors)
    _create_adjacency_matrix(large_framework, session_path, "large_adjacency_matrix",
                            "Large Dataset - Adjacency Matrix", colors)

    # Generate correlation matrices
    _create_correlation_matrix(small_framework, session_path, "small_correlation_matrix",
                              "Small Dataset - Correlation Matrix", colors)
    _create_correlation_matrix(large_framework, session_path, "large_correlation_matrix",
                              "Large Dataset - Correlation Matrix", colors)

    # Generate strength matrices
    _create_strength_matrix(small_framework, session_path, "small_strength_matrix",
                           "Small Dataset - Relationship Strength Matrix", colors)
    _create_strength_matrix(large_framework, session_path, "large_strength_matrix",
                           "Large Dataset - Relationship Strength Matrix", colors)

    # Generate comprehensive matrix overview
    _create_matrix_overview(small_framework, large_framework, session_path,
                           "comprehensive_matrix_overview", "Comprehensive Matrix Overview", colors)


def _create_adjacency_matrix(framework: P3IFFramework,
                           session_path: Path,
                           filename: str,
                           title: str,
                           colors: Dict[str, str]):
    """Create an adjacency matrix showing connections between components."""
    # Get all patterns organized by type
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    all_patterns = properties + processes + perspectives

    if not all_patterns:
        logger.warning(f"No patterns found for adjacency matrix: {filename}")
        return

    # Create adjacency matrix
    n = len(all_patterns)
    adj_matrix = np.zeros((n, n))

    # Fill adjacency matrix based on relationships
    for rel in framework._relationships.values():
        indices = []

        # Find indices of connected patterns
        for pattern in all_patterns:
            if ((isinstance(pattern, Property) and rel.property_id == pattern.id) or
                (isinstance(pattern, Process) and rel.process_id == pattern.id) or
                (isinstance(pattern, Perspective) and rel.perspective_id == pattern.id)):
                indices.append(all_patterns.index(pattern))

        # Mark connections
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                adj_matrix[indices[i], indices[j]] = 1
                adj_matrix[indices[j], indices[i]] = 1

    # Create visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))

    # Main adjacency heatmap
    if np.any(adj_matrix > 0):
        sns.heatmap(adj_matrix, ax=ax1, cmap='Blues', annot=False,
                   xticklabels=[p.name[:8] for p in all_patterns],
                   yticklabels=[p.name[:8] for p in all_patterns], square=True)
        ax1.set_title('Adjacency Matrix (Connections)', fontsize=12, fontweight='bold')
    else:
        ax1.text(0.5, 0.5, 'No connections', ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Adjacency Matrix (Connections)', fontsize=12, fontweight='bold')

    # Pattern type indicators
    pattern_types = []
    for pattern in all_patterns:
        if isinstance(pattern, Property):
            pattern_types.append('P')
        elif isinstance(pattern, Process):
            pattern_types.append('Proc')
        else:  # Perspective
            pattern_types.append('Persp')

    # Type-based visualization
    type_matrix = np.zeros((3, 3))  # P, Proc, Persp counts
    for i, p1 in enumerate(all_patterns):
        for j, p2 in enumerate(all_patterns):
            if adj_matrix[i, j] > 0:
                if isinstance(p1, Property) and isinstance(p2, Process):
                    type_matrix[0, 1] += 1
                    type_matrix[1, 0] += 1
                elif isinstance(p1, Property) and isinstance(p2, Perspective):
                    type_matrix[0, 2] += 1
                    type_matrix[2, 0] += 1
                elif isinstance(p1, Process) and isinstance(p2, Perspective):
                    type_matrix[1, 2] += 1
                    type_matrix[2, 1] += 1

    if np.any(type_matrix > 0):
        sns.heatmap(type_matrix, ax=ax2, cmap='Reds', annot=True, fmt='g',
                   xticklabels=['Properties', 'Processes', 'Perspectives'],
                   yticklabels=['Properties', 'Processes', 'Perspectives'], square=True)
        ax2.set_title('Inter-Type Connections', fontsize=12, fontweight='bold')
    else:
        ax2.text(0.5, 0.5, 'No inter-type connections', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Inter-Type Connections', fontsize=12, fontweight='bold')

    # Connection statistics
    ax3.axis('off')
    total_connections = np.sum(adj_matrix) / 2  # Divide by 2 since symmetric
    connection_stats = {
        'Total Components': len(all_patterns),
        'Total Connections': int(total_connections),
        'Connection Density': f"{(total_connections / (n*(n-1)/2) * 100):.1f}%" if n > 1 else "0%",
        'Components with Connections': np.count_nonzero(np.sum(adj_matrix, axis=1))
    }

    y_pos = 0.9
    for stat_name, stat_value in connection_stats.items():
        ax3.text(0.1, y_pos, f"{stat_name}: {stat_value}", fontsize=10, fontweight='bold')
        y_pos -= 0.1

    # Component breakdown
    ax4.axis('off')
    comp_counts = {
        'Properties': len(properties),
        'Processes': len(processes),
        'Perspectives': len(perspectives)
    }

    ax4.bar(comp_counts.keys(), comp_counts.values(),
           color=[colors['property'], colors['process'], colors['perspective']], alpha=0.8)
    ax4.set_title('Component Distribution', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Count')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    matrices_dir = session_path / "visualizations" / "matrices"
    matrices_dir.mkdir(parents=True, exist_ok=True)
    output_path = matrices_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_correlation_matrix(framework: P3IFFramework,
                             session_path: Path,
                             filename: str,
                             title: str,
                             colors: Dict[str, str]):
    """Create a correlation matrix showing relationship strengths."""
    # Get all patterns organized by type
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    all_patterns = properties + processes + perspectives

    if not all_patterns:
        logger.warning(f"No patterns found for correlation matrix: {filename}")
        return

    # Create correlation matrix based on relationship strengths
    n = len(all_patterns)
    corr_matrix = np.zeros((n, n))

    # Fill correlation matrix with relationship strengths
    for rel in framework._relationships.values():
        indices = []

        # Find indices of connected patterns
        for pattern in all_patterns:
            if ((isinstance(pattern, Property) and rel.property_id == pattern.id) or
                (isinstance(pattern, Process) and rel.process_id == pattern.id) or
                (isinstance(pattern, Perspective) and rel.perspective_id == pattern.id)):
                indices.append(all_patterns.index(pattern))

        # Add correlation values
        strength = float(rel.strength) if hasattr(rel.strength, '__float__') else 0.5
        confidence = float(rel.confidence) if hasattr(rel.confidence, '__float__') else 1.0
        correlation = strength * confidence

        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                corr_matrix[indices[i], indices[j]] = correlation
                corr_matrix[indices[j], indices[i]] = correlation

    # Create visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))

    # Main correlation heatmap
    if np.any(corr_matrix > 0):
        sns.heatmap(corr_matrix, ax=ax1, cmap='RdYlBu_r', annot=False,
                   xticklabels=[p.name[:8] for p in all_patterns],
                   yticklabels=[p.name[:8] for p in all_patterns], square=True)
        ax1.set_title('Correlation Matrix (Strength × Confidence)', fontsize=12, fontweight='bold')
    else:
        ax1.text(0.5, 0.5, 'No correlations', ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Correlation Matrix (Strength × Confidence)', fontsize=12, fontweight='bold')

    # Correlation statistics
    correlations = corr_matrix[corr_matrix > 0]
    if len(correlations) > 0:
        ax2.hist(correlations, bins=20, alpha=0.7, color='lightgreen')
        ax2.set_title('Correlation Value Distribution')
        ax2.set_xlabel('Correlation')
        ax2.set_ylabel('Frequency')
        ax2.axvline(np.mean(correlations), color='red', linestyle='--', alpha=0.8,
                   label=f'Mean: {np.mean(correlations):.3f}')
        ax2.legend()
    else:
        ax2.text(0.5, 0.5, 'No correlation data', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Correlation Value Distribution')

    # Component type correlations
    type_correlations = {'P-P': [], 'P-Proc': [], 'P-Persp': [], 'Proc-Proc': [], 'Proc-Persp': [], 'Persp-Persp': []}

    for i, p1 in enumerate(all_patterns):
        for j, p2 in enumerate(all_patterns):
            if corr_matrix[i, j] > 0:
                if isinstance(p1, Property) and isinstance(p2, Property):
                    type_correlations['P-P'].append(corr_matrix[i, j])
                elif isinstance(p1, Property) and isinstance(p2, Process):
                    type_correlations['P-Proc'].append(corr_matrix[i, j])
                elif isinstance(p1, Property) and isinstance(p2, Perspective):
                    type_correlations['P-Persp'].append(corr_matrix[i, j])
                elif isinstance(p1, Process) and isinstance(p2, Process):
                    type_correlations['Proc-Proc'].append(corr_matrix[i, j])
                elif isinstance(p1, Process) and isinstance(p2, Perspective):
                    type_correlations['Proc-Persp'].append(corr_matrix[i, j])
                elif isinstance(p1, Perspective) and isinstance(p2, Perspective):
                    type_correlations['Persp-Persp'].append(corr_matrix[i, j])

    # Plot type correlations
    ax3.axis('off')
    y_pos = 0.9
    for corr_type, values in type_correlations.items():
        if values:
            mean_corr = np.mean(values)
            ax3.barh(y_pos, mean_corr, height=0.05, alpha=0.7,
                    label=f'{corr_type}: {mean_corr:.3f}')
            ax3.text(mean_corr + 0.01, y_pos, f'{len(values)} connections',
                    fontsize=8, va='center')
            y_pos -= 0.08

    ax3.set_xlim(0, 1)
    ax3.set_title('Average Correlations by Type', fontsize=12, fontweight='bold')
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    # Correlation summary
    ax4.axis('off')
    total_correlations = np.sum(corr_matrix > 0) / 2  # Divide by 2 for symmetric matrix
    avg_correlation = np.mean(correlations) if len(correlations) > 0 else 0

    summary_text = f"""
    Correlation Matrix Summary:

    Total Components: {len(all_patterns)}
    Total Correlations: {int(total_correlations)}
    Average Correlation: {avg_correlation:.3f}

    Type Breakdown:
    • Property-Property: {len(type_correlations['P-P'])} connections
    • Property-Process: {len(type_correlations['P-Proc'])} connections
    • Property-Perspective: {len(type_correlations['P-Persp'])} connections
    • Process-Process: {len(type_correlations['Proc-Proc'])} connections
    • Process-Perspective: {len(type_correlations['Proc-Persp'])} connections
    • Perspective-Perspective: {len(type_correlations['Persp-Persp'])} connections
    """

    ax4.text(0.1, 0.9, summary_text, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    ax4.set_title('Correlation Summary', fontsize=12, fontweight='bold')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    matrices_dir = session_path / "visualizations" / "matrices"
    matrices_dir.mkdir(parents=True, exist_ok=True)
    output_path = matrices_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_strength_matrix(framework: P3IFFramework,
                          session_path: Path,
                          filename: str,
                          title: str,
                          colors: Dict[str, str]):
    """Create a matrix showing relationship strengths."""
    # Get all patterns organized by type
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    all_patterns = properties + processes + perspectives

    if not all_patterns:
        logger.warning(f"No patterns found for strength matrix: {filename}")
        return

    # Create strength matrix
    n = len(all_patterns)
    strength_matrix = np.zeros((n, n))

    # Fill strength matrix
    for rel in framework._relationships.values():
        indices = []

        # Find indices of connected patterns
        for pattern in all_patterns:
            if ((isinstance(pattern, Property) and rel.property_id == pattern.id) or
                (isinstance(pattern, Process) and rel.process_id == pattern.id) or
                (isinstance(pattern, Perspective) and rel.perspective_id == pattern.id)):
                indices.append(all_patterns.index(pattern))

        # Add strength values
        strength = float(rel.strength) if hasattr(rel.strength, '__float__') else 0.5

        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                strength_matrix[indices[i], indices[j]] = strength
                strength_matrix[indices[j], indices[i]] = strength

    # Create visualization
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    # Strength heatmap
    if np.any(strength_matrix > 0):
        sns.heatmap(strength_matrix, ax=ax, cmap='YlOrRd', annot=True, fmt='.2f',
                   xticklabels=[p.name[:8] for p in all_patterns],
                   yticklabels=[p.name[:8] for p in all_patterns], square=True)
        ax.set_title('Relationship Strength Matrix', fontsize=14, fontweight='bold')
    else:
        ax.text(0.5, 0.5, 'No strength data', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Relationship Strength Matrix', fontsize=14, fontweight='bold')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    matrices_dir = session_path / "visualizations" / "matrices"
    matrices_dir.mkdir(parents=True, exist_ok=True)
    output_path = matrices_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_matrix_overview(small_framework: P3IFFramework,
                          large_framework: P3IFFramework,
                          session_path: Path,
                          filename: str,
                          title: str,
                          colors: Dict[str, str]):
    """Create a comprehensive overview of all matrix types."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))

    # Matrix size comparison
    small_patterns = len(small_framework._patterns)
    large_patterns = len(large_framework._patterns)

    ax1.bar(['Small Dataset', 'Large Dataset'], [small_patterns, large_patterns],
           color=['lightblue', 'lightcoral'], alpha=0.8)
    ax1.set_title('Matrix Sizes (Pattern Counts)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Number of Patterns')

    # Relationship density comparison
    small_density = len(small_framework._relationships) / (small_patterns * (small_patterns - 1) / 2) if small_patterns > 1 else 0
    large_density = len(large_framework._relationships) / (large_patterns * (large_patterns - 1) / 2) if large_patterns > 1 else 0

    ax2.bar(['Small Dataset', 'Large Dataset'], [small_density, large_density],
           color=['lightgreen', 'lightpink'], alpha=0.8)
    ax2.set_title('Relationship Density', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Density (0-1)')

    # Component type distribution in matrices
    small_props = len([p for p in small_framework._patterns.values() if isinstance(p, Property)])
    small_procs = len([p for p in small_framework._patterns.values() if isinstance(p, Process)])
    small_persps = len([p for p in small_framework._patterns.values() if isinstance(p, Perspective)])

    large_props = len([p for p in large_framework._patterns.values() if isinstance(p, Property)])
    large_procs = len([p for p in large_framework._patterns.values() if isinstance(p, Process)])
    large_persps = len([p for p in large_framework._patterns.values() if isinstance(p, Perspective)])

    # Small dataset breakdown
    ax3.pie([small_props, small_procs, small_persps],
           labels=['Properties', 'Processes', 'Perspectives'],
           colors=[colors['property'], colors['process'], colors['perspective']],
           autopct='%1.1f%%', startangle=90)
    ax3.set_title('Small Dataset - Component Distribution', fontsize=12, fontweight='bold')

    # Large dataset breakdown
    ax4.pie([large_props, large_procs, large_persps],
           labels=['Properties', 'Processes', 'Perspectives'],
           colors=[colors['property'], colors['process'], colors['perspective']],
           autopct='%1.1f%%', startangle=90)
    ax4.set_title('Large Dataset - Component Distribution', fontsize=12, fontweight='bold')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    matrices_dir = session_path / "visualizations" / "matrices"
    matrices_dir.mkdir(parents=True, exist_ok=True)
    output_path = matrices_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")
