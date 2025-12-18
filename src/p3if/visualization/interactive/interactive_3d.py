"""
Interactive 3D Visualization for P3IF

This module provides advanced interactive 3D visualization capabilities for P3IF frameworks,
enabling users to explore Properties, Processes, and Perspectives in immersive 3D space.
"""

import json
import math
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
import logging
from datetime import datetime

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import numpy as np
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: Plotly not available. 3D visualization features will be limited.")


@dataclass
class Interactive3DVisualizer:
    """Advanced interactive 3D visualization for P3IF frameworks."""

    name: str = "interactive_3d_visualizer"
    framework_data: Dict[str, Any] = field(default_factory=dict)
    visualization_config: Dict[str, Any] = field(default_factory=dict)
    logger = logging.getLogger(__name__)

    def __post_init__(self):
        if not PLOTLY_AVAILABLE:
            self.logger.warning("Plotly not available. Some features will be limited.")

        # Default configuration
        self.visualization_config = {
            "dimensions": {
                "properties": {"range": [-5, 5], "color": "#FF6B6B", "size": 1.0},
                "processes": {"range": [-5, 5], "color": "#4ECDC4", "size": 1.0},
                "perspectives": {"range": [-5, 5], "color": "#45B7D1", "size": 1.0}
            },
            "relationships": {
                "line_color": "#666666",
                "line_width": 1,
                "opacity": 0.6
            },
            "animation": {
                "enabled": True,
                "duration": 1000,
                "easing": "cubic-in-out"
            }
        }

    def load_framework_data(self, data: Dict[str, Any]):
        """Load P3IF framework data for visualization."""
        self.framework_data = data

        # Validate data structure
        required_keys = ["properties", "processes", "perspectives", "relationships"]
        for key in required_keys:
            if key not in data:
                self.logger.warning(f"Missing key in framework data: {key}")

        self.logger.info(f"Loaded framework data with {len(data.get('properties', []))} properties, "
                        f"{len(data.get('processes', []))} processes, "
                        f"{len(data.get('perspectives', []))} perspectives")

    def create_3d_scatter_plot(self, dimension: str = "all") -> Any:
        """Create an interactive 3D scatter plot."""
        if not PLOTLY_AVAILABLE:
            return self._create_ascii_3d_representation()

        # Extract data for visualization
        if dimension == "all":
            return self._create_full_3d_visualization()
        elif dimension == "properties":
            return self._create_dimension_3d_visualization("properties")
        elif dimension == "processes":
            return self._create_dimension_3d_visualization("processes")
        elif dimension == "perspectives":
            return self._create_dimension_3d_visualization("perspectives")
        else:
            raise ValueError(f"Unknown dimension: {dimension}")

    def _create_full_3d_visualization(self) -> Any:
        """Create a full 3D visualization with all dimensions."""
        try:
            # Create figure with subplots
            fig = make_subplots(
                rows=2, cols=2,
                specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}],
                       [{'type': 'scatter3d'}, {'type': 'scatter'}]],
                subplot_titles=('Properties × Processes × Perspectives',
                              'Properties × Processes',
                              'Processes × Perspectives',
                              'Properties × Perspectives'),
                column_widths=[0.5, 0.5],
                row_heights=[0.5, 0.5]
            )

            # Add 3D scatter plots for each combination
            self._add_properties_processes_perspectives_3d(fig, 1, 1)
            self._add_properties_processes_2d(fig, 1, 2)
            self._add_processes_perspectives_2d(fig, 2, 1)
            self._add_properties_perspectives_2d(fig, 2, 2)

            # Update layout
            fig.update_layout(
                title="P3IF Framework: Interactive Multi-Dimensional Visualization",
                height=800,
                showlegend=True,
                scene=dict(
                    xaxis_title="Properties",
                    yaxis_title="Processes",
                    zaxis_title="Perspectives",
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                )
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating 3D visualization: {e}")
            return self._create_ascii_3d_representation()

    def _add_properties_processes_perspectives_3d(self, fig, row: int, col: int):
        """Add 3D scatter plot for Properties × Processes × Perspectives."""
        if not PLOTLY_AVAILABLE:
            return

        # Generate 3D coordinates for elements
        properties = self.framework_data.get("properties", [])
        processes = self.framework_data.get("processes", [])
        perspectives = self.framework_data.get("perspectives", [])

        # Create coordinate mappings
        prop_coords = {p["name"]: i for i, p in enumerate(properties)}
        proc_coords = {p["name"]: i for i, p in enumerate(processes)}
        pers_coords = {p["name"]: i for i, p in enumerate(perspectives)}

        # Add traces for each element type
        for element_type, elements, color in [
            ("Properties", properties, "#FF6B6B"),
            ("Processes", processes, "#4ECDC4"),
            ("Perspectives", perspectives, "#45B7D1")
        ]:
            if elements:
                x_coords = []
                y_coords = []
                z_coords = []
                names = []
                sizes = []

                for element in elements:
                    if element_type == "Properties":
                        x = len(prop_coords)
                        y = 0
                        z = 0
                    elif element_type == "Processes":
                        x = 0
                        y = len(proc_coords)
                        z = 0
                    else:  # Perspectives
                        x = 0
                        y = 0
                        z = len(pers_coords)

                    x_coords.append(x)
                    y_coords.append(y)
                    z_coords.append(z)
                    names.append(element.get("name", "Unknown"))
                    sizes.append(8)  # Fixed size for now

                fig.add_trace(
                    go.Scatter3d(
                        x=x_coords, y=y_coords, z=z_coords,
                        mode='markers+text',
                        marker=dict(
                            size=sizes,
                            color=color,
                            opacity=0.8,
                            symbol='circle'
                        ),
                        text=names,
                        textposition="top center",
                        name=element_type,
                        hovertemplate='<b>%{text}</b><br>Type: %{name}<extra></extra>'
                    ),
                    row=row, col=col
                )

    def _add_properties_processes_2d(self, fig, row: int, col: int):
        """Add 2D scatter plot for Properties × Processes."""
        # Simplified 2D representation
        pass

    def _add_processes_perspectives_2d(self, fig, row: int, col: int):
        """Add 2D scatter plot for Processes × Perspectives."""
        # Simplified 2D representation
        pass

    def _add_properties_perspectives_2d(self, fig, row: int, col: int):
        """Add 2D scatter plot for Properties × Perspectives."""
        # Simplified 2D representation
        pass

    def create_animated_visualization(self, animation_type: str = "rotation") -> Any:
        """Create an animated visualization."""
        if not PLOTLY_AVAILABLE:
            return self._create_ascii_animation()

        if animation_type == "rotation":
            return self._create_rotation_animation()
        elif animation_type == "dimension_transition":
            return self._create_dimension_transition_animation()
        elif animation_type == "relationship_evolution":
            return self._create_relationship_evolution_animation()
        else:
            raise ValueError(f"Unknown animation type: {animation_type}")

    def _create_rotation_animation(self) -> Any:
        """Create a rotation animation showing P3IF dimensions."""
        try:
            frames = []

            # Create 12 frames for a full rotation (30° steps)
            for angle in range(0, 360, 30):
                # Calculate rotated positions
                properties_pos = self._calculate_rotated_positions("properties", angle)
                processes_pos = self._calculate_rotated_positions("processes", angle + 120)
                perspectives_pos = self._calculate_rotated_positions("perspectives", angle + 240)

                frame_data = []

                # Add properties
                frame_data.append(go.Scatter3d(
                    x=[pos[0] for pos in properties_pos],
                    y=[pos[1] for pos in properties_pos],
                    z=[pos[2] for pos in properties_pos],
                    mode='markers+text',
                    marker=dict(size=8, color='#FF6B6B', opacity=0.8),
                    text=[f"Prop {i}" for i in range(len(properties_pos))],
                    name="Properties"
                ))

                # Add processes
                frame_data.append(go.Scatter3d(
                    x=[pos[0] for pos in processes_pos],
                    y=[pos[1] for pos in processes_pos],
                    z=[pos[2] for pos in processes_pos],
                    mode='markers+text',
                    marker=dict(size=8, color='#4ECDC4', opacity=0.8),
                    text=[f"Proc {i}" for i in range(len(processes_pos))],
                    name="Processes"
                ))

                # Add perspectives
                frame_data.append(go.Scatter3d(
                    x=[pos[0] for pos in perspectives_pos],
                    y=[pos[1] for pos in perspectives_pos],
                    z=[pos[2] for pos in perspectives_pos],
                    mode='markers+text',
                    marker=dict(size=8, color='#45B7D1', opacity=0.8),
                    text=[f"Pers {i}" for i in range(len(perspectives_pos))],
                    name="Perspectives"
                ))

                frames.append(go.Frame(data=frame_data, name=str(angle)))

            # Create figure with first frame
            fig = go.Figure(
                data=frames[0].data,
                frames=frames
            )

            # Add animation controls
            fig.update_layout(
                title="P3IF Framework: Animated Component Rotation",
                updatemenus=[{
                    'type': 'buttons',
                    'showactive': False,
                    'buttons': [
                        {
                            'label': 'Play',
                            'method': 'animate',
                            'args': [None, {'frame': {'duration': 500, 'redraw': True},
                                         'fromcurrent': True, 'mode': 'immediate'}]
                        },
                        {
                            'label': 'Pause',
                            'method': 'animate',
                            'args': [[None], {'frame': {'duration': 0, 'redraw': False},
                                           'mode': 'immediate', 'transition': {'duration': 0}}]
                        }
                    ]
                }],
                scene=dict(
                    xaxis_title="X Axis",
                    yaxis_title="Y Axis",
                    zaxis_title="Z Axis"
                )
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating rotation animation: {e}")
            return self._create_ascii_animation()

    def _calculate_rotated_positions(self, dimension: str, angle_degrees: int,
                                   radius: float = 3.0) -> List[Tuple[float, float, float]]:
        """Calculate rotated positions for animation."""
        angle_radians = math.radians(angle_degrees)
        positions = []

        # Number of elements based on dimension
        if dimension == "properties":
            element_count = len(self.framework_data.get("properties", []))
        elif dimension == "processes":
            element_count = len(self.framework_data.get("processes", []))
        elif dimension == "perspectives":
            element_count = len(self.framework_data.get("perspectives", []))
        else:
            element_count = 4  # Default

        for i in range(element_count):
            element_angle = (2 * math.pi * i) / element_count
            x = radius * math.cos(element_angle + angle_radians)
            y = radius * math.sin(element_angle + angle_radians)
            z = 0  # Keep in plane for now
            positions.append((x, y, z))

        return positions

    def _create_ascii_3d_representation(self) -> str:
        """Create an ASCII art representation when Plotly is not available."""
        ascii_art = """
        P3IF Interactive 3D Visualization (ASCII Representation)

        ┌─────────────────────────────────────────────────────────┐
        │                    Properties (X)                       │
        │  • Property 1                    • Property 2           │
        │  • Property 3                    • Property 4           │
        │                                                         │
        │  Processes (Y)               Perspectives (Z)          │
        │  • Process 1     • Perspective 1     • Perspective 2    │
        │  • Process 2     • Perspective 3     • Perspective 4    │
        │  • Process 3                                            │
        │  • Process 4                                            │
        └─────────────────────────────────────────────────────────┘

        Relationships:
        Property 1 ↔ Process 1 ↔ Perspective 1
        Property 2 ↔ Process 2 ↔ Perspective 2
        Property 3 ↔ Process 3 ↔ Perspective 3
        Property 4 ↔ Process 4 ↔ Perspective 4

        Legend:
        • = Framework Element
        ↔ = Relationship
        """
        return ascii_art

    def _create_ascii_animation(self) -> str:
        """Create an ASCII animation representation."""
        frames = [
            """
            Frame 1 - 0° Rotation:
            Properties: • • • •
            Processes:    • • • •
            Perspectives:  • • • •
            """,
            """
            Frame 2 - 90° Rotation:
            Properties:   • • • •
            Processes: • • • •
            Perspectives: • • • •
            """,
            """
            Frame 3 - 180° Rotation:
            Properties: • • • •
            Processes: • • • •
            Perspectives: • • • •
            """,
            """
            Frame 4 - 270° Rotation:
            Properties: • • • •
            Processes:   • • • •
            Perspectives: • • • •
            """
        ]

        return "\n".join(frames)

    def _create_dimension_transition_animation(self) -> Any:
        """Create animation showing transitions between dimensions."""
        if not PLOTLY_AVAILABLE:
            return self._create_ascii_animation()

        # Create animation showing dimension transitions
        frames = []

        # Animation phases
        phases = ["properties", "processes", "perspectives", "combined"]

        for phase in phases:
            frame_data = []

            if phase == "properties":
                # Show only properties
                frame_data.append(go.Scatter3d(
                    x=[1, 2, 3, 4],
                    y=[0, 0, 0, 0],
                    z=[0, 0, 0, 0],
                    mode='markers+text',
                    marker=dict(size=12, color='#FF6B6B', opacity=1.0),
                    text=['Prop 1', 'Prop 2', 'Prop 3', 'Prop 4'],
                    name="Properties"
                ))
            elif phase == "processes":
                # Show only processes
                frame_data.append(go.Scatter3d(
                    x=[0, 0, 0, 0],
                    y=[1, 2, 3, 4],
                    z=[0, 0, 0, 0],
                    mode='markers+text',
                    marker=dict(size=12, color='#4ECDC4', opacity=1.0),
                    text=['Proc 1', 'Proc 2', 'Proc 3', 'Proc 4'],
                    name="Processes"
                ))
            elif phase == "perspectives":
                # Show only perspectives
                frame_data.append(go.Scatter3d(
                    x=[0, 0, 0, 0],
                    y=[0, 0, 0, 0],
                    z=[1, 2, 3, 4],
                    mode='markers+text',
                    marker=dict(size=12, color='#45B7D1', opacity=1.0),
                    text=['Pers 1', 'Pers 2', 'Pers 3', 'Pers 4'],
                    name="Perspectives"
                ))
            else:  # combined
                # Show all dimensions
                frame_data.extend([
                    go.Scatter3d(x=[1, 2, 3, 4], y=[0, 0, 0, 0], z=[0, 0, 0, 0],
                               mode='markers', marker=dict(size=8, color='#FF6B6B'),
                               name="Properties"),
                    go.Scatter3d(x=[0, 0, 0, 0], y=[1, 2, 3, 4], z=[0, 0, 0, 0],
                               mode='markers', marker=dict(size=8, color='#4ECDC4'),
                               name="Processes"),
                    go.Scatter3d(x=[0, 0, 0, 0], y=[0, 0, 0, 0], z=[1, 2, 3, 4],
                               mode='markers', marker=dict(size=8, color='#45B7D1'),
                               name="Perspectives")
                ])

            frames.append(go.Frame(data=frame_data, name=phase))

        # Create figure
        fig = go.Figure(data=frames[0].data, frames=frames)

        fig.update_layout(
            title="P3IF Dimension Transition Animation",
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [{
                    'label': 'Play Transition',
                    'method': 'animate',
                    'args': [None, {'frame': {'duration': 1500, 'redraw': True},
                                 'transition': {'duration': 500}}]
                }]
            }]
        )

        return fig

    def _create_relationship_evolution_animation(self) -> Any:
        """Create animation showing relationship evolution."""
        if not PLOTLY_AVAILABLE:
            return self._create_ascii_animation()

        # Create animation showing relationships forming over time
        frames = []
        relationships = [
            [(0, 1), (1, 2)],  # Initial relationships
            [(0, 1), (1, 2), (2, 3)],  # Add more
            [(0, 1), (1, 2), (2, 3), (3, 0)],  # Close the loop
            [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]  # Add diagonal
        ]

        for i, rels in enumerate(relationships):
            frame_data = []

            # Add nodes
            frame_data.append(go.Scatter3d(
                x=[0, 1, 2, 3], y=[0, 0, 0, 0], z=[0, 0, 0, 0],
                mode='markers+text',
                marker=dict(size=10, color='#FF6B6B'),
                text=[f'Node {j}' for j in range(4)],
                name="Framework Elements"
            ))

            # Add relationships as lines
            for start_idx, end_idx in rels:
                frame_data.append(go.Scatter3d(
                    x=[start_idx, end_idx],
                    y=[0, 0],
                    z=[0, 0],
                    mode='lines',
                    line=dict(color='#666666', width=2),
                    showlegend=False,
                    name=f"Relationship {start_idx}-{end_idx}"
                ))

            frames.append(go.Frame(data=frame_data, name=f"step_{i}"))

        fig = go.Figure(data=frames[0].data, frames=frames)

        fig.update_layout(
            title="P3IF Relationship Evolution Animation",
            scene=dict(
                xaxis_title="Framework Elements",
                yaxis_title="",
                zaxis_title=""
            ),
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [{
                    'label': 'Evolve Relationships',
                    'method': 'animate',
                    'args': [None, {'frame': {'duration': 1000, 'redraw': True},
                                 'transition': {'duration': 300}}]
                }]
            }]
        )

        return fig

    def export_visualization(self, fig: Any, format: str = "html",
                           filename: str = "p3if_visualization") -> str:
        """Export visualization to various formats."""
        if not PLOTLY_AVAILABLE:
            return "Export not available without Plotly"

        if format.lower() == "html":
            output_file = f"{filename}.html"
            fig.write_html(output_file)
            return output_file
        elif format.lower() == "json":
            output_file = f"{filename}.json"
            fig.write_json(output_file)
            return output_file
        elif format.lower() == "png":
            output_file = f"{filename}.png"
            fig.write_image(output_file)
            return output_file
        else:
            raise ValueError(f"Unsupported export format: {format}")
