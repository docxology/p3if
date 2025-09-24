#!/usr/bin/env python3
"""
P3IF Visualization Orchestrator

Coordinates multiple specialized visualization generators to create comprehensive
visual representations of Properties, Processes, and Perspectives.
"""
import logging
from pathlib import Path
from typing import Optional
import importlib.util
import sys

from p3if_methods.framework import P3IFFramework
from p3if_methods.models import Property, Process, Perspective, Relationship
from data.synthetic import SyntheticDataGenerator
from utils.output_organizer import create_standard_output_structure, get_output_organizer

logger = logging.getLogger(__name__)


class P3IFVisualizationOrchestrator:
    """Orchestrates multiple visualization generators."""

    def __init__(self, session_path: Path):
        """Initialize orchestrator with session tracking."""
        self.session_path = Path(session_path)
        self.output_organizer = get_output_organizer()

        # Create session structure
        self.session_path.mkdir(exist_ok=True)
        (self.session_path / "visualizations").mkdir(exist_ok=True)
        (self.session_path / "animations").mkdir(exist_ok=True)
        (self.session_path / "reports").mkdir(exist_ok=True)

        # Create datasets
        self.small_framework = self._create_small_dataset()
        self.large_framework = self._create_large_dataset()

        logger.info(f"Initialized P3IF Visualization Orchestrator in {self.session_path}")

    def _create_small_dataset(self) -> P3IFFramework:
        """Create small P3IF dataset."""
        logger.info("Creating small P3IF dataset...")
        framework = P3IFFramework()

        patterns = [
            Property(name="Patient Safety", domain="healthcare", description="Safety measures"),
            Property(name="Data Privacy", domain="healthcare", description="Privacy protection"),
            Process(name="Diagnosis", domain="healthcare", description="Diagnosis process"),
            Process(name="Treatment", domain="healthcare", description="Treatment process"),
            Perspective(name="Patient View", domain="healthcare", description="Patient perspective", viewpoint="patient_centered"),
            Perspective(name="Provider View", domain="healthcare", description="Provider perspective", viewpoint="clinical_expertise")
        ]

        for pattern in patterns:
            framework.add_pattern(pattern)

        # Generate relationships for small dataset
        self._generate_relationships(framework, num_relationships=20)

        logger.info(f"Created small dataset: {len(framework._patterns)} patterns, {len(framework._relationships)} relationships")
        return framework

    def _create_large_dataset(self) -> P3IFFramework:
        """Create large P3IF dataset."""
        logger.info("Creating large P3IF dataset...")
        framework = P3IFFramework()

        domains = ['healthcare', 'finance', 'education', 'technology']

        for domain in domains:
            for i in range(8):  # 8 of each type per domain
                prop = Property(
                    name=f"{domain.title()} Property {i+1}",
                    domain=domain,
                    description=f"Property {i+1} in {domain}"
                )
                framework.add_pattern(prop)

                proc = Process(
                    name=f"{domain.title()} Process {i+1}",
                    domain=domain,
                    description=f"Process {i+1} in {domain}"
                )
                framework.add_pattern(proc)

                persp = Perspective(
                    name=f"{domain.title()} Perspective {i+1}",
                    domain=domain,
                    description=f"Perspective {i+1} in {domain}",
                    viewpoint=f"view_{domain}_{i+1}"
                )
                framework.add_pattern(persp)

        # Generate relationships for large dataset
        self._generate_relationships(framework, num_relationships=150)

        logger.info(f"Created large dataset: {len(framework._patterns)} patterns, {len(framework._relationships)} relationships")
        return framework

    def _generate_relationships(self, framework: P3IFFramework, num_relationships: int = 50):
        """Generate relationships between P3IF components."""
        import random

        # Get all patterns organized by type
        properties = [p for p in framework._patterns.values() if isinstance(p, Property)]
        processes = [p for p in framework._patterns.values() if isinstance(p, Process)]
        perspectives = [p for p in framework._patterns.values() if isinstance(p, Perspective)]

        if not (properties and processes and perspectives):
            logger.warning("Insufficient patterns to generate relationships")
            return

        relationships_created = 0
        max_attempts = num_relationships * 3  # Prevent infinite loops
        attempts = 0

        while relationships_created < num_relationships and attempts < max_attempts:
            attempts += 1

            # Randomly select patterns
            prop = random.choice(properties) if properties else None
            proc = random.choice(processes) if processes else None
            persp = random.choice(perspectives) if perspectives else None

            # Ensure we have at least 2 different types
            selected_patterns = [p for p in [prop, proc, persp] if p is not None]
            if len(selected_patterns) < 2:
                continue

            # Create relationship with varying strengths and confidences
            strength = random.uniform(0.3, 1.0)
            confidence = random.uniform(0.6, 1.0)

            # Create relationship with guaranteed connections
            # Ensure at least 2 connections are present
            connections = []
            if prop and random.random() > 0.2:
                connections.append(('property', prop.id))
            if proc and random.random() > 0.2:
                connections.append(('process', proc.id))
            if persp and random.random() > 0.2:
                connections.append(('perspective', persp.id))

            # If we don't have enough connections, force some
            if len(connections) < 2:
                if not any(c[0] == 'property' for c in connections) and prop:
                    connections.append(('property', prop.id))
                elif not any(c[0] == 'process' for c in connections) and proc:
                    connections.append(('process', proc.id))
                elif not any(c[0] == 'perspective' for c in connections) and persp:
                    connections.append(('perspective', persp.id))

            # Ensure we have at least 2 connections
            if len(connections) >= 2:
                relationship = Relationship(
                    property_id=next((cid for ctype, cid in connections if ctype == 'property'), None),
                    process_id=next((cid for ctype, cid in connections if ctype == 'process'), None),
                    perspective_id=next((cid for ctype, cid in connections if ctype == 'perspective'), None),
                    strength=strength,
                    confidence=confidence,
                    relationship_type=random.choice(['general', 'causal', 'dependency', 'composition']),
                    bidirectional=random.random() > 0.5
                )

            try:
                framework.add_relationship(relationship)
                relationships_created += 1
            except Exception as e:
                # Skip duplicate relationships
                continue

        logger.info(f"Generated {relationships_created} relationships from {attempts} attempts")

    def _load_visualization_module(self, module_name: str):
        """Dynamically load a visualization module."""
        try:
            # Try to import directly first
            try:
                module = __import__(f"p3if_visualization.{module_name}", fromlist=[module_name])
                return module
            except ImportError:
                pass

            # Fallback to file path loading
            module_path = Path(__file__).parent / f"{module_name}.py"
            if module_path.exists():
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                return module

            logger.error(f"Module {module_name} not found")
            return None

        except Exception as e:
            logger.error(f"Failed to load {module_name}: {e}")
            return None

    def generate_network_visualizations(self):
        """Generate all network visualizations."""
        logger.info("🕸️ Generating network visualizations...")

        network_module = self._load_visualization_module("network_visualizations")
        if network_module:
            network_module.generate_network_visualizations(
                self.small_framework, self.large_framework, self.session_path
            )

    def generate_list_visualizations(self):
        """Generate list visualizations for P3IF components."""
        logger.info("📋 Generating list visualizations...")

        list_module = self._load_visualization_module("list_visualizations")
        if list_module:
            list_module.generate_list_visualizations(
                self.small_framework, self.large_framework, self.session_path
            )

    def generate_heatmap_visualizations(self):
        """Generate heatmap visualizations."""
        logger.info("🔥 Generating heatmap visualizations...")

        heatmap_module = self._load_visualization_module("heatmap_visualizations")
        if heatmap_module:
            heatmap_module.generate_heatmap_visualizations(
                self.small_framework, self.large_framework, self.session_path
            )

    def generate_3d_cube_visualizations(self):
        """Generate 3D cube visualizations."""
        logger.info("🎲 Generating 3D cube visualizations...")

        try:
            from p3if_visualization.cube_visualizations import generate_3d_cube_visualizations
            generate_3d_cube_visualizations(
                self.small_framework, self.large_framework, self.session_path
            )
        except Exception as e:
            logger.error(f"Failed to generate 3D cube visualizations: {e}")

    def generate_hierarchical_visualizations(self):
        """Generate hierarchical structure diagrams."""
        logger.info("🌳 Generating hierarchical visualizations...")

        try:
            from p3if_visualization.hierarchy_visualizations import generate_hierarchical_visualizations
            generate_hierarchical_visualizations(
                self.small_framework, self.large_framework, self.session_path
            )
        except Exception as e:
            logger.error(f"Failed to generate hierarchical visualizations: {e}")

    def generate_grid_visualizations(self):
        """Generate grid visualizations."""
        logger.info("🔲 Generating grid visualizations...")

        try:
            from p3if_visualization.grid_visualizations import generate_grid_visualizations
            generate_grid_visualizations(
                self.small_framework, self.large_framework, self.session_path
            )
        except Exception as e:
            logger.error(f"Failed to generate grid visualizations: {e}")

    def generate_matrix_visualizations(self):
        """Generate matrix visualizations."""
        logger.info("📊 Generating matrix visualizations...")

        matrix_module = self._load_visualization_module("matrix_visualizations")
        if matrix_module:
            matrix_module.generate_matrix_visualizations(
                self.small_framework, self.large_framework, self.session_path
            )

    def generate_statistical_visualizations(self):
        """Generate statistical charts."""
        logger.info("📈 Generating statistical visualizations...")

        try:
            from p3if_visualization.statistical_visualizations import generate_statistical_visualizations
            generate_statistical_visualizations(
                self.small_framework, self.large_framework, self.session_path
            )
        except Exception as e:
            logger.error(f"Failed to generate statistical visualizations: {e}")

    def generate_animation_visualizations(self):
        """Generate animation visualizations."""
        logger.info("🎬 Generating animation visualizations...")

        try:
            from p3if_visualization.animation_visualizations import generate_animation_visualizations
            generate_animation_visualizations(
                self.small_framework, self.large_framework, self.session_path
            )
        except Exception as e:
            logger.error(f"Failed to generate animation visualizations: {e}")

    def generate_grid_visualizations(self):
        """Generate grid visualizations."""
        logger.info("🔲 Generating grid visualizations...")

        try:
            from p3if_visualization.grid_visualizations import generate_grid_visualizations
            generate_grid_visualizations(
                self.small_framework, self.large_framework, self.session_path
            )
        except Exception as e:
            logger.error(f"Failed to generate grid visualizations: {e}")

    def generate_comprehensive_report(self) -> Path:
        """Generate comprehensive report of all visualizations."""
        logger.info("📋 Generating comprehensive report...")

        report_content = f"""# P3IF Comprehensive Visualization Report

Generated: {self._get_timestamp()}

## Session Information
- Session Path: {self.session_path}
- Small Dataset: {len(self.small_framework._patterns)} patterns
- Large Dataset: {len(self.large_framework._patterns)} patterns

## Generated Visualizations

### 🕸️ Network Visualizations
- General network graphs for small and large datasets
- Component-specific networks (Properties, Processes, Perspectives)
- Domain-specific networks

### 📋 List Visualizations
- Properties lists (detailed component listings)
- Processes lists (detailed component listings)
- Perspectives lists (detailed component listings)

### 🔥 Heatmap Visualizations
- P3IF relationship heatmaps
- Domain relationship heatmaps
- Connection strength matrices

### 🎲 3D Cube Visualizations
- P3IF 3D cube representations
- Dimension cube visualizations
- Multi-dimensional relationship cubes

### 🌳 Hierarchical Visualizations
- P3IF framework hierarchies
- Domain hierarchies
- Component relationship trees

### 📊 Matrix Visualizations
- Adjacency matrices
- Correlation matrices
- Relationship strength matrices

### 📈 Statistical Visualizations
- Pattern type distributions
- Domain distributions
- Confidence score analyses
- Quality metric visualizations

### 🎬 Animation Visualizations
- P3IF component rotations
- Framework evolution animations
- Dynamic relationship visualizations

## Features
- High resolution (300 DPI) outputs
- Real P3IF data with proper models
- Consistent color coding for P3IF components:
  - Properties: Red (#FF6B6B)
  - Processes: Cyan (#4ECDC4)
  - Perspectives: Blue (#45B7D1)
- Organized file structure
- Comprehensive metadata tracking

## File Organization
```
{self.session_path}/
├── visualizations/
│   ├── networks/          # Network graphs
│   ├── lists/            # Component lists
│   ├── heatmaps/         # Relationship heatmaps
│   ├── cubes/            # 3D visualizations
│   ├── hierarchies/      # Hierarchical diagrams
│   ├── matrices/         # Matrix visualizations
│   └── statistics/       # Statistical charts
├── animations/           # GIF animations
└── reports/             # Documentation
```

All files saved to organized output directories.
"""

        report_path = self.session_path / "reports" / "comprehensive_visualization_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"Generated comprehensive report: {report_path}")
        return report_path

    def count_generated_files(self) -> int:
        """Count total generated visualization files."""
        count = 0

        directories_to_check = [
            "visualizations/networks",
            "visualizations/lists",
            "visualizations/heatmaps",
            "visualizations/cubes",
            "visualizations/hierarchies",
            "visualizations/matrices",
            "visualizations/statistics",
            "animations"
        ]

        for dir_name in directories_to_check:
            dir_path = self.session_path / dir_name
            if dir_path.exists():
                for ext in ['*.png', '*.gif', '*.svg', '*.jpg']:
                    count += len(list(dir_path.glob(ext)))

        # Count report files
        reports_dir = self.session_path / "reports"
        if reports_dir.exists():
            count += len(list(reports_dir.glob("*.md")))

        return count

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _get_component_counts(self) -> dict:
        """Get counts of P3IF components."""
        small_props = len([p for p in self.small_framework._patterns.values() if isinstance(p, Property)])
        small_procs = len([p for p in self.small_framework._patterns.values() if isinstance(p, Process)])
        small_persps = len([p for p in self.small_framework._patterns.values() if isinstance(p, Perspective)])

        large_props = len([p for p in self.large_framework._patterns.values() if isinstance(p, Property)])
        large_procs = len([p for p in self.large_framework._patterns.values() if isinstance(p, Process)])
        large_persps = len([p for p in self.large_framework._patterns.values() if isinstance(p, Perspective)])

        return {
            'small_properties': small_props,
            'small_processes': small_procs,
            'small_perspectives': small_persps,
            'large_properties': large_props,
            'large_processes': large_procs,
            'large_perspectives': large_persps
        }
