"""
Tests for Interactive 3D Visualizer (p3if.visualization.interactive.interactive_3d).
"""
import pytest
from pathlib import Path
from p3if.visualization.interactive.interactive_3d import Interactive3DVisualizer


@pytest.fixture
def sample_3d_data():
    return {
        "properties": [
            {"name": "Security", "id": "p1"},
            {"name": "Performance", "id": "p2"},
        ],
        "processes": [
            {"name": "Authentication", "id": "pr1"},
            {"name": "Encryption", "id": "pr2"},
        ],
        "perspectives": [
            {"name": "Developer", "id": "pe1"},
            {"name": "Auditor", "id": "pe2"},
        ],
        "relationships": [
            {"property_id": "p1", "process_id": "pr1", "perspective_id": "pe1", "strength": 0.9}
        ],
    }


def test_interactive_3d_visualizer_initialization():
    viz = Interactive3DVisualizer()
    assert viz.framework_data == {}


def test_interactive_3d_scatter_plot_all_and_dimensions(sample_3d_data):
    viz = Interactive3DVisualizer()
    viz.load_framework_data(sample_3d_data)

    res_all = viz.create_3d_scatter_plot(dimension="all")
    assert res_all is not None

    for dim in ["properties", "processes", "perspectives"]:
        res_dim = viz.create_3d_scatter_plot(dimension=dim)
        assert res_dim is not None


def test_interactive_3d_animations(sample_3d_data):
    viz = Interactive3DVisualizer()
    viz.load_framework_data(sample_3d_data)

    rot_anim = viz.create_animated_visualization(animation_type="rotation")
    assert rot_anim is not None

    dim_anim = viz.create_animated_visualization(animation_type="dimension_transition")
    assert dim_anim is not None

    rel_anim = viz.create_animated_visualization(animation_type="relationship_evolution")
    assert rel_anim is not None


def test_interactive_3d_export_html(sample_3d_data, tmp_path):
    viz = Interactive3DVisualizer()
    viz.load_framework_data(sample_3d_data)

    fig = viz.create_3d_scatter_plot(dimension="all")
    out_file = tmp_path / "test_3d.html"
    exported = viz.export_visualization(fig, format="html", filename=out_file)
    assert exported.endswith(".html")
    assert Path(exported).exists()
