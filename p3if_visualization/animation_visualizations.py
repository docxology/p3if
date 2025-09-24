#!/usr/bin/env python3
"""
P3IF Animation Visualizations

Generates animated GIF visualizations showing dynamic aspects of Properties,
Processes, and Perspectives relationships and evolution.
"""
import logging
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
import numpy as np
from pathlib import Path
from typing import Dict, Any
from PIL import Image
import io

from p3if_methods.framework import P3IFFramework
from p3if_methods.models import Property, Process, Perspective

logger = logging.getLogger(__name__)


def generate_animation_visualizations(small_framework: P3IFFramework,
                                    large_framework: P3IFFramework,
                                    session_path: Path):
    """Generate all animation visualizations."""
    logger.info("🎬 Generating animation visualizations...")

    # Color scheme for P3IF components
    colors = {
        'property': '#FF6B6B',      # Red
        'process': '#4ECDC4',       # Cyan
        'perspective': '#45B7D1'    # Blue
    }

    # Generate P3IF component rotation animation
    _create_p3if_rotation_animation(small_framework, large_framework, session_path,
                                   "p3if_components_rotation", "P3IF Components Rotation", colors)

    # Generate framework evolution animation
    _create_framework_evolution_animation(small_framework, large_framework, session_path,
                                        "framework_evolution", "Framework Evolution", colors)

    # Generate relationship dynamics animation
    _create_relationship_dynamics_animation(small_framework, large_framework, session_path,
                                          "relationship_dynamics", "Relationship Dynamics", colors)

    # Generate component interaction animation
    _create_component_interaction_animation(small_framework, large_framework, session_path,
                                          "component_interactions", "Component Interactions", colors)


def _create_p3if_rotation_animation(small_framework: P3IFFramework,
                                  large_framework: P3IFFramework,
                                  session_path: Path,
                                  filename: str,
                                  title: str,
                                  colors: Dict[str, str]):
    """Create an animation showing P3IF components rotating around the central framework."""
    logger.info(f"Creating P3IF rotation animation: {filename}")

    frames = []
    n_frames = 24  # 24 frames for smooth animation

    # Get component counts
    small_props = len([p for p in small_framework._patterns.values() if isinstance(p, Property)])
    small_procs = len([p for p in small_framework._patterns.values() if isinstance(p, Process)])
    small_persps = len([p for p in small_framework._patterns.values() if isinstance(p, Perspective)])

    large_props = len([p for p in large_framework._patterns.values() if isinstance(p, Property)])
    large_procs = len([p for p in large_framework._patterns.values() if isinstance(p, Process)])
    large_persps = len([p for p in large_framework._patterns.values() if isinstance(p, Perspective)])

    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

        # Remove axes
        ax.axis('off')
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)

        # Central P3IF core
        center_x, center_y = 0, 0
        center_circle = Circle((center_x, center_y), 0.8, color='black', alpha=0.9)
        ax.add_patch(center_circle)
        ax.text(center_x, center_y, 'P3IF', ha='center', va='center',
               fontweight='bold', fontsize=12, color='white')

        # Three rotating component groups
        components = [
            ('Properties (P)', colors['property'], small_props, large_props),
            ('Processes (P)', colors['process'], small_procs, large_procs),
            ('Perspectives (P)', colors['perspective'], small_persps, large_persps)
        ]

        for i, (name, color, small_count, large_count) in enumerate(components):
            # Position based on frame (rotating)
            angle = frame * (360 / n_frames) + i * 120  # 120 degrees apart
            radius = 3
            x = center_x + radius * np.cos(np.radians(angle))
            y = center_y + radius * np.sin(np.radians(angle))

            # Component circle
            comp_circle = Circle((x, y), 0.6, color=color, alpha=0.8)
            ax.add_patch(comp_circle)

            # Component label
            ax.text(x, y, name, ha='center', va='center', fontweight='bold', fontsize=10, color='white')

            # Component counts
            ax.text(x, y - 0.3, f'Small: {small_count}', ha='center', va='center', fontsize=8)
            ax.text(x, y - 0.5, f'Large: {large_count}', ha='center', va='center', fontsize=8)

            # Connecting lines to center
            ax.plot([center_x, x], [center_y, y], color=color, alpha=0.6, linewidth=2)

        # Add title with frame number
        ax.set_title(f'{title} - Frame {frame + 1}/{n_frames}', fontsize=14, fontweight='bold', pad=20)

        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        frames.append(Image.open(buf).copy())
        buf.close()
        plt.close()

    # Save as GIF
    if frames:
        animations_dir = session_path / "animations"
        animations_dir.mkdir(parents=True, exist_ok=True)
        output_path = animations_dir / f"{filename}.gif"
        frames[0].save(output_path, save_all=True, append_images=frames[1:],
                      duration=200, loop=0, optimize=True)
        logger.info(f"Generated: {output_path}")


def _create_framework_evolution_animation(small_framework: P3IFFramework,
                                        large_framework: P3IFFramework,
                                        session_path: Path,
                                        filename: str,
                                        title: str,
                                        colors: Dict[str, str]):
    """Create an animation showing framework evolution from small to large."""
    logger.info(f"Creating framework evolution animation: {filename}")

    frames = []
    n_frames = 16  # 16 frames for evolution sequence

    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))

        # Remove axes
        ax.axis('off')

        # Calculate interpolation factor
        t = frame / (n_frames - 1)  # 0 to 1

        # Interpolate between small and large datasets
        small_total = len(small_framework._patterns)
        large_total = len(large_framework._patterns)
        current_total = int(small_total + t * (large_total - small_total))

        # Show both frameworks side by side
        _draw_framework_snapshot(ax, small_framework, "Small Dataset", -0.35, colors, alpha=0.7)
        _draw_framework_snapshot(ax, large_framework, "Large Dataset", 0.35, colors, alpha=0.7)

        # Show evolution progress
        ax.add_patch(Rectangle((-0.6, -0.4), 1.2, 0.1, color='lightgray', alpha=0.8))
        ax.add_patch(Rectangle((-0.6, -0.4), t * 1.2, 0.1, color='lightblue', alpha=0.9))
        ax.text(0, -0.35, f'Evolution: {t*100:.0f}%', ha='center', va='center', fontweight='bold')

        ax.set_title(f'{title} - Evolution Step {frame + 1}/{n_frames}', fontsize=14, fontweight='bold')
        ax.set_xlim(-1, 1)
        ax.set_ylim(-0.5, 0.5)

        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        frames.append(Image.open(buf).copy())
        buf.close()
        plt.close()

    # Save as GIF
    if frames:
        animations_dir = session_path / "animations"
        animations_dir.mkdir(parents=True, exist_ok=True)
        output_path = animations_dir / f"{filename}.gif"
        frames[0].save(output_path, save_all=True, append_images=frames[1:],
                      duration=300, loop=0, optimize=True)
        logger.info(f"Generated: {output_path}")


def _draw_framework_snapshot(ax, framework: P3IFFramework, label: str, x_offset: float, colors: Dict[str, str], alpha: float):
    """Draw a snapshot of a framework at a given position."""
    # Get component counts
    properties = len([p for p in framework._patterns.values() if isinstance(p, Property)])
    processes = len([p for p in framework._patterns.values() if isinstance(p, Process)])
    perspectives = len([p for p in framework._patterns.values() if isinstance(p, Perspective)])

    # Draw component boxes
    box_width, box_height = 0.15, 0.1

    # Properties box
    ax.add_patch(Rectangle((x_offset - 0.15, 0.1), box_width, box_height,
                          color=colors['property'], alpha=alpha))
    ax.text(x_offset - 0.075, 0.15, f'P: {properties}', ha='center', va='center', fontsize=8, fontweight='bold')

    # Processes box
    ax.add_patch(Rectangle((x_offset - 0.15, 0.0), box_width, box_height,
                          color=colors['process'], alpha=alpha))
    ax.text(x_offset - 0.075, 0.05, f'Proc: {processes}', ha='center', va='center', fontsize=8, fontweight='bold')

    # Perspectives box
    ax.add_patch(Rectangle((x_offset - 0.15, -0.1), box_width, box_height,
                          color=colors['perspective'], alpha=alpha))
    ax.text(x_offset - 0.075, -0.05, f'Persp: {perspectives}', ha='center', va='center', fontsize=8, fontweight='bold')

    # Total count
    ax.text(x_offset + 0.1, 0.05, f'Total: {len(framework._patterns)}',
           ha='center', va='center', fontweight='bold', fontsize=10)

    # Label
    ax.text(x_offset, -0.25, label, ha='center', va='center', fontweight='bold')


def _create_relationship_dynamics_animation(small_framework: P3IFFramework,
                                          large_framework: P3IFFramework,
                                          session_path: Path,
                                          filename: str,
                                          title: str,
                                          colors: Dict[str, str]):
    """Create an animation showing relationship dynamics."""
    logger.info(f"Creating relationship dynamics animation: {filename}")

    frames = []
    n_frames = 20

    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))

        # Remove axes
        ax.axis('off')

        # Draw P3IF triangle
        _draw_p3if_triangle(ax, colors)

        # Show relationship formation
        small_rels = len(small_framework._relationships)
        large_rels = len(large_framework._relationships)
        current_rels = int(small_rels + (frame / (n_frames - 1)) * (large_rels - small_rels))

        # Draw relationships as connecting lines
        _draw_relationship_connections(ax, small_framework, colors, current_rels, frame)

        ax.set_title(f'{title} - Relationships: {current_rels}', fontsize=14, fontweight='bold')
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)

        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        frames.append(Image.open(buf).copy())
        buf.close()
        plt.close()

    # Save as GIF
    if frames:
        animations_dir = session_path / "animations"
        animations_dir.mkdir(parents=True, exist_ok=True)
        output_path = animations_dir / f"{filename}.gif"
        frames[0].save(output_path, save_all=True, append_images=frames[1:],
                      duration=250, loop=0, optimize=True)
        logger.info(f"Generated: {output_path}")


def _draw_p3if_triangle(ax, colors: Dict[str, str]):
    """Draw the P3IF triangle structure."""
    # Triangle vertices
    vertices = [
        (-1, -1.5),  # Properties
        (2, -1.5),   # Processes
        (0.5, 2)     # Perspectives
    ]

    # Draw triangle
    for i in range(3):
        ax.plot([vertices[i][0], vertices[(i+1)%3][0]],
               [vertices[i][1], vertices[(i+1)%3][1]],
               color='black', alpha=0.5, linewidth=2)

    # Label vertices
    labels = ['Properties (P)', 'Processes (P)', 'Perspectives (P)']
    for i, (x, y) in enumerate(vertices):
        color = list(colors.values())[i]
        ax.add_patch(Circle((x, y), 0.3, color=color, alpha=0.8))
        ax.text(x, y, labels[i], ha='center', va='center', fontweight='bold', color='white', fontsize=9)


def _draw_relationship_connections(ax, framework: P3IFFramework, colors: Dict[str, str],
                                 max_rels: int, frame: int):
    """Draw relationship connections within the triangle."""
    # Get all patterns organized by type
    properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
    processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
    perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

    # Triangle vertices
    vertices = [(-1, -1.5), (2, -1.5), (0.5, 2)]

    # Position patterns at vertices
    if properties:
        for i, prop in enumerate(properties[:3]):  # Up to 3 properties
            x, y = vertices[0]
            x += (i - 1) * 0.5  # Spread horizontally
            ax.add_patch(Circle((x, y), 0.15, color=colors['property'], alpha=0.8))

    if processes:
        for i, proc in enumerate(processes[:3]):  # Up to 3 processes
            x, y = vertices[1]
            x += (i - 1) * 0.5  # Spread horizontally
            ax.add_patch(Circle((x, y), 0.15, color=colors['process'], alpha=0.8))

    if perspectives:
        for i, persp in enumerate(perspectives[:3]):  # Up to 3 perspectives
            x, y = vertices[2]
            x += (i - 1) * 0.5  # Spread horizontally
            ax.add_patch(Circle((x, y), 0.15, color=colors['perspective'], alpha=0.8))

    # Draw relationships
    rels_to_draw = min(frame + 1, len(framework._relationships), max_rels)

    for i, rel in enumerate(list(framework._relationships.values())[:rels_to_draw]):
        alpha = min(1.0, (i + 1) / max(rels_to_draw, 1))  # Fade in effect, ensure 0-1 range

        # Find connected components
        connected_points = []
        if rel.property_id and properties:
            connected_points.append(vertices[0])
        if rel.process_id and processes:
            connected_points.append(vertices[1])
        if rel.perspective_id and perspectives:
            connected_points.append(vertices[2])

        # Draw connections
        if len(connected_points) >= 2:
            for j in range(len(connected_points)):
                for k in range(j + 1, len(connected_points)):
                    x1, y1 = connected_points[j]
                    x2, y2 = connected_points[k]
                    ax.plot([x1, x2], [y1, y2], color='gray', alpha=alpha * 0.6, linewidth=2)


def _create_component_interaction_animation(small_framework: P3IFFramework,
                                          large_framework: P3IFFramework,
                                          session_path: Path,
                                          filename: str,
                                          title: str,
                                          colors: Dict[str, str]):
    """Create an animation showing component interactions."""
    logger.info(f"Creating component interaction animation: {filename}")

    frames = []
    n_frames = 18

    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))

        # Remove axes
        ax.axis('off')

        # Draw interaction scene
        _draw_interaction_scene(ax, colors)

        # Show evolving interactions
        _draw_evolving_interactions(ax, small_framework, colors, frame, n_frames)

        ax.set_title(f'{title} - Interaction Frame {frame + 1}', fontsize=14, fontweight='bold')
        ax.set_xlim(-4, 4)
        ax.set_ylim(-3, 3)

        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        frames.append(Image.open(buf).copy())
        buf.close()
        plt.close()

    # Save as GIF
    if frames:
        animations_dir = session_path / "animations"
        animations_dir.mkdir(parents=True, exist_ok=True)
        output_path = animations_dir / f"{filename}.gif"
        frames[0].save(output_path, save_all=True, append_images=frames[1:],
                      duration=280, loop=0, optimize=True)
        logger.info(f"Generated: {output_path}")


def _draw_interaction_scene(ax, colors: Dict[str, str]):
    """Draw the basic interaction scene."""
    # Background elements
    ax.add_patch(Rectangle((-3, -2), 6, 4, color='lightblue', alpha=0.1))

    # Component areas
    ax.add_patch(Rectangle((-3, 0), 2, 2, color=colors['property'], alpha=0.2))
    ax.text(-2, 1, 'Properties (P)', ha='center', va='center', fontweight='bold')

    ax.add_patch(Rectangle((-1, 0), 2, 2, color=colors['process'], alpha=0.2))
    ax.text(0, 1, 'Processes (P)', ha='center', va='center', fontweight='bold')

    ax.add_patch(Rectangle((1, 0), 2, 2, color=colors['perspective'], alpha=0.2))
    ax.text(2, 1, 'Perspectives (P)', ha='center', va='center', fontweight='bold')


def _draw_evolving_interactions(ax, framework: P3IFFramework, colors: Dict[str, str],
                              frame: int, n_frames: int):
    """Draw evolving component interactions."""
    # Get component counts
    properties = len([p for p in framework._patterns.values() if isinstance(p, Property)])
    processes = len([p for p in framework._patterns.values() if isinstance(p, Process)])
    perspectives = len([p for p in framework._patterns.values() if isinstance(p, Perspective)])

    # Show components appearing
    progress = frame / (n_frames - 1)

    # Properties (appear first)
    if progress > 0.2:
        n_props = min(int(progress * properties), properties)
        for i in range(n_props):
            x = -2.5 + (i % 3) * 0.4
            y = 0.5 - (i // 3) * 0.3
            ax.add_patch(Circle((x, y), 0.08, color=colors['property'], alpha=0.8))

    # Processes (appear second)
    if progress > 0.4:
        n_procs = min(int((progress - 0.2) * processes * 2), processes)
        for i in range(n_procs):
            x = -0.5 + (i % 2) * 0.4
            y = 0.5 - (i // 2) * 0.3
            ax.add_patch(Circle((x, y), 0.08, color=colors['process'], alpha=0.8))

    # Perspectives (appear third)
    if progress > 0.6:
        n_persps = min(int((progress - 0.4) * perspectives * 2), perspectives)
        for i in range(n_persps):
            x = 1.5 + (i % 2) * 0.4
            y = 0.5 - (i // 2) * 0.3
            ax.add_patch(Circle((x, y), 0.08, color=colors['perspective'], alpha=0.8))

    # Show relationships forming
    if progress > 0.8:
        rel_progress = (progress - 0.6) * 5  # Scale up the last 20%
        n_rels = min(int(rel_progress * len(framework._relationships)), len(framework._relationships))

        for i, rel in enumerate(list(framework._relationships.values())[:n_rels]):
            # Draw relationship connection
            alpha = min(1.0, rel_progress - i * 0.1)
            ax.plot([-2.5, -0.5, 1.5], [0.5, 0.5, 0.5], color='gray', alpha=alpha * 0.5, linewidth=2)
