#!/usr/bin/env python3
"""
P3IF List Visualizations

Generates detailed list visualizations for each P3IF component type,
showing Properties, Processes, and Perspectives in structured formats.
"""
import logging
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from matplotlib.table import Table

from p3if_methods.framework import P3IFFramework
from p3if_methods.models import Property, Process, Perspective

logger = logging.getLogger(__name__)


def generate_list_visualizations(small_framework: P3IFFramework,
                               large_framework: P3IFFramework,
                               session_path: Path):
    """Generate all list visualizations."""
    logger.info("📋 Generating list visualizations...")

    # Color scheme for P3IF components
    colors = {
        'property': '#FF6B6B',      # Red
        'process': '#4ECDC4',       # Cyan
        'perspective': '#45B7D1'    # Blue
    }

    # Generate lists for small dataset
    _create_properties_list(small_framework, session_path, "small_properties_list", "Small Dataset - Properties", colors)
    _create_processes_list(small_framework, session_path, "small_processes_list", "Small Dataset - Processes", colors)
    _create_perspectives_list(small_framework, session_path, "small_perspectives_list", "Small Dataset - Perspectives", colors)

    # Generate lists for large dataset
    _create_properties_list(large_framework, session_path, "large_properties_list", "Large Dataset - Properties", colors)
    _create_processes_list(large_framework, session_path, "large_processes_list", "Large Dataset - Processes", colors)
    _create_perspectives_list(large_framework, session_path, "large_perspectives_list", "Large Dataset - Perspectives", colors)

    # Generate comprehensive overview lists
    _create_comprehensive_overview(small_framework, large_framework, session_path, colors)


def _create_properties_list(framework: P3IFFramework,
                          session_path: Path,
                          filename: str,
                          title: str,
                          colors: Dict[str, str]):
    """Create a detailed list visualization of Properties."""
    # Get all properties
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]

    if not properties:
        logger.warning(f"No properties found in {filename}")
        return

    fig, ax = plt.subplots(1, 1, figsize=(12, len(properties) * 0.8 + 2))

    # Remove axes
    ax.axis('off')

    # Create table
    table_data = [['Property Name', 'Domain', 'Description', 'Tags', 'Quality Score']]

    for prop in properties:
        tags_str = ', '.join(prop.tags) if prop.tags else 'None'
        description = prop.description[:50] + '...' if len(prop.description) > 50 else prop.description

        table_data.append([
            prop.name,
            prop.domain,
            description,
            tags_str,
            f"{prop.quality_score:.2f}"
        ])

    # Create table
    table = Table(ax, bbox=[0, 0, 1, 1])

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)  # Make rows taller

    # Add cells
    for i, row in enumerate(table_data):
        for j, cell_text in enumerate(row):
            if i == 0:  # Header row
                table.add_cell(i, j, width=0.2, height=0.1,
                             text=cell_text, loc='center',
                             facecolor=colors['property'], edgecolor='black')
            else:  # Data rows
                if j == 0:  # Property name column
                    table.add_cell(i, j, width=0.2, height=0.1,
                                 text=cell_text, loc='left',
                                 facecolor='#FFE6E6', edgecolor='black')
                else:
                    table.add_cell(i, j, width=0.2, height=0.1,
                                 text=cell_text, loc='center',
                                 facecolor='white', edgecolor='black')

    ax.add_table(table)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()

    # Save
    lists_dir = session_path / "visualizations" / "lists"
    lists_dir.mkdir(parents=True, exist_ok=True)
    output_path = lists_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_processes_list(framework: P3IFFramework,
                         session_path: Path,
                         filename: str,
                         title: str,
                         colors: Dict[str, str]):
    """Create a detailed list visualization of Processes."""
    # Get all processes
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]

    if not processes:
        logger.warning(f"No processes found in {filename}")
        return

    fig, ax = plt.subplots(1, 1, figsize=(12, len(processes) * 0.8 + 2))

    # Remove axes
    ax.axis('off')

    # Create table
    table_data = [['Process Name', 'Domain', 'Description', 'Complexity', 'Automation Level']]

    for proc in processes:
        description = proc.description[:50] + '...' if len(proc.description) > 50 else proc.description
        complexity = getattr(proc, 'complexity', 'medium')
        automation = getattr(proc, 'automation_level', 'manual')

        table_data.append([
            proc.name,
            proc.domain,
            description,
            complexity,
            automation
        ])

    # Create table
    table = Table(ax, bbox=[0, 0, 1, 1])

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)  # Make rows taller

    # Add cells
    for i, row in enumerate(table_data):
        for j, cell_text in enumerate(row):
            if i == 0:  # Header row
                table.add_cell(i, j, width=0.2, height=0.1,
                             text=cell_text, loc='center',
                             facecolor=colors['process'], edgecolor='black')
            else:  # Data rows
                if j == 0:  # Process name column
                    table.add_cell(i, j, width=0.2, height=0.1,
                                 text=cell_text, loc='left',
                                 facecolor='#E6F7FF', edgecolor='black')
                else:
                    table.add_cell(i, j, width=0.2, height=0.1,
                                 text=cell_text, loc='center',
                                 facecolor='white', edgecolor='black')

    ax.add_table(table)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()

    # Save
    lists_dir = session_path / "visualizations" / "lists"
    lists_dir.mkdir(parents=True, exist_ok=True)
    output_path = lists_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_perspectives_list(framework: P3IFFramework,
                            session_path: Path,
                            filename: str,
                            title: str,
                            colors: Dict[str, str]):
    """Create a detailed list visualization of Perspectives."""
    # Get all perspectives
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    if not perspectives:
        logger.warning(f"No perspectives found in {filename}")
        return

    fig, ax = plt.subplots(1, 1, figsize=(12, len(perspectives) * 0.8 + 2))

    # Remove axes
    ax.axis('off')

    # Create table
    table_data = [['Perspective Name', 'Domain', 'Viewpoint', 'Stakeholder Type', 'Expertise Level']]

    for persp in perspectives:
        viewpoint = getattr(persp, 'viewpoint', 'general')
        stakeholder_type = getattr(persp, 'stakeholder_type', 'general')
        expertise_level = getattr(persp, 'expertise_level', 'intermediate')

        table_data.append([
            persp.name,
            persp.domain,
            viewpoint,
            stakeholder_type,
            expertise_level
        ])

    # Create table
    table = Table(ax, bbox=[0, 0, 1, 1])

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)  # Make rows taller

    # Add cells
    for i, row in enumerate(table_data):
        for j, cell_text in enumerate(row):
            if i == 0:  # Header row
                table.add_cell(i, j, width=0.2, height=0.1,
                             text=cell_text, loc='center',
                             facecolor=colors['perspective'], edgecolor='black')
            else:  # Data rows
                if j == 0:  # Perspective name column
                    table.add_cell(i, j, width=0.2, height=0.1,
                                 text=cell_text, loc='left',
                                 facecolor='#E6F3FF', edgecolor='black')
                else:
                    table.add_cell(i, j, width=0.2, height=0.1,
                                 text=cell_text, loc='center',
                                 facecolor='white', edgecolor='black')

    ax.add_table(table)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()

    # Save
    lists_dir = session_path / "visualizations" / "lists"
    lists_dir.mkdir(parents=True, exist_ok=True)
    output_path = lists_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _create_comprehensive_overview(small_framework: P3IFFramework,
                                 large_framework: P3IFFramework,
                                 session_path: Path,
                                 colors: Dict[str, str]):
    """Create a comprehensive overview of all P3IF components."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # Remove axes
    for ax in [ax1, ax2, ax3, ax4]:
        ax.axis('off')

    # Properties overview
    properties_small = len([p for p in small_framework._patterns.values() if isinstance(p, Property)])
    properties_large = len([p for p in large_framework._patterns.values() if isinstance(p, Property)])

    ax1.bar(['Small Dataset', 'Large Dataset'], [properties_small, properties_large],
           color=[colors['property'], colors['property']], alpha=0.7)
    ax1.set_title('Properties Overview', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Count')

    # Processes overview
    processes_small = len([p for p in small_framework._patterns.values() if isinstance(p, Process)])
    processes_large = len([p for p in large_framework._patterns.values() if isinstance(p, Process)])

    ax2.bar(['Small Dataset', 'Large Dataset'], [processes_small, processes_large],
           color=[colors['process'], colors['process']], alpha=0.7)
    ax2.set_title('Processes Overview', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Count')

    # Perspectives overview
    perspectives_small = len([p for p in small_framework._patterns.values() if isinstance(p, Perspective)])
    perspectives_large = len([p for p in large_framework._patterns.values() if isinstance(p, Perspective)])

    ax3.bar(['Small Dataset', 'Large Dataset'], [perspectives_small, perspectives_large],
           color=[colors['perspective'], colors['perspective']], alpha=0.7)
    ax3.set_title('Perspectives Overview', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Count')

    # Total comparison
    small_total = len(small_framework._patterns)
    large_total = len(large_framework._patterns)

    ax4.bar(['Small Dataset', 'Large Dataset'], [small_total, large_total],
           color=['#95A5A6', '#95A5A6'], alpha=0.7)
    ax4.set_title('Total P3IF Components', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Count')

    # Add summary text
    summary_text = f"""
    P3IF Component Summary:

    Small Dataset: {small_total} total components
    • Properties: {properties_small}
    • Processes: {processes_small}
    • Perspectives: {perspectives_small}

    Large Dataset: {large_total} total components
    • Properties: {properties_large}
    • Processes: {processes_large}
    • Perspectives: {perspectives_large}
    """

    fig.suptitle('Comprehensive P3IF Components Overview', fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    lists_dir = session_path / "visualizations" / "lists"
    lists_dir.mkdir(parents=True, exist_ok=True)
    output_path = lists_dir / "comprehensive_overview.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")
