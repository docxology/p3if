#!/usr/bin/env python3
"""
P3IF 3D Cube Visualizations

Generates 3D cube representations showing Properties, Processes, and Perspectives
in three-dimensional space with proper P3IF labeling.
"""
import logging
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from pathlib import Path
from typing import Dict, Any
from matplotlib.patches import FancyBboxPatch

from p3if_methods.framework import P3IFFramework
from p3if_methods.models import Property, Process, Perspective

logger = logging.getLogger(__name__)


def generate_3d_cube_visualizations(small_framework: P3IFFramework,
                                  large_framework: P3IFFramework,
                                  session_path: Path):
    """Generate all 3D cube visualizations."""
    logger.info("🎲 Generating 3D cube visualizations...")

    # Color scheme for P3IF components
    colors = {
        'property': '#FF6B6B',      # Red
        'process': '#4ECDC4',       # Cyan
        'perspective': '#45B7D1'    # Blue
    }

    # Generate P3IF 3D cubes
    _create_3d_p3if_cube(small_framework, session_path, "small_3d_cube",
                        "Small Dataset - P3IF 3D Cube", colors)
    _create_3d_p3if_cube(large_framework, session_path, "large_3d_cube",
                        "Large Dataset - P3IF 3D Cube", colors)

    # Generate dimension cubes
    _create_p3if_dimension_cube(small_framework, session_path, "small_dimension_cube",
                               "Small Dataset - P3IF Dimension Cube", colors)
    _create_p3if_dimension_cube(large_framework, session_path, "large_dimension_cube",
                               "Large Dataset - P3IF Dimension Cube", colors)

    # Generate relationship cubes
    _create_relationship_cubes(small_framework, session_path, "small_relationship_cubes",
                              "Small Dataset - Relationship Cubes", colors)
    _create_relationship_cubes(large_framework, session_path, "large_relationship_cubes",
                              "Large Dataset - Relationship Cubes", colors)


def _create_3d_p3if_cube(framework: P3IFFramework,
                        session_path: Path,
                        filename: str,
                        title: str,
                        colors: Dict[str, str]):
    """Create a 3D cube representation of the P3IF framework."""
    # Get patterns by type
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Define cube dimensions (representing the three P3IF axes)
    cube_size = 10

    # Draw the main P3IF cube
    _draw_cube_frame(ax, cube_size)

    # Position patterns within the cube
    prop_positions = _position_properties_in_cube(properties, cube_size)
    proc_positions = _position_processes_in_cube(processes, cube_size)
    persp_positions = _position_perspectives_in_cube(perspectives, cube_size)

    # Plot Properties (X-axis)
    if prop_positions:
        x, y, z = zip(*prop_positions)
        ax.scatter(x, y, z, c=colors['property'], s=100, alpha=0.8, label='Properties')

        # Add labels for Properties
        for i, (px, py, pz) in enumerate(prop_positions):
            if i < 5:  # Only label first few to avoid clutter
                ax.text(px + 0.5, py, pz, properties[i].name[:10], fontsize=8,
                       bbox=dict(boxstyle='round', facecolor=colors['property'], alpha=0.7))

    # Plot Processes (Y-axis)
    if proc_positions:
        x, y, z = zip(*proc_positions)
        ax.scatter(x, y, z, c=colors['process'], s=100, alpha=0.8, label='Processes')

        # Add labels for Processes
        for i, (px, py, pz) in enumerate(proc_positions):
            if i < 5:  # Only label first few to avoid clutter
                ax.text(px, py + 0.5, pz, processes[i].name[:10], fontsize=8,
                       bbox=dict(boxstyle='round', facecolor=colors['process'], alpha=0.7))

    # Plot Perspectives (Z-axis)
    if persp_positions:
        x, y, z = zip(*persp_positions)
        ax.scatter(x, y, z, c=colors['perspective'], s=100, alpha=0.8, label='Perspectives')

        # Add labels for Perspectives
        for i, (px, py, pz) in enumerate(persp_positions):
            if i < 5:  # Only label first few to avoid clutter
                ax.text(px, py, pz + 0.5, perspectives[i].name[:10], fontsize=8,
                       bbox=dict(boxstyle='round', facecolor=colors['perspective'], alpha=0.7))

    # Draw relationships as lines
    _draw_relationship_lines(ax, framework, colors, prop_positions, proc_positions, persp_positions)

    # Set labels and title
    ax.set_xlabel('Properties (P)', fontsize=12, fontweight='bold', color=colors['property'])
    ax.set_ylabel('Processes (P)', fontsize=12, fontweight='bold', color=colors['process'])
    ax.set_zlabel('Perspectives (P)', fontsize=12, fontweight='bold', color=colors['perspective'])

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    # Set equal aspect ratio and limits
    ax.set_xlim([-2, cube_size + 2])
    ax.set_ylim([-2, cube_size + 2])
    ax.set_zlim([-2, cube_size + 2])

    # Add legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))

    # Add P3IF framework label
    ax.text2D(0.02, 0.98, 'P3IF Framework Cube', transform=ax.transAxes,
             fontsize=14, fontweight='bold', verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))

    plt.tight_layout()

    # Save
    cubes_dir = session_path / "visualizations" / "cubes"
    cubes_dir.mkdir(parents=True, exist_ok=True)
    output_path = cubes_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _draw_cube_frame(ax, size: int):
    """Draw the frame of a 3D cube."""
    # Define cube vertices
    r = [-size/2, size/2]
    vertices = []
    for x in r:
        for y in r:
            for z in r:
                vertices.append((x, y, z))

    # Define edges
    edges = [
        (0,1), (1,3), (3,2), (2,0),  # Bottom face
        (4,5), (5,7), (7,6), (6,4),  # Top face
        (0,4), (1,5), (2,6), (3,7)   # Vertical edges
    ]

    # Draw edges
    for edge in edges:
        point1 = vertices[edge[0]]
        point2 = vertices[edge[1]]
        ax.plot3D(*zip(point1, point2), color='black', alpha=0.3, linewidth=1)

    # Add axis labels at cube corners
    ax.text(size/2 + 1, -size/2, -size/2, 'Properties (P)', color='red', fontweight='bold')
    ax.text(-size/2, size/2 + 1, -size/2, 'Processes (P)', color='cyan', fontweight='bold')
    ax.text(-size/2, -size/2, size/2 + 1, 'Perspectives (P)', color='blue', fontweight='bold')


def _position_properties_in_cube(properties: list, cube_size: int) -> list:
    """Position properties along the X-axis of the cube."""
    positions = []
    for i, prop in enumerate(properties):
        # Spread properties along X-axis
        x = (i / max(len(properties), 1)) * cube_size - cube_size/2
        y = np.random.uniform(-cube_size/2, cube_size/2)
        z = np.random.uniform(-cube_size/2, cube_size/2)
        positions.append((x, y, z))
    return positions


def _position_processes_in_cube(processes: list, cube_size: int) -> list:
    """Position processes along the Y-axis of the cube."""
    positions = []
    for i, proc in enumerate(processes):
        # Spread processes along Y-axis
        x = np.random.uniform(-cube_size/2, cube_size/2)
        y = (i / max(len(processes), 1)) * cube_size - cube_size/2
        z = np.random.uniform(-cube_size/2, cube_size/2)
        positions.append((x, y, z))
    return positions


def _position_perspectives_in_cube(perspectives: list, cube_size: int) -> list:
    """Position perspectives along the Z-axis of the cube."""
    positions = []
    for i, persp in enumerate(perspectives):
        # Spread perspectives along Z-axis
        x = np.random.uniform(-cube_size/2, cube_size/2)
        y = np.random.uniform(-cube_size/2, cube_size/2)
        z = (i / max(len(perspectives), 1)) * cube_size - cube_size/2
        positions.append((x, y, z))
    return positions


def _draw_relationship_lines(ax, framework: P3IFFramework, colors: Dict[str, str],
                           prop_positions: list, proc_positions: list, persp_positions: list):
    """Draw lines representing relationships between P3IF components."""
    # Create mapping from pattern ID to position
    prop_id_to_pos = {p.id: pos for p, pos in zip([p for p in framework._patterns.values() if isinstance(p, Property)], prop_positions)}
    proc_id_to_pos = {p.id: pos for p, pos in zip([p for p in framework._patterns.values() if isinstance(p, Process)], proc_positions)}
    persp_id_to_pos = {p.id: pos for p, pos in zip([p for p in framework._patterns.values() if isinstance(p, Perspective)], persp_positions)}

    # Draw relationship lines
    for rel in framework._relationships.values():
        connected_positions = []

        if rel.property_id and rel.property_id in prop_id_to_pos:
            connected_positions.append(prop_id_to_pos[rel.property_id])

        if rel.process_id and rel.process_id in proc_id_to_pos:
            connected_positions.append(proc_id_to_pos[rel.process_id])

        if rel.perspective_id and rel.perspective_id in persp_id_to_pos:
            connected_positions.append(persp_id_to_pos[rel.perspective_id])

        # Draw lines between connected components
        for i in range(len(connected_positions)):
            for j in range(i + 1, len(connected_positions)):
                pos1 = connected_positions[i]
                pos2 = connected_positions[j]
                ax.plot3D([pos1[0], pos2[0]], [pos1[1], pos2[1]], [pos1[2], pos2[2]],
                         color='gray', alpha=0.3, linewidth=1)


def _create_p3if_dimension_cube(framework: P3IFFramework,
                              session_path: Path,
                              filename: str,
                              title: str,
                              colors: Dict[str, str]):
    """Create a dimension cube showing the three P3IF dimensions clearly."""
    fig = plt.figure(figsize=(14, 12))

    # Create three subplots showing each dimension
    ax1 = fig.add_subplot(221, projection='3d')
    ax2 = fig.add_subplot(222, projection='3d')
    ax3 = fig.add_subplot(223, projection='3d')
    ax4 = fig.add_subplot(224)

    # Get patterns by type
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    cube_size = 8

    # Dimension 1: Properties (X-axis focus)
    _draw_dimension_focus(ax1, "Properties", properties, processes, perspectives,
                         cube_size, colors, focus_axis='x')

    # Dimension 2: Processes (Y-axis focus)
    _draw_dimension_focus(ax2, "Processes", properties, processes, perspectives,
                         cube_size, colors, focus_axis='y')

    # Dimension 3: Perspectives (Z-axis focus)
    _draw_dimension_focus(ax3, "Perspectives", properties, processes, perspectives,
                         cube_size, colors, focus_axis='z')

    # Summary visualization
    ax4.axis('off')
    _create_dimension_summary(ax4, properties, processes, perspectives, colors)

    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    cubes_dir = session_path / "visualizations" / "cubes"
    cubes_dir.mkdir(parents=True, exist_ok=True)
    output_path = cubes_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _draw_dimension_focus(ax, dimension_name: str, properties: list, processes: list,
                         perspectives: list, cube_size: int, colors: Dict[str, str],
                         focus_axis: str):
    """Draw a cube focusing on one dimension."""
    # Draw cube frame
    _draw_cube_frame(ax, cube_size)

    if focus_axis == 'x':
        # Focus on Properties (X-axis)
        prop_positions = _position_properties_in_cube(properties, cube_size)
        x, y, z = zip(*prop_positions)
        ax.scatter(x, y, z, c=colors['property'], s=150, alpha=0.9, label='Properties')

        # Add other components in background
        proc_positions = [(cube_size/2, cube_size/2, cube_size/2) for _ in processes]
        if proc_positions:
            x, y, z = zip(*proc_positions)
            ax.scatter(x, y, z, c=colors['process'], s=50, alpha=0.3)

        persp_positions = [(cube_size/2, cube_size/2, cube_size/2) for _ in perspectives]
        if persp_positions:
            x, y, z = zip(*persp_positions)
            ax.scatter(x, y, z, c=colors['perspective'], s=50, alpha=0.3)

        ax.set_xlabel('Properties (P)', fontsize=12, fontweight='bold', color=colors['property'])

    elif focus_axis == 'y':
        # Focus on Processes (Y-axis)
        proc_positions = _position_processes_in_cube(processes, cube_size)
        x, y, z = zip(*proc_positions)
        ax.scatter(x, y, z, c=colors['process'], s=150, alpha=0.9, label='Processes')

        # Add other components in background
        prop_positions = [(cube_size/2, cube_size/2, cube_size/2) for _ in properties]
        if prop_positions:
            x, y, z = zip(*prop_positions)
            ax.scatter(x, y, z, c=colors['property'], s=50, alpha=0.3)

        persp_positions = [(cube_size/2, cube_size/2, cube_size/2) for _ in perspectives]
        if persp_positions:
            x, y, z = zip(*persp_positions)
            ax.scatter(x, y, z, c=colors['perspective'], s=50, alpha=0.3)

        ax.set_ylabel('Processes (P)', fontsize=12, fontweight='bold', color=colors['process'])

    else:  # focus_axis == 'z'
        # Focus on Perspectives (Z-axis)
        persp_positions = _position_perspectives_in_cube(perspectives, cube_size)
        x, y, z = zip(*persp_positions)
        ax.scatter(x, y, z, c=colors['perspective'], s=150, alpha=0.9, label='Perspectives')

        # Add other components in background
        prop_positions = [(cube_size/2, cube_size/2, cube_size/2) for _ in properties]
        if prop_positions:
            x, y, z = zip(*prop_positions)
            ax.scatter(x, y, z, c=colors['property'], s=50, alpha=0.3)

        proc_positions = [(cube_size/2, cube_size/2, cube_size/2) for _ in processes]
        if proc_positions:
            x, y, z = zip(*proc_positions)
            ax.scatter(x, y, z, c=colors['process'], s=50, alpha=0.3)

        ax.set_zlabel('Perspectives (P)', fontsize=12, fontweight='bold', color=colors['perspective'])

    ax.set_title(f'{dimension_name} Dimension', fontsize=12, fontweight='bold')
    ax.set_xlim([-2, cube_size + 2])
    ax.set_ylim([-2, cube_size + 2])
    ax.set_zlim([-2, cube_size + 2])


def _create_dimension_summary(ax, properties: list, processes: list, perspectives: list, colors: Dict[str, str]):
    """Create a summary visualization of the three P3IF dimensions."""
    # Create dimension bars
    dimensions = ['Properties', 'Processes', 'Perspectives']
    counts = [len(properties), len(processes), len(perspectives)]
    colors_list = [colors['property'], colors['process'], colors['perspective']]

    bars = ax.bar(dimensions, counts, color=colors_list, alpha=0.8)

    # Add count labels
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{count}', ha='center', va='bottom', fontweight='bold')

    ax.set_title('P3IF Dimension Summary', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Components')

    # Add dimension descriptions
    descriptions = [
        "Properties (P)\nData attributes and\ncharacteristics",
        "Processes (P)\nActions, workflows,\nand procedures",
        "Perspectives (P)\nViewpoints, contexts,\nand frameworks"
    ]

    for i, (dim, desc) in enumerate(zip(dimensions, descriptions)):
        ax.text(i, -max(counts) * 0.15, desc, ha='center', va='top',
               fontsize=9, bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.7))


def _create_relationship_cubes(framework: P3IFFramework,
                             session_path: Path,
                             filename: str,
                             title: str,
                             colors: Dict[str, str]):
    """Create visualizations showing relationship cubes."""
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Get patterns and relationships
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    cube_size = 6

    # Draw cube frame
    _draw_cube_frame(ax, cube_size)

    # Position components
    prop_positions = _position_properties_in_cube(properties, cube_size)
    proc_positions = _position_processes_in_cube(processes, cube_size)
    persp_positions = _position_perspectives_in_cube(perspectives, cube_size)

    # Plot all components
    if prop_positions:
        x, y, z = zip(*prop_positions)
        ax.scatter(x, y, z, c=colors['property'], s=100, alpha=0.8, label='Properties')

    if proc_positions:
        x, y, z = zip(*proc_positions)
        ax.scatter(x, y, z, c=colors['process'], s=100, alpha=0.8, label='Processes')

    if persp_positions:
        x, y, z = zip(*persp_positions)
        ax.scatter(x, y, z, c=colors['perspective'], s=100, alpha=0.8, label='Perspectives')

    # Draw relationship connections as cubes
    _draw_relationship_connections(ax, framework, colors, prop_positions, proc_positions, persp_positions)

    # Set labels
    ax.set_xlabel('Properties (P)', fontsize=12, fontweight='bold', color=colors['property'])
    ax.set_ylabel('Processes (P)', fontsize=12, fontweight='bold', color=colors['process'])
    ax.set_zlabel('Perspectives (P)', fontsize=12, fontweight='bold', color=colors['perspective'])

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim([-2, cube_size + 2])
    ax.set_ylim([-2, cube_size + 2])
    ax.set_zlim([-2, cube_size + 2])

    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))

    plt.tight_layout()

    # Save
    cubes_dir = session_path / "visualizations" / "cubes"
    cubes_dir.mkdir(parents=True, exist_ok=True)
    output_path = cubes_dir / f"{filename}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"Generated: {output_path}")


def _draw_relationship_connections(ax, framework: P3IFFramework, colors: Dict[str, str],
                                 prop_positions: list, proc_positions: list, persp_positions: list):
    """Draw relationship connections as 3D elements."""
    # Create mapping from pattern ID to position
    prop_id_to_pos = {p.id: pos for p, pos in zip([p for p in framework._patterns.values() if isinstance(p, Property)], prop_positions)}
    proc_id_to_pos = {p.id: pos for p, pos in zip([p for p in framework._patterns.values() if isinstance(p, Process)], proc_positions)}
    persp_id_to_pos = {p.id: pos for p, pos in zip([p for p in framework._patterns.values() if isinstance(p, Perspective)], persp_positions)}

    # Draw relationship cubes/connections
    for rel in framework._relationships.values():
        connected_positions = []

        if rel.property_id and rel.property_id in prop_id_to_pos:
            connected_positions.append(prop_id_to_pos[rel.property_id])

        if rel.process_id and rel.process_id in proc_id_to_pos:
            connected_positions.append(proc_id_to_pos[rel.process_id])

        if rel.perspective_id and rel.perspective_id in persp_id_to_pos:
            connected_positions.append(persp_id_to_pos[rel.perspective_id])

        # Draw connection elements
        if len(connected_positions) >= 2:
            # Calculate center point of relationship
            center_x = sum(pos[0] for pos in connected_positions) / len(connected_positions)
            center_y = sum(pos[1] for pos in connected_positions) / len(connected_positions)
            center_z = sum(pos[2] for pos in connected_positions) / len(connected_positions)

            # Draw small cube at center representing the relationship
            cube_size = 0.3
            _draw_small_cube(ax, center_x, center_y, center_z, cube_size, 'gray', 0.6)
