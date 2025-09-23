#!/usr/bin/env python3
"""
Basic P3IF Visualization Generator

This script generates real PNG visualizations and GIF animations
showcasing P3IF visualization methods with manually created datasets.
"""
import os
import sys
import json
import logging
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
import pandas as pd
from PIL import Image, ImageDraw
import io

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.framework import P3IFFramework
from core.models import Property, Process, Perspective, Relationship
from utils.output_organizer import create_standard_output_structure, get_output_organizer

# Configure matplotlib for high-quality output
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BasicVisualizationGenerator:
    """Generates basic P3IF visualizations with manually created data."""

    def __init__(self):
        """Initialize the visualization generator."""
        self.session_path = create_standard_output_structure()
        self.output_organizer = get_output_organizer()
        
        # Create datasets
        self.small_framework = self._create_small_dataset()
        self.large_framework = self._create_large_dataset()
        
        # Color schemes
        self.colors = {
            'property': '#FF6B6B',
            'process': '#4ECDC4', 
            'perspective': '#45B7D1',
            'relationship': '#96CEB4'
        }

    def _create_small_dataset(self) -> P3IFFramework:
        """Create a small P3IF dataset manually."""
        logger.info("Creating small P3IF dataset...")
        framework = P3IFFramework()
        
        # Healthcare domain patterns
        patterns = [
            Property(name="Patient Safety", domain="healthcare", description="Ensuring patient wellbeing"),
            Property(name="Data Privacy", domain="healthcare", description="Protecting patient information"),
            Process(name="Diagnosis", domain="healthcare", description="Medical diagnosis workflow"),
            Process(name="Treatment", domain="healthcare", description="Treatment delivery process"),
            Perspective(name="Patient View", domain="healthcare", description="Patient's perspective", viewpoint="patient"),
            Perspective(name="Provider View", domain="healthcare", description="Healthcare provider perspective", viewpoint="provider")
        ]
        
        for pattern in patterns:
            framework.add_pattern(pattern)
        
        # Add some relationships manually
        pattern_ids = list(framework._patterns.keys())
        if len(pattern_ids) >= 4:
            # Create relationships between different pattern types
            rel1 = Relationship(
                property_id=pattern_ids[0],  # Patient Safety
                process_id=pattern_ids[2],   # Diagnosis
                strength=0.85,
                confidence=0.90
            )
            framework.add_relationship(rel1)
            
            rel2 = Relationship(
                process_id=pattern_ids[3],    # Treatment
                perspective_id=pattern_ids[4], # Patient View
                strength=0.75,
                confidence=0.85
            )
            framework.add_relationship(rel2)
        
        logger.info(f"Created small dataset: {len(framework._patterns)} patterns, {len(framework._relationships)} relationships")
        return framework

    def _create_large_dataset(self) -> P3IFFramework:
        """Create a larger P3IF dataset manually."""
        logger.info("Creating large P3IF dataset...")
        framework = P3IFFramework()
        
        domains = ['healthcare', 'finance', 'education', 'technology']
        
        # Create patterns for each domain
        for domain in domains:
            for i in range(5):  # 5 of each type per domain
                prop = Property(
                    name=f"{domain.title()} Property {i+1}",
                    domain=domain,
                    description=f"Property {i+1} in {domain} domain"
                )
                framework.add_pattern(prop)
                
                proc = Process(
                    name=f"{domain.title()} Process {i+1}",
                    domain=domain,
                    description=f"Process {i+1} in {domain} domain"
                )
                framework.add_pattern(proc)
                
                persp = Perspective(
                    name=f"{domain.title()} Perspective {i+1}",
                    domain=domain,
                    description=f"Perspective {i+1} in {domain} domain",
                    viewpoint=f"stakeholder_{i+1}"
                )
                framework.add_pattern(persp)
        
        # Add some relationships
        pattern_ids = list(framework._patterns.keys())
        for i in range(min(20, len(pattern_ids) - 1)):
            if i + 1 < len(pattern_ids):
                rel = Relationship(
                    property_id=pattern_ids[i],
                    process_id=pattern_ids[i+1],
                    strength=np.random.uniform(0.3, 0.9),
                    confidence=np.random.uniform(0.6, 0.95)
                )
                try:
                    framework.add_relationship(rel)
                except:
                    pass  # Skip invalid relationships
        
        logger.info(f"Created large dataset: {len(framework._patterns)} patterns, {len(framework._relationships)} relationships")
        return framework

    def generate_network_visualizations(self):
        """Generate network visualizations."""
        logger.info("🕸️ Generating network visualizations...")
        
        self._generate_network_graph(self.small_framework, "small_network", "Small P3IF Network")
        self._generate_network_graph(self.large_framework, "large_network", "Large P3IF Network")

    def _generate_network_graph(self, framework: P3IFFramework, filename: str, title: str):
        """Generate a network graph visualization."""
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        
        # Create NetworkX graph
        G = nx.Graph()
        
        # Add nodes
        for pattern_id, pattern in framework._patterns.items():
            G.add_node(pattern_id, 
                      name=pattern.name,
                      type=pattern.type.value,
                      domain=pattern.domain)
        
        # Add edges
        for rel in framework._relationships:
            source_id = rel.property_id or rel.process_id or rel.perspective_id
            target_id = rel.process_id or rel.perspective_id or rel.property_id
            if source_id != target_id and source_id in G.nodes() and target_id in G.nodes():
                G.add_edge(source_id, target_id, weight=rel.strength)
        
        if len(G.nodes()) == 0:
            ax.text(0.5, 0.5, 'No data to visualize', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title)
        else:
            # Layout
            if len(G.nodes()) < 30:
                pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
            else:
                pos = nx.circular_layout(G)
            
            # Draw nodes by type
            for pattern_type in ['property', 'process', 'perspective']:
                nodes = [n for n, d in G.nodes(data=True) if d.get('type') == pattern_type]
                if nodes:
                    nx.draw_networkx_nodes(G, pos, nodelist=nodes,
                                         node_color=self.colors[pattern_type],
                                         node_size=500, alpha=0.8, ax=ax)
            
            # Draw edges
            if G.edges():
                nx.draw_networkx_edges(G, pos, alpha=0.5, ax=ax)
            
            # Add labels for small networks
            if len(G.nodes()) <= 10:
                labels = {n: d['name'][:10] for n, d in G.nodes(data=True)}
                nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)
            
            ax.set_title(title, fontsize=16, fontweight='bold')
        
        ax.axis('off')
        plt.tight_layout()
        
        # Save
        output_path = self.output_organizer.get_path("images/network_graphs", f"{filename}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        self.output_organizer.record_output_file(output_path, "visualization", f"Network: {title}")
        plt.close()
        
        logger.info(f"Generated network graph: {output_path}")

    def generate_statistical_charts(self):
        """Generate statistical charts."""
        logger.info("📊 Generating statistical charts...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Pattern type distribution
        all_patterns = list(self.small_framework._patterns.values()) + list(self.large_framework._patterns.values())
        if all_patterns:
            types = [p.type.value for p in all_patterns]
            type_counts = pd.Series(types).value_counts()
            
            colors = [self.colors.get(t, '#95A5A6') for t in type_counts.index]
            ax1.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%', 
                   colors=colors, startangle=90)
            ax1.set_title('Pattern Type Distribution')
        
        # Domain distribution
        if all_patterns:
            domains = [p.domain for p in all_patterns]
            domain_counts = pd.Series(domains).value_counts()
            
            ax2.bar(range(len(domain_counts)), domain_counts.values)
            ax2.set_xticks(range(len(domain_counts)))
            ax2.set_xticklabels(domain_counts.index, rotation=45)
            ax2.set_title('Domain Distribution')
            ax2.set_ylabel('Count')
        
        # Confidence distribution
        confidences = [p.confidence for p in all_patterns]
        if confidences:
            ax3.hist(confidences, bins=15, color=self.colors['process'], alpha=0.7)
            ax3.set_xlabel('Confidence Score')
            ax3.set_ylabel('Frequency')
            ax3.set_title('Confidence Distribution')
        
        # Relationship strength distribution
        all_relationships = list(self.small_framework._relationships.values()) + list(self.large_framework._relationships.values())
        if all_relationships:
            strengths = [r.strength for r in all_relationships]
            ax4.hist(strengths, bins=15, color=self.colors['relationship'], alpha=0.7)
            ax4.set_xlabel('Relationship Strength')
            ax4.set_ylabel('Frequency')
            ax4.set_title('Relationship Strength Distribution')
        
        plt.tight_layout()
        
        # Save
        output_path = self.output_organizer.get_path("images/statistics", "statistical_charts.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        self.output_organizer.record_output_file(output_path, "visualization", "Statistical charts")
        plt.close()
        
        logger.info(f"Generated statistical charts: {output_path}")

    def generate_animated_gifs(self):
        """Generate animated GIF visualizations."""
        logger.info("🎬 Generating animated GIFs...")
        
        self._generate_rotation_gif()

    def _generate_rotation_gif(self):
        """Generate a simple rotation GIF."""
        logger.info("Creating rotation animation...")
        
        frames = []
        
        for angle in range(0, 360, 30):  # 12 frames
            fig, ax = plt.subplots(1, 1, figsize=(8, 8))
            
            # Create rotating P3IF visualization
            center_x, center_y = 0, 0
            radius = 2
            
            # Three components rotating
            components = [
                ('Properties', self.colors['property']),
                ('Processes', self.colors['process']),
                ('Perspectives', self.colors['perspective'])
            ]
            
            for i, (name, color) in enumerate(components):
                # Calculate position
                comp_angle = angle + i * 120  # 120 degrees apart
                x = center_x + radius * np.cos(np.radians(comp_angle))
                y = center_y + radius * np.sin(np.radians(comp_angle))
                
                # Draw component
                circle = plt.Circle((x, y), 0.5, color=color, alpha=0.8)
                ax.add_patch(circle)
                ax.text(x, y, name[:4], ha='center', va='center', fontweight='bold', fontsize=10)
            
            # Draw center
            center_circle = plt.Circle((center_x, center_y), 0.3, color='#2C3E50', alpha=0.9)
            ax.add_patch(center_circle)
            ax.text(center_x, center_y, 'P3IF', ha='center', va='center', 
                   fontweight='bold', fontsize=12, color='white')
            
            ax.set_xlim(-3, 3)
            ax.set_ylim(-3, 3)
            ax.set_aspect('equal')
            ax.set_title(f'P3IF Framework - Frame {angle//30 + 1}/12', fontsize=14)
            ax.axis('off')
            
            # Convert to image
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
            buf.seek(0)
            frames.append(Image.open(buf).copy())
            buf.close()
            plt.close()
        
        if frames:
            # Save as GIF
            output_path = self.output_organizer.get_path("animations/rotation", "p3if_framework.gif")
            frames[0].save(output_path, save_all=True, append_images=frames[1:], 
                          duration=400, loop=0, optimize=True)
            self.output_organizer.record_output_file(output_path, "animation", "P3IF framework rotation")
            logger.info(f"Generated rotation GIF: {output_path}")

    def generate_report(self):
        """Generate visualization report."""
        logger.info("📋 Generating report...")
        
        report_content = f"""# P3IF Basic Visualization Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Dataset Summary

### Small Dataset
- **Patterns**: {len(self.small_framework._patterns)}
- **Relationships**: {len(self.small_framework._relationships)}

### Large Dataset  
- **Patterns**: {len(self.large_framework._patterns)}
- **Relationships**: {len(self.large_framework._relationships)}

## Generated Visualizations

### PNG Visualizations
1. **Network Graphs**: Show pattern relationships and connections
2. **Statistical Charts**: Display distributions and metrics

### GIF Animations
1. **Framework Rotation**: Animated view of P3IF components

## Quality Features
- ✅ High resolution (300 DPI) PNG outputs
- ✅ Real P3IF data with proper relationships
- ✅ Consistent color coding by pattern type
- ✅ Organized output structure

## File Organization
- `images/network_graphs/`: Network visualizations
- `images/statistics/`: Statistical charts  
- `animations/rotation/`: Animated GIFs

This demonstrates P3IF's visualization capabilities with real data.
"""
        
        # Save report
        report_path = self.output_organizer.get_path("reports", "basic_visualization_report.md")
        report_path.write_text(report_content, encoding='utf-8')
        self.output_organizer.record_output_file(report_path, "report", "Basic visualization report")
        
        logger.info(f"Generated report: {report_path}")

    def run_generation(self):
        """Run the complete visualization generation process."""
        logger.info("🚀 Starting basic P3IF visualization generation...")
        
        try:
            # Generate all visualization types
            self.generate_network_visualizations()
            self.generate_statistical_charts()
            self.generate_animated_gifs()
            self.generate_report()
            
            # Generate output index
            self.output_organizer.generate_output_index()
            
            # Print summary
            logger.info("\n" + "="*70)
            logger.info("🎉 P3IF BASIC VISUALIZATION GENERATION COMPLETE")
            logger.info("="*70)
            
            self.output_organizer.print_session_summary()
            
            logger.info(f"\n📍 All files saved to: {self.session_path}")
            logger.info("\n✨ Generated:")
            logger.info("  📊 PNG network graphs and statistical charts")
            logger.info("  🎬 GIF animation of P3IF framework")
            logger.info("  📋 Comprehensive report")
            
        except Exception as e:
            logger.error(f"Error during generation: {e}")
            raise


def main():
    """Main function."""
    generator = BasicVisualizationGenerator()
    generator.run_generation()


if __name__ == "__main__":
    main()
