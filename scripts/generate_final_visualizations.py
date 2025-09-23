#!/usr/bin/env python3
"""
Final P3IF Visualization Generator

Creates real PNG visualizations and GIF animations with working P3IF data.
"""
import os
import sys
import logging
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from pathlib import Path
from datetime import datetime
import pandas as pd
from PIL import Image
import io

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.framework import P3IFFramework
from core.models import Property, Process, Perspective
from utils.output_organizer import create_standard_output_structure, get_output_organizer

# Configure matplotlib
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FinalVisualizationGenerator:
    """Generates P3IF visualizations with working data."""

    def __init__(self):
        """Initialize generator."""
        self.session_path = create_standard_output_structure()
        self.output_organizer = get_output_organizer()
        
        # Create datasets
        self.small_framework = self._create_small_dataset()
        self.large_framework = self._create_large_dataset()
        
        # Colors
        self.colors = {
            'property': '#FF6B6B',
            'process': '#4ECDC4', 
            'perspective': '#45B7D1'
        }

    def _create_small_dataset(self) -> P3IFFramework:
        """Create small dataset."""
        logger.info("Creating small dataset...")
        framework = P3IFFramework()
        
        # Add patterns
        patterns = [
            Property(name="Patient Safety", domain="healthcare", description="Safety measures"),
            Property(name="Data Privacy", domain="healthcare", description="Privacy protection"),
            Process(name="Diagnosis", domain="healthcare", description="Diagnosis process"),
            Process(name="Treatment", domain="healthcare", description="Treatment process"),
            Perspective(name="Patient View", domain="healthcare", description="Patient perspective", viewpoint="patient"),
            Perspective(name="Provider View", domain="healthcare", description="Provider perspective", viewpoint="provider")
        ]
        
        for pattern in patterns:
            framework.add_pattern(pattern)
        
        logger.info(f"Created small dataset: {len(framework._patterns)} patterns")
        return framework

    def _create_large_dataset(self) -> P3IFFramework:
        """Create large dataset."""
        logger.info("Creating large dataset...")
        framework = P3IFFramework()
        
        domains = ['healthcare', 'finance', 'education', 'technology']
        
        # Create patterns
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
                    viewpoint=f"view_{i+1}"
                )
                framework.add_pattern(persp)
        
        logger.info(f"Created large dataset: {len(framework._patterns)} patterns")
        return framework

    def generate_network_graphs(self):
        """Generate network visualizations."""
        logger.info("🕸️ Generating network graphs...")
        
        self._create_network_graph(self.small_framework, "small_network", "Small P3IF Network")
        self._create_network_graph(self.large_framework, "large_network", "Large P3IF Network")

    def _create_network_graph(self, framework: P3IFFramework, filename: str, title: str):
        """Create network graph."""
        fig, ax = plt.subplots(1, 1, figsize=(12, 9))
        
        # Create graph
        G = nx.Graph()
        
        # Add nodes
        for pattern_id, pattern in framework._patterns.items():
            G.add_node(pattern_id, 
                      name=pattern.name,
                      type=pattern.type.value,
                      domain=pattern.domain)
        
        # Simple connections between patterns of same domain
        pattern_items = list(framework._patterns.items())
        for i in range(len(pattern_items) - 1):
            id1, p1 = pattern_items[i]
            id2, p2 = pattern_items[i + 1]
            if p1.domain == p2.domain and p1.type != p2.type:
                G.add_edge(id1, id2)
        
        if len(G.nodes()) == 0:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
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
                                         node_size=400, alpha=0.8, ax=ax)
            
            # Draw edges
            if G.edges():
                nx.draw_networkx_edges(G, pos, alpha=0.5, ax=ax)
            
            # Labels for small graphs
            if len(G.nodes()) <= 12:
                labels = {n: d['name'][:8] for n, d in G.nodes(data=True)}
                nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.axis('off')
        
        # Legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colors['property'],
                      markersize=10, label='Properties'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colors['process'],
                      markersize=10, label='Processes'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colors['perspective'],
                      markersize=10, label='Perspectives')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        # Save
        output_path = self.output_organizer.get_visualization_path("networks", f"{filename}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        # Record file (method may not exist in this version)
        plt.close()
        
        logger.info(f"Generated: {output_path}")

    def generate_statistics(self):
        """Generate statistical charts."""
        logger.info("📊 Generating statistics...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # Get all patterns
        all_patterns = list(self.small_framework._patterns.values()) + list(self.large_framework._patterns.values())
        
        if all_patterns:
            # Type distribution
            types = [p.type.value for p in all_patterns]
            type_counts = pd.Series(types).value_counts()
            
            colors = [self.colors.get(t, '#95A5A6') for t in type_counts.index]
            ax1.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%', 
                   colors=colors, startangle=90)
            ax1.set_title('Pattern Type Distribution')
            
            # Domain distribution
            domains = [p.domain for p in all_patterns]
            domain_counts = pd.Series(domains).value_counts()
            
            ax2.bar(range(len(domain_counts)), domain_counts.values)
            ax2.set_xticks(range(len(domain_counts)))
            ax2.set_xticklabels(domain_counts.index, rotation=45)
            ax2.set_title('Domain Distribution')
            ax2.set_ylabel('Count')
            
            # Confidence distribution (use default confidence if attribute doesn't exist)
            confidences = [getattr(p, 'confidence', 1.0) for p in all_patterns]
            ax3.hist(confidences, bins=15, color=self.colors['process'], alpha=0.7)
            ax3.set_xlabel('Confidence Score')
            ax3.set_ylabel('Frequency')
            ax3.set_title('Confidence Distribution')
            
            # Pattern count by dataset
            datasets = ['Small Dataset'] * len(self.small_framework._patterns) + ['Large Dataset'] * len(self.large_framework._patterns)
            dataset_counts = pd.Series(datasets).value_counts()
            
            ax4.bar(dataset_counts.index, dataset_counts.values, color=['#FF9999', '#99CCFF'])
            ax4.set_title('Patterns by Dataset')
            ax4.set_ylabel('Count')
        
        plt.tight_layout()
        
        # Save
        output_path = self.output_organizer.get_visualization_path("statistics", "pattern_statistics.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        # Record file (method may not exist in this version)
        plt.close()
        
        logger.info(f"Generated: {output_path}")

    def generate_animations(self):
        """Generate GIF animations."""
        logger.info("🎬 Generating animations...")
        
        frames = []
        
        # Create rotating P3IF components
        for angle in range(0, 360, 30):  # 12 frames
            fig, ax = plt.subplots(1, 1, figsize=(8, 8))
            
            center_x, center_y = 0, 0
            radius = 2
            
            # Three rotating components
            components = [
                ('Properties', self.colors['property']),
                ('Processes', self.colors['process']),
                ('Perspectives', self.colors['perspective'])
            ]
            
            for i, (name, color) in enumerate(components):
                # Position
                comp_angle = angle + i * 120
                x = center_x + radius * np.cos(np.radians(comp_angle))
                y = center_y + radius * np.sin(np.radians(comp_angle))
                
                # Draw component
                circle = plt.Circle((x, y), 0.4, color=color, alpha=0.8)
                ax.add_patch(circle)
                ax.text(x, y, name[:4], ha='center', va='center', fontweight='bold', fontsize=9)
            
            # Center
            center_circle = plt.Circle((center_x, center_y), 0.25, color='#2C3E50', alpha=0.9)
            ax.add_patch(center_circle)
            ax.text(center_x, center_y, 'P3IF', ha='center', va='center', 
                   fontweight='bold', fontsize=10, color='white')
            
            ax.set_xlim(-3, 3)
            ax.set_ylim(-3, 3)
            ax.set_aspect('equal')
            ax.set_title(f'P3IF Framework Components', fontsize=12)
            ax.axis('off')
            
            # Convert to image
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
            buf.seek(0)
            frames.append(Image.open(buf).copy())
            buf.close()
            plt.close()
        
        if frames:
            # Save GIF
            output_path = self.output_organizer.get_animation_path("framework", "p3if_components.gif")
            frames[0].save(output_path, save_all=True, append_images=frames[1:], 
                          duration=300, loop=0, optimize=True)
            # Record file (method may not exist in this version)
            logger.info(f"Generated: {output_path}")

    def generate_report(self):
        """Generate report."""
        logger.info("📋 Generating report...")
        
        report_content = f"""# P3IF Visualization Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Datasets

### Small Dataset
- Patterns: {len(self.small_framework._patterns)}
- Domains: {len(set(p.domain for p in self.small_framework._patterns.values()))}

### Large Dataset  
- Patterns: {len(self.large_framework._patterns)}
- Domains: {len(set(p.domain for p in self.large_framework._patterns.values()))}

## Generated Files

### PNG Visualizations
- Network graphs showing pattern connections
- Statistical charts with distributions

### GIF Animations
- P3IF framework component rotation

## Features
- High resolution (300 DPI) outputs
- Real P3IF data with proper models
- Consistent color coding
- Organized file structure

All files saved to organized output directories.
"""
        
        # Save
        report_path = self.session_path / "reports" / "visualization_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_content, encoding='utf-8')
        # Record file (method may not exist in this version)
        
        logger.info(f"Generated: {report_path}")

    def run(self):
        """Run generation."""
        logger.info("🚀 Starting P3IF visualization generation...")
        
        try:
            self.generate_network_graphs()
            self.generate_statistics()
            self.generate_animations()
            self.generate_report()
            
            # Summary
            logger.info("\n" + "="*60)
            logger.info("🎉 P3IF VISUALIZATION GENERATION COMPLETE")
            logger.info("="*60)
            
            logger.info(f"\n📍 Files saved to: {self.session_path}")
            logger.info("\n✨ Generated:")
            logger.info("  📊 PNG network graphs and statistics")
            logger.info("  🎬 GIF animation")
            logger.info("  📋 Report")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            raise


def main():
    """Main function."""
    generator = FinalVisualizationGenerator()
    generator.run()


if __name__ == "__main__":
    main()
