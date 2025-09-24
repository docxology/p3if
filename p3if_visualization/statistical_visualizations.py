#!/usr/bin/env python3
"""
P3IF Statistical Visualizations

Generates statistical charts and analyses for Properties, Processes, and Perspectives
including distributions, trends, and quality metrics.
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


def generate_statistical_visualizations(small_framework: P3IFFramework,
                                     large_framework: P3IFFramework,
                                     session_path: Path):
    """Generate all statistical visualizations."""
    logger.info("📈 Generating statistical visualizations...")

    # Color scheme for P3IF components
    colors = {
        'property': '#FF6B6B',      # Red
        'process': '#4ECDC4',       # Cyan
        'perspective': '#45B7D1'    # Blue
    }

    # Generate component type distributions
    _create_component_distributions(small_framework, large_framework, session_path,
                                  "component_distributions", "Component Type Distributions", colors)

    # Generate quality metrics analysis
    _create_quality_metrics_analysis(small_framework, large_framework, session_path,
                                   "quality_metrics", "Quality Metrics Analysis", colors)

    # Generate relationship statistics
    _create_relationship_statistics(small_framework, large_framework, session_path,
                                  "relationship_stats", "Relationship Statistics", colors)

    # Generate domain analysis
    _create_domain_analysis(small_framework, large_framework, session_path,
                           "domain_analysis", "Domain Analysis", colors)

    # Generate comprehensive statistical overview
    _create_statistical_overview(small_framework, large_framework, session_path,
                                "comprehensive_stats", "Comprehensive Statistical Overview", colors)


def _create_component_distributions(small_framework: P3IFFramework,
                                  large_framework: P3IFFramework,
                                  session_path: Path,
                                  filename: str,
                                  title: str,
                                  colors: Dict[str, str]):
    """Create component type distribution visualizations."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))

    # Get component counts
    small_props = len([p for p in small_framework._patterns.values() if isinstance(p, Property)])
    small_procs = len([p for p in small_framework._patterns.values() if isinstance(p, Process)])
    small_persps = len([p for p in small_framework._patterns.values() if isinstance(p, Perspective)])

    large_props = len([p for p in large_framework._patterns.values() if isinstance(p, Property)])
    large_procs = len([p for p in large_framework._patterns.values() if isinstance(p, Process)])
    large_persps = len([p for p in large_framework._patterns.values() if isinstance(p, Perspective)])

    # Bar chart comparison
    datasets = ['Small Dataset', 'Large Dataset']
    prop_counts = [small_props, large_props]
    proc_counts = [small_procs, large_procs]
    persp_counts = [small_persps, large_persps]

    x = np.arange(len(datasets))
    width = 0.25

    ax1.bar(x - width, prop_counts, width, label='Properties', color=colors['property'], alpha=0.8)
    ax1.bar(x, proc_counts, width, label='Processes', color=colors['process'], alpha=0.8)
    ax1.bar(x + width, persp_counts, width, label='Perspectives', color=colors['perspective'], alpha=0.8)

    ax1.set_xlabel('Dataset')
    ax1.set_ylabel('Count')
    ax1.set_title('Component Distribution by Dataset')
    ax1.set_xticks(x)
    ax1.set_xticklabels(datasets)
    ax1.legend()

    # Pie chart for small dataset
    small_total = small_props + small_procs + small_persps
    if small_total > 0:
        ax2.pie([small_props, small_procs, small_persps],
               labels=['Properties', 'Processes', 'Perspectives'],
               colors=[colors['property'], colors['process'], colors['perspective']],
               autopct='%1.1f%%', startangle=90)
        ax2.set_title('Small Dataset - Component Distribution')
    else:
        ax2.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Small Dataset - Component Distribution')

    # Pie chart for large dataset
    large_total = large_props + large_procs + large_persps
    if large_total > 0:
        ax3.pie([large_props, large_procs, large_persps],
               labels=['Properties', 'Processes', 'Perspectives'],
               colors=[colors['property'], colors['process'], colors['perspective']],
               autopct='%1.1f%%', startangle=90)
        ax3.set_title('Large Dataset - Component Distribution')
    else:
        ax3.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Large Dataset - Component Distribution')

    # Stacked area chart showing growth
    ax4.stackplot(datasets, [prop_counts, proc_counts, persp_counts],
                 labels=['Properties', 'Processes', 'Perspectives'],
                 colors=[colors['property'], colors['process'], colors['perspective']], alpha=0.8)

    ax4.set_xlabel('Dataset')
    ax4.set_ylabel('Total Components')
    ax4.set_title('Component Growth Between Datasets')
    ax4.legend(loc='upper left')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    statistics_dir = session_path / "visualizations" / "statistics"
    statistics_dir.mkdir(parents=True, exist_ok=True)
    output_path = statistics_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_quality_metrics_analysis(small_framework: P3IFFramework,
                                   large_framework: P3IFFramework,
                                   session_path: Path,
                                   filename: str,
                                   title: str,
                                   colors: Dict[str, str]):
    """Create quality metrics analysis visualizations."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))

    # Get quality scores for all components
    small_quality_scores = []
    large_quality_scores = []

    for framework, scores_list in [(small_framework, small_quality_scores), (large_framework, large_quality_scores)]:
        for pattern in framework._patterns.values():
            quality_score = getattr(pattern, 'quality_score', 1.0)
            scores_list.append(quality_score)

    # Quality score distributions
    if small_quality_scores:
        ax1.hist(small_quality_scores, bins=10, alpha=0.7, color=colors['property'], label='Small Dataset')
        ax1.axvline(np.mean(small_quality_scores), color='red', linestyle='--', alpha=0.8,
                   label=f'Mean: {np.mean(small_quality_scores):.2f}')

    if large_quality_scores:
        ax2.hist(large_quality_scores, bins=10, alpha=0.7, color=colors['process'], label='Large Dataset')
        ax2.axvline(np.mean(large_quality_scores), color='blue', linestyle='--', alpha=0.8,
                   label=f'Mean: {np.mean(large_quality_scores):.2f}')

    ax1.set_xlabel('Quality Score')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Small Dataset - Quality Score Distribution')
    ax1.legend()

    ax2.set_xlabel('Quality Score')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Large Dataset - Quality Score Distribution')
    ax2.legend()

    # Quality score comparison
    datasets = ['Small Dataset', 'Large Dataset']
    if small_quality_scores and large_quality_scores:
        means = [np.mean(small_quality_scores), np.mean(large_quality_scores)]
        stds = [np.std(small_quality_scores), np.std(large_quality_scores)]

        ax3.bar(datasets, means, yerr=stds, capsize=5,
               color=[colors['property'], colors['process']], alpha=0.8)
        ax3.set_ylabel('Quality Score')
        ax3.set_title('Quality Score Comparison')

        # Add value labels
        for i, (mean, std) in enumerate(zip(means, stds)):
            ax3.text(i, mean + std + 0.01, f'{mean:.2f}±{std:.2f}',
                    ha='center', va='bottom', fontweight='bold')

    # Quality score by component type
    ax4.axis('off')

    # Calculate quality by type
    small_prop_quality = []
    small_proc_quality = []
    small_persp_quality = []

    large_prop_quality = []
    large_proc_quality = []
    large_persp_quality = []

    for framework, prop_list, proc_list, persp_list in [
        (small_framework, small_prop_quality, small_proc_quality, small_persp_quality),
        (large_framework, large_prop_quality, large_proc_quality, large_persp_quality)
    ]:
        for pattern in framework._patterns.values():
            quality = getattr(pattern, 'quality_score', 1.0)
            if isinstance(pattern, Property):
                prop_list.append(quality)
            elif isinstance(pattern, Process):
                proc_list.append(quality)
            elif isinstance(pattern, Perspective):
                persp_list.append(quality)

    # Create summary table
    summary_data = []
    for dataset, prop_q, proc_q, persp_q in [
        ('Small', small_prop_quality, small_proc_quality, small_persp_quality),
        ('Large', large_prop_quality, large_proc_quality, large_persp_quality)
    ]:
        summary_data.append([
            dataset,
            f"{np.mean(prop_q):.2f}" if prop_q else 'N/A',
            f"{np.mean(proc_q):.2f}" if proc_q else 'N/A',
            f"{np.mean(persp_q):.2f}" if persp_q else 'N/A',
            f"{len(prop_q + proc_q + persp_q)}"
        ])

    table = ax4.table(cellText=summary_data,
                     colLabels=['Dataset', 'Properties', 'Processes', 'Perspectives', 'Total'],
                     cellLoc='center', loc='center', colColours=['lightgray']*5)

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    ax4.set_title('Quality Metrics Summary', fontsize=12, fontweight='bold')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    statistics_dir = session_path / "visualizations" / "statistics"
    statistics_dir.mkdir(parents=True, exist_ok=True)
    output_path = statistics_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_relationship_statistics(small_framework: P3IFFramework,
                                  large_framework: P3IFFramework,
                                  session_path: Path,
                                  filename: str,
                                  title: str,
                                  colors: Dict[str, str]):
    """Create relationship statistics visualizations."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))

    # Get relationship strengths and confidences
    small_strengths = []
    small_confidences = []
    large_strengths = []
    large_confidences = []

    for framework, str_list, conf_list in [
        (small_framework, small_strengths, small_confidences),
        (large_framework, large_strengths, large_confidences)
    ]:
        for rel in framework._relationships.values():
            strength = float(rel.strength) if hasattr(rel.strength, '__float__') else 0.5
            confidence = float(rel.confidence) if hasattr(rel.confidence, '__float__') else 1.0
            str_list.append(strength)
            conf_list.append(confidence)

    # Relationship strength distributions
    if small_strengths:
        ax1.hist(small_strengths, bins=10, alpha=0.7, color=colors['property'], label='Small Dataset')
        ax1.axvline(np.mean(small_strengths), color='red', linestyle='--', alpha=0.8)

    if large_strengths:
        ax2.hist(large_strengths, bins=10, alpha=0.7, color=colors['process'], label='Large Dataset')
        ax2.axvline(np.mean(large_strengths), color='blue', linestyle='--', alpha=0.8)

    ax1.set_xlabel('Relationship Strength')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Small Dataset - Strength Distribution')
    ax1.legend()

    ax2.set_xlabel('Relationship Strength')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Large Dataset - Strength Distribution')
    ax2.legend()

    # Relationship confidence distributions
    if small_confidences:
        ax3.hist(small_confidences, bins=10, alpha=0.7, color=colors['property'], label='Small Dataset')
        ax3.axvline(np.mean(small_confidences), color='red', linestyle='--', alpha=0.8)

    if large_confidences:
        ax4.hist(large_confidences, bins=10, alpha=0.7, color=colors['process'], label='Large Dataset')
        ax4.axvline(np.mean(large_confidences), color='blue', linestyle='--', alpha=0.8)

    ax3.set_xlabel('Relationship Confidence')
    ax3.set_ylabel('Frequency')
    ax3.set_title('Small Dataset - Confidence Distribution')
    ax3.legend()

    ax4.set_xlabel('Relationship Confidence')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Large Dataset - Confidence Distribution')
    ax4.legend()

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    statistics_dir = session_path / "visualizations" / "statistics"
    statistics_dir.mkdir(parents=True, exist_ok=True)
    output_path = statistics_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_domain_analysis(small_framework: P3IFFramework,
                          large_framework: P3IFFramework,
                          session_path: Path,
                          filename: str,
                          title: str,
                          colors: Dict[str, str]):
    """Create domain analysis visualizations."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))

    # Get domain data
    small_domains = {}
    large_domains = {}

    for framework, domain_dict in [(small_framework, small_domains), (large_framework, large_domains)]:
        for pattern in framework._patterns.values():
            domain = pattern.domain
            if domain not in domain_dict:
                domain_dict[domain] = {'properties': 0, 'processes': 0, 'perspectives': 0}

            if isinstance(pattern, Property):
                domain_dict[domain]['properties'] += 1
            elif isinstance(pattern, Process):
                domain_dict[domain]['processes'] += 1
            elif isinstance(pattern, Perspective):
                domain_dict[domain]['perspectives'] += 1

    # Domain count comparison
    if small_domains and large_domains:
        common_domains = set(small_domains.keys()) & set(large_domains.keys())
        if common_domains:
            domains_list = list(common_domains)[:5]  # Show top 5 domains

            small_counts = [sum(small_domains[d].values()) for d in domains_list]
            large_counts = [sum(large_domains[d].values()) for d in domains_list]

            x = np.arange(len(domains_list))
            width = 0.35

            ax1.bar(x - width/2, small_counts, width, label='Small Dataset', color=colors['property'], alpha=0.8)
            ax1.bar(x + width/2, large_counts, width, label='Large Dataset', color=colors['process'], alpha=0.8)

            ax1.set_xlabel('Domain')
            ax1.set_ylabel('Pattern Count')
            ax1.set_title('Domain Pattern Distribution')
            ax1.set_xticks(x)
            ax1.set_xticklabels(domains_list, rotation=45)
            ax1.legend()

    # Domain diversity
    small_diversity = len(small_domains)
    large_diversity = len(large_domains)

    ax2.bar(['Small Dataset', 'Large Dataset'], [small_diversity, large_diversity],
           color=[colors['property'], colors['process']], alpha=0.8)
    ax2.set_ylabel('Number of Domains')
    ax2.set_title('Domain Diversity')

    # Component distribution by domain
    ax3.axis('off')

    if small_domains:
        # Create summary for small dataset
        small_summary = []
        for domain, counts in list(small_domains.items())[:5]:  # Show top 5
            total = sum(counts.values())
            small_summary.append([domain, total, counts['properties'], counts['processes'], counts['perspectives']])

        table = ax3.table(cellText=small_summary,
                         colLabels=['Domain', 'Total', 'Properties', 'Processes', 'Perspectives'],
                         cellLoc='center', loc='center', colColours=['lightgray']*5)
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.5)
        ax3.set_title('Small Dataset - Domain Breakdown', fontsize=12, fontweight='bold')

    # Large dataset summary
    ax4.axis('off')

    if large_domains:
        large_summary = []
        for domain, counts in list(large_domains.items())[:5]:  # Show top 5
            total = sum(counts.values())
            large_summary.append([domain, total, counts['properties'], counts['processes'], counts['perspectives']])

        table = ax4.table(cellText=large_summary,
                         colLabels=['Domain', 'Total', 'Properties', 'Processes', 'Perspectives'],
                         cellLoc='center', loc='center', colColours=['lightgray']*5)
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.5)
        ax4.set_title('Large Dataset - Domain Breakdown', fontsize=12, fontweight='bold')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    statistics_dir = session_path / "visualizations" / "statistics"
    statistics_dir.mkdir(parents=True, exist_ok=True)
    output_path = statistics_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_statistical_overview(small_framework: P3IFFramework,
                               large_framework: P3IFFramework,
                               session_path: Path,
                               filename: str,
                               title: str,
                               colors: Dict[str, str]):
    """Create a comprehensive statistical overview."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))

    # Calculate comprehensive statistics
    small_stats = _calculate_framework_stats(small_framework)
    large_stats = _calculate_framework_stats(large_framework)

    # Patterns vs Relationships comparison
    datasets = ['Small Dataset', 'Large Dataset']
    pattern_counts = [small_stats['total_patterns'], large_stats['total_patterns']]
    relationship_counts = [small_stats['total_relationships'], large_stats['total_relationships']]

    x = np.arange(len(datasets))
    width = 0.35

    ax1.bar(x - width/2, pattern_counts, width, label='Patterns', color=colors['property'], alpha=0.8)
    ax1.bar(x + width/2, relationship_counts, width, label='Relationships', color=colors['process'], alpha=0.8)

    ax1.set_xlabel('Dataset')
    ax1.set_ylabel('Count')
    ax1.set_title('Patterns vs Relationships')
    ax1.set_xticks(x)
    ax1.set_xticklabels(datasets)
    ax1.legend()

    # Component type breakdown
    small_components = [small_stats['properties'], small_stats['processes'], small_stats['perspectives']]
    large_components = [large_stats['properties'], large_stats['processes'], large_stats['perspectives']]

    ax2.bar(datasets, small_components, label='Small', color=colors['property'], alpha=0.7)
    ax2.bar(datasets, large_components, bottom=small_components, label='Large', color=colors['process'], alpha=0.7)

    ax2.set_xlabel('Dataset')
    ax2.set_ylabel('Component Count')
    ax2.set_title('Component Breakdown')
    ax2.legend()

    # Quality metrics comparison
    small_quality = small_stats['avg_quality']
    large_quality = large_stats['avg_quality']

    ax3.bar(['Small Dataset', 'Large Dataset'], [small_quality, large_quality],
           color=[colors['property'], colors['process']], alpha=0.8)
    ax3.set_ylabel('Average Quality Score')
    ax3.set_title('Quality Metrics Comparison')

    # Add value labels
    ax3.text(0, small_quality + 0.01, f'{small_quality:.2f}', ha='center', va='bottom', fontweight='bold')
    ax3.text(1, large_quality + 0.01, f'{large_quality:.2f}', ha='center', va='bottom', fontweight='bold')

    # Statistical summary
    ax4.axis('off')

    summary_text = f"""
    Comprehensive Statistical Overview:

    Small Dataset:
    • Total Patterns: {small_stats['total_patterns']}
    • Total Relationships: {small_stats['total_relationships']}
    • Properties: {small_stats['properties']}
    • Processes: {small_stats['processes']}
    • Perspectives: {small_stats['perspectives']}
    • Average Quality: {small_stats['avg_quality']:.2f}
    • Domains: {small_stats['domains']}

    Large Dataset:
    • Total Patterns: {large_stats['total_patterns']}
    • Total Relationships: {large_stats['total_relationships']}
    • Properties: {large_stats['properties']}
    • Processes: {large_stats['processes']}
    • Perspectives: {large_stats['perspectives']}
    • Average Quality: {large_stats['avg_quality']:.2f}
    • Domains: {large_stats['domains']}

    Ratio (Large/Small):
    • Patterns: {large_stats['total_patterns']/small_stats['total_patterns']:.1f}x
    • Relationships: {large_stats['total_relationships']/small_stats['total_relationships']:.1f}x
    • Quality: {large_stats['avg_quality']/small_stats['avg_quality']:.2f}x
    """

    ax4.text(0.1, 0.9, summary_text, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    ax4.set_title('Statistical Summary', fontsize=12, fontweight='bold')

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    statistics_dir = session_path / "visualizations" / "statistics"
    statistics_dir.mkdir(parents=True, exist_ok=True)
    output_path = statistics_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _calculate_framework_stats(framework: P3IFFramework) -> Dict[str, Any]:
    """Calculate comprehensive statistics for a framework."""
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    # Calculate quality scores
    quality_scores = [getattr(p, 'quality_score', 1.0) for p in framework._patterns.values()]
    avg_quality = np.mean(quality_scores) if quality_scores else 0

    # Get unique domains
    domains = len(set(p.domain for p in framework._patterns.values()))

    return {
        'total_patterns': len(framework._patterns),
        'total_relationships': len(framework._relationships),
        'properties': len(properties),
        'processes': len(processes),
        'perspectives': len(perspectives),
        'avg_quality': avg_quality,
        'domains': domains
    }
