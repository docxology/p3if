#!/usr/bin/env python3
"""
Demonstration script showing the new organized output structure for P3IF visualizations.

This script creates sample visualizations and shows how they are organized
into a consistent directory structure under the main output folder.
"""
import sys
import json
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.output_organizer import (
    get_output_organizer, organize_visualization_output,
    organize_animation_output, create_standard_output_structure
)
from core.framework import P3IFFramework
from tests.utils import create_test_patterns_with_relationships


def demo_organized_output():
    """Demonstrate the organized output structure."""
    print("🚀 P3IF Organized Output Structure Demonstration")
    print("=" * 60)

    # Create a test framework
    print("📊 Creating test framework...")
    framework = create_test_patterns_with_relationships(
        num_patterns=50,
        num_relationships=100
    )

    # Create organized output structure
    print("📁 Creating organized output structure...")
    output_path = create_standard_output_structure()

    print(f"✅ Created output session at: {output_path}")
    print()

    # Create sample visualization files
    print("🎨 Creating sample visualization files...")

    # Create 3D cube visualization
    cube_data = {
        "dimensions": {
            "property": ["prop1", "prop2", "prop3"],
            "process": ["proc1", "proc2", "proc3"],
            "perspective": ["persp1", "persp2", "persp3"]
        },
        "connections": [
            {
                "id": "conn1",
                "property_id": "prop1",
                "process_id": "proc1",
                "perspective_id": "persp1",
                "strength": 0.8,
                "confidence": 0.9
            }
        ],
        "metadata": {
            "generated_at": "2024-01-01T00:00:00Z",
            "total_elements": 9
        }
    }

    cube_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>3D Cube Visualization</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
        <h1>3D Cube Visualization</h1>
        <div id="cube-container"></div>
        <script>
            // Sample 3D cube code
            console.log("3D Cube loaded with data:", cube_data);
        </script>
    </body>
    </html>
    """

    cube_path = organize_visualization_output(
        visualization_type="3d_cube",
        filename="sample_cube.html",
        content=cube_html,
        root_output_dir=output_path
    )

    print(f"📋 Created 3D cube visualization at: {cube_path}")

    # Create network graph visualization
    network_data = {
        "nodes": [
            {"id": "node1", "name": "Property 1", "type": "property"},
            {"id": "node2", "name": "Process 1", "type": "process"},
            {"id": "node3", "name": "Perspective 1", "type": "perspective"}
        ],
        "links": [
            {"source": "node1", "target": "node2", "strength": 0.8},
            {"source": "node2", "target": "node3", "strength": 0.7}
        ]
    }

    network_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network Graph Visualization</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
    </head>
    <body>
        <h1>Network Graph Visualization</h1>
        <div id="graph-container"></div>
        <script>
            // Sample network graph code
            console.log("Network graph loaded with data:", network_data);
        </script>
    </body>
    </html>
    """

    network_path = organize_visualization_output(
        visualization_type="network_graph",
        filename="sample_network.html",
        content=network_html,
        root_output_dir=output_path
    )

    print(f"📊 Created network graph visualization at: {network_path}")

    # Create animation file
    animation_css = """
    /* Sample animation CSS */
    @keyframes rotate-cube {
        0% { transform: rotateX(0deg) rotateY(0deg); }
        100% { transform: rotateX(360deg) rotateY(360deg); }
    }

    .cube {
        animation: rotate-cube 10s infinite linear;
    }
    """

    animation_path = organize_animation_output(
        animation_type="rotation",
        filename="cube_rotation.css",
        content=animation_css,
        root_output_dir=output_path
    )

    print(f"🎬 Created animation at: {animation_path}")

    # Create data export
    data_export = {
        "framework_stats": {
            "total_patterns": len(framework._patterns),
            "total_relationships": len(framework._relationships),
            "domains": list(set(p.domain for p in framework._patterns.values() if p.domain))
        },
        "exported_at": "2024-01-01T00:00:00Z"
    }

    from utils.output_organizer import get_output_organizer
    organizer = get_output_organizer()
    data_path = organizer.get_data_path("exports", "framework_stats.json")
    with open(data_path, 'w') as f:
        json.dump(data_export, f, indent=2)

    print(f"💾 Created data export at: {data_path}")
    print()

    # Show the directory structure
    print("📂 Output Directory Structure:")
    print("=" * 40)

    for subdir_name, description in organizer.current_session.get_subdirs().items():
        subdir_path = output_path / subdir_name
        if subdir_path.exists():
            file_count = len(list(subdir_path.rglob("*")))
            if file_count > 0:
                print(f"📁 {subdir_name}/")
                print(f"   {description}")
                print(f"   Files: {file_count}")

                # Show some example files
                for file_path in list(subdir_path.rglob("*"))[:3]:
                    if file_path.is_file():
                        rel_path = file_path.relative_to(output_path)
                        size = file_path.stat().st_size
                        print(f"   📄 {rel_path} ({size} bytes)")

                if file_count > 3:
                    print(f"   ... and {file_count - 3} more files")

                print()

    # Create session index
    print("📋 Creating session index...")
    index_path = organizer.create_output_index()
    print(f"✅ Created session index at: {index_path}")

    # Show session summary
    summary = organizer.get_session_summary()
    print("\n📊 Session Summary:")
    print("=" * 40)
    print(f"Session: {summary['session_name']}")
    print(f"Base Path: {summary['base_path']}")
    print(f"Total Size: {summary['total_size']:,} bytes")
    print(f"File Counts by Extension:")

    for ext, count in summary['file_counts'].items():
        print(f"  {ext or 'no extension'}: {count} files")

    print("\n🎉 Organized output demonstration complete!")
    print(f"📍 All files are organized under: {output_path}")
    print("\nTo view the organized structure:")
    print(f"ls -la {output_path}")


if __name__ == "__main__":
    demo_organized_output()
