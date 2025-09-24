"""
Animated Dimensions for P3IF

This module provides animation capabilities for P3IF dimensions,
enabling dynamic visualization of Properties, Processes, and Perspectives.
"""

import math
import json
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
import logging
from datetime import datetime

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.patches import Circle, Rectangle
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: Matplotlib not available. Animation features will be limited.")


@dataclass
class DimensionAnimator:
    """Advanced animator for P3IF dimensions."""

    name: str = "dimension_animator"
    framework_data: Dict[str, Any] = field(default_factory=dict)
    animation_config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not MATPLOTLIB_AVAILABLE:
            self.logger.warning("Matplotlib not available. Some features will be limited.")

        # Default animation configuration
        self.animation_config = {
            "dimensions": {
                "properties": {
                    "color": "#FF6B6B",
                    "shape": "circle",
                    "size_range": [50, 200],
                    "animation": "pulse"
                },
                "processes": {
                    "color": "#4ECDC4",
                    "shape": "square",
                    "size_range": [40, 180],
                    "animation": "rotate"
                },
                "perspectives": {
                    "color": "#45B7D1",
                    "shape": "triangle",
                    "size_range": [60, 220],
                    "animation": "bounce"
                }
            },
            "relationships": {
                "line_color": "#666666",
                "line_width": 2,
                "animation": "flow"
            },
            "layout": {
                "type": "orbital",
                "radius": 3.0,
                "center_x": 0,
                "center_y": 0
            }
        }

        self.logger = logging.getLogger(__name__)

    def load_framework_data(self, data: Dict[str, Any]):
        """Load P3IF framework data for animation."""
        self.framework_data = data
        self.logger.info(f"Loaded animation data with {len(data.get('properties', []))} properties, "
                        f"{len(data.get('processes', []))} processes, "
                        f"{len(data.get('perspectives', []))} perspectives")

    def create_orbit_animation(self, animation_type: str = "dimension_orbit") -> Any:
        """Create orbital animation of P3IF dimensions."""
        if not MATPLOTLIB_AVAILABLE:
            return self._create_ascii_orbit_animation()

        try:
            # Set up the figure and axis
            fig, ax = plt.subplots(figsize=(10, 10))
            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)
            ax.set_aspect('equal')
            ax.axis('off')

            # Set title
            ax.set_title('P3IF Framework: Animated Dimension Orbit', fontsize=16, fontweight='bold')

            # Create animation elements
            elements = self._create_animation_elements()

            # Create animation
            def animate(frame):
                ax.clear()
                ax.set_xlim(-5, 5)
                ax.set_ylim(-5, 5)
                ax.set_aspect('equal')
                ax.axis('off')
                ax.set_title('P3IF Framework: Animated Dimension Orbit', fontsize=16, fontweight='bold')

                # Update element positions
                angle = frame * 2 * math.pi / 60  # 60 frames for full rotation

                for element in elements:
                    element.update_position(angle)
                    element.draw(ax)

                # Draw relationships
                self._draw_relationships(ax, elements, angle)

                return ax

            # Create animation
            anim = animation.FuncAnimation(fig, animate, frames=60, interval=100, blit=False)

            return anim

        except Exception as e:
            self.logger.error(f"Error creating orbit animation: {e}")
            return self._create_ascii_orbit_animation()

    def _create_animation_elements(self) -> List[Any]:
        """Create animation elements for each dimension."""
        elements = []

        # Properties (red circles)
        properties = self.framework_data.get("properties", [])
        for i, prop in enumerate(properties):
            angle = (2 * math.pi * i) / len(properties) if properties else 0
            elements.append(AnimationElement(
                name=prop.get("name", f"Property {i}"),
                element_type="property",
                base_angle=angle,
                radius=2.0,
                color=self.animation_config["dimensions"]["properties"]["color"],
                size=100,
                animation_type="pulse"
            ))

        # Processes (teal squares)
        processes = self.framework_data.get("processes", [])
        for i, proc in enumerate(processes):
            angle = (2 * math.pi * i) / len(processes) if processes else math.pi
            elements.append(AnimationElement(
                name=proc.get("name", f"Process {i}"),
                element_type="process",
                base_angle=angle,
                radius=2.5,
                color=self.animation_config["dimensions"]["processes"]["color"],
                size=80,
                animation_type="rotate"
            ))

        # Perspectives (blue triangles)
        perspectives = self.framework_data.get("perspectives", [])
        for i, pers in enumerate(perspectives):
            angle = (2 * math.pi * i) / len(perspectives) if perspectives else 2 * math.pi / 3
            elements.append(AnimationElement(
                name=pers.get("name", f"Perspective {i}"),
                element_type="perspective",
                base_angle=angle,
                radius=3.0,
                color=self.animation_config["dimensions"]["perspectives"]["color"],
                size=120,
                animation_type="bounce"
            ))

        return elements

    def _draw_relationships(self, ax, elements: List[Any], angle: float):
        """Draw relationships between animated elements."""
        # Find elements by type
        properties = [e for e in elements if e.element_type == "property"]
        processes = [e for e in elements if e.element_type == "process"]
        perspectives = [e for e in elements if e.element_type == "perspective"]

        # Draw some example relationships
        if properties and processes:
            # Connect first property to first process
            prop_pos = properties[0].get_current_position()
            proc_pos = processes[0].get_current_position()
            ax.plot([prop_pos[0], proc_pos[0]], [prop_pos[1], proc_pos[1]],
                   color='#666666', linewidth=2, alpha=0.6, linestyle='--')

        if processes and perspectives:
            # Connect first process to first perspective
            proc_pos = processes[0].get_current_position()
            pers_pos = perspectives[0].get_current_position()
            ax.plot([proc_pos[0], pers_pos[0]], [proc_pos[1], pers_pos[1]],
                   color='#666666', linewidth=2, alpha=0.6, linestyle='--')

        if properties and perspectives:
            # Connect first property to first perspective
            prop_pos = properties[0].get_current_position()
            pers_pos = perspectives[0].get_current_position()
            ax.plot([prop_pos[0], pers_pos[0]], [prop_pos[1], pers_pos[1]],
                   color='#666666', linewidth=2, alpha=0.4, linestyle=':')

    def create_pulse_animation(self) -> Any:
        """Create a pulsing animation showing element importance."""
        if not MATPLOTLIB_AVAILABLE:
            return self._create_ascii_pulse_animation()

        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.set_xlim(-6, 6)
            ax.set_ylim(-4, 4)
            ax.set_aspect('equal')
            ax.axis('off')

            ax.set_title('P3IF Framework: Pulsing Element Animation', fontsize=16, fontweight='bold')

            # Create elements
            elements = self._create_animation_elements()

            def animate(frame):
                ax.clear()
                ax.set_xlim(-6, 6)
                ax.set_ylim(-4, 4)
                ax.set_aspect('equal')
                ax.axis('off')
                ax.set_title('P3IF Framework: Pulsing Element Animation', fontsize=16, fontweight='bold')

                # Update and draw elements
                for element in elements:
                    element.update_pulse(frame)
                    element.draw(ax)

                # Draw legend
                legend_elements = [
                    plt.Circle((0, 0), 1, color='#FF6B6B', alpha=0.7, label='Properties'),
                    plt.Rectangle((0, 0), 1, 1, color='#4ECDC4', alpha=0.7, label='Processes'),
                    plt.Polygon([[0, 0], [0.5, 1], [1, 0]], color='#45B7D1', alpha=0.7, label='Perspectives')
                ]

                for elem in legend_elements:
                    ax.add_patch(elem)

                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                ax.text(-5.5, -3.5, f'Frame: {frame}', fontsize=10)

            anim = animation.FuncAnimation(fig, animate, frames=100, interval=50, blit=False)
            return anim

        except Exception as e:
            self.logger.error(f"Error creating pulse animation: {e}")
            return self._create_ascii_pulse_animation()

    def _create_ascii_orbit_animation(self) -> str:
        """Create ASCII representation of orbital animation."""
        return """
        P3IF Orbital Animation (ASCII Representation)

        Frame 1: 0° Rotation
        Properties:   • • • •
        Processes:    • • • •
        Perspectives: • • • •

        Frame 2: 120° Rotation
        Properties:     • • • •
        Processes:  • • • •
        Perspectives:   • • • •

        Frame 3: 240° Rotation
        Properties: • • • •
        Processes:     • • • •
        Perspectives:     • • • •

        Legend:
        • = Framework Element
        """

    def _create_ascii_pulse_animation(self) -> str:
        """Create ASCII representation of pulse animation."""
        return """
        P3IF Pulse Animation (ASCII Representation)

        Frame 1: Normal Size
        Properties:   ● ● ● ●
        Processes:    ■ ■ ■ ■
        Perspectives: ▲ ▲ ▲ ▲

        Frame 2: Large Size
        Properties:   ⬤ ⬤ ⬤ ⬤
        Processes:    ⬛ ⬛ ⬛ ⬛
        Perspectives: ⬟ ⬟ ⬟ ⬟

        Frame 3: Small Size
        Properties:   • • • •
        Processes:    □ □ □ □
        Perspectives: △ △ △ △

        Legend:
        ●/⬤/• = Properties (pulsing)
        ■/⬛/□ = Processes (rotating)
        ▲/⬟/△ = Perspectives (bouncing)
        """


@dataclass
class AnimationElement:
    """A single animated element in the P3IF visualization."""

    name: str
    element_type: str
    base_angle: float
    radius: float
    color: str
    size: float
    animation_type: str

    # Animation state
    current_angle: float = 0.0
    pulse_phase: float = 0.0
    bounce_height: float = 0.0
    rotation_angle: float = 0.0

    def get_current_position(self) -> Tuple[float, float]:
        """Get current position of the element."""
        x = self.radius * math.cos(self.current_angle)
        y = self.radius * math.sin(self.current_angle)
        return (x, y)

    def update_position(self, global_angle: float):
        """Update position based on global animation angle."""
        self.current_angle = self.base_angle + global_angle

        # Apply element-specific animation
        if self.animation_type == "pulse":
            self.pulse_phase += 0.1
        elif self.animation_type == "rotate":
            self.rotation_angle += 0.05
        elif self.animation_type == "bounce":
            self.bounce_height = math.sin(self.pulse_phase) * 0.5
            self.pulse_phase += 0.1

    def update_pulse(self, frame: int):
        """Update for pulse animation."""
        self.pulse_phase = frame * 0.1

    def get_current_size(self) -> float:
        """Get current size based on animation state."""
        base_size = self.size

        if self.animation_type == "pulse":
            pulse_factor = 1.0 + 0.3 * math.sin(self.pulse_phase)
            return base_size * pulse_factor
        elif self.animation_type == "bounce":
            bounce_factor = 1.0 + 0.2 * abs(math.sin(self.pulse_phase))
            return base_size * bounce_factor
        else:
            return base_size

    def draw(self, ax):
        """Draw the element on the given axes."""
        x, y = self.get_current_position()
        current_size = self.get_current_size()

        if self.element_type == "property":
            # Draw as circle
            circle = Circle((x, y), current_size/100, color=self.color, alpha=0.7)
            ax.add_patch(circle)
            ax.text(x, y, self.name[:8], ha='center', va='center', fontsize=8, fontweight='bold')

        elif self.element_type == "process":
            # Draw as square with rotation
            half_size = current_size/100
            rect = Rectangle((x - half_size, y - half_size), half_size*2, half_size*2,
                           color=self.color, alpha=0.7, angle=math.degrees(self.rotation_angle))
            ax.add_patch(rect)
            ax.text(x, y, self.name[:6], ha='center', va='center', fontsize=7, fontweight='bold')

        elif self.element_type == "perspective":
            # Draw as triangle
            triangle_size = current_size/100
            triangle = plt.Polygon([
                [x, y + triangle_size],
                [x - triangle_size*0.8, y - triangle_size*0.8],
                [x + triangle_size*0.8, y - triangle_size*0.8]
            ], color=self.color, alpha=0.7)
            ax.add_patch(triangle)
            ax.text(x, y, self.name[:6], ha='center', va='center', fontsize=7, fontweight='bold')


def create_dimension_animator(framework_data: Dict[str, Any]) -> DimensionAnimator:
    """Create a dimension animator with the given framework data."""
    animator = DimensionAnimator()
    animator.load_framework_data(framework_data)
    return animator


def save_animation(animator, filename: str = "p3if_animation.gif", fps: int = 10) -> str:
    """Save animation to file."""
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot save animation: Matplotlib not available")
        return ""

    try:
        # Create animation
        anim = animator.create_orbit_animation()

        if hasattr(anim, 'save'):
            anim.save(filename, writer='pillow', fps=fps)
            return filename
        else:
            print("Animation object does not support saving")
            return ""

    except Exception as e:
        print(f"Error saving animation: {e}")
        return ""
