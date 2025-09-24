#!/usr/bin/env python3
"""
P3IF Comprehensive Visualization Orchestrator

Coordinates multiple specialized visualization generators to create comprehensive
visual representations of Properties, Processes, and Perspectives.
"""
import logging
from pathlib import Path
from datetime import datetime

from p3if_visualization.orchestrator import P3IFVisualizationOrchestrator
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class P3IFVisualizationCoordinator:
    """Coordinates all P3IF visualization generation."""

    def __init__(self):
        """Initialize coordinator with session tracking."""
        self.session_path = Path(f"p3if_visualizations_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.session_path.mkdir(exist_ok=True)

        logger.info(f"Created visualization session: {self.session_path}")

    def generate_comprehensive_visualizations(self):
        """Generate all types of P3IF visualizations."""
        logger.info("🚀 Starting comprehensive P3IF visualization generation...")

        try:
            # Initialize orchestrator
            orchestrator = P3IFVisualizationOrchestrator(self.session_path)

            # Generate all visualization types
            orchestrator.generate_network_visualizations()
            orchestrator.generate_list_visualizations()
            orchestrator.generate_heatmap_visualizations()
            orchestrator.generate_3d_cube_visualizations()
            orchestrator.generate_hierarchical_visualizations()
            orchestrator.generate_matrix_visualizations()
            orchestrator.generate_statistical_visualizations()
            orchestrator.generate_animation_visualizations()
            orchestrator.generate_grid_visualizations()

            # Generate comprehensive report
            report_path = orchestrator.generate_comprehensive_report()
            
            # Summary
            total_files = orchestrator.count_generated_files()
            logger.info(f"\n🎉 COMPREHENSIVE VISUALIZATION GENERATION COMPLETE")
            logger.info(f"📊 Generated {total_files} visualization files")
            logger.info(f"📋 Report saved to: {report_path}")
            logger.info(f"📁 All files saved to: {self.session_path}")

            return self.session_path
            
        except Exception as e:
            logger.error(f"Error during visualization generation: {e}")
            raise


def main():
    """Main entry point for P3IF visualization generation."""
    coordinator = P3IFVisualizationCoordinator()
    session_path = coordinator.generate_comprehensive_visualizations()
    logger.info(f"\n✅ P3IF visualization generation completed successfully!")
    logger.info(f"📁 Session directory: {session_path}")


if __name__ == "__main__":
    main()
