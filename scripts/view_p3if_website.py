#!/usr/bin/env python3
"""
Simple script to open the P3IF interactive visualization website in a web browser.
"""
import os
import sys
import webbrowser
from pathlib import Path


def open_website():
    """Open the P3IF unified interactive dashboard in a web browser."""
    # Define the path to the website / dashboard
    website_path = Path("outputs/p3if_unified_dashboard.html")
    if not website_path.exists():
        website_path = Path("outputs/unified_interactive_dashboard.html")
    
    if not website_path.exists():
        print(f"Generating unified interactive dashboard at {website_path}...")
        from p3if.core.framework import P3IFFramework
        from p3if.data.synthetic import SyntheticDataGenerator
        from p3if.visualization.interactive.interactive import InteractiveVisualizer

        gen = SyntheticDataGenerator()
        fw = P3IFFramework()
        domains = ["Healthcare", "ArtificialIntelligence", "Blockchain", "QuantumComputing"]
        gen.generate_multi_domain(fw, domain_names=domains, relationships_per_domain=20)
        gen.generate_cross_domain_connections(fw, num_connections=15)

        viz = InteractiveVisualizer(fw)
        website_path.parent.mkdir(parents=True, exist_ok=True)
        viz.generate_modern_dashboard(website_path, title="P3IF Unified Interactive Dashboard")
    
    # Convert to absolute path with file:// protocol
    file_url = f"file://{os.path.abspath(website_path)}"
    
    print(f"Opening P3IF interactive visualization website at: {file_url}")
    webbrowser.open(file_url)
    
    print("\nNavigation Instructions:")
    print("- Click and drag to rotate the 3D cube")
    print("- Use mouse wheel to zoom in/out")
    print("- Hold Shift and drag to pan the view")
    print("- Use the domain dropdown at the top to select different domains")
    
    return True


if __name__ == "__main__":
    if not open_website():
        sys.exit(1)
    
    print("\nFor more information, see:")
    print("- docs/visualization/technical_documentation.md - Comprehensive documentation")
    print("- docs/visualization/user_guide.md - Step-by-step user guide") 