"""
Visualization capabilities and generation API routes.
"""
import uuid
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from .common import API_BASE_URL, API_VERSION, handle_api_errors, validate_json

visualizations_api_bp = Blueprint("api_visualizations", __name__)


@visualizations_api_bp.route(f"{API_BASE_URL}/visualizations")
@handle_api_errors
def get_visualizations():
    """Get available visualization types and capabilities."""
    return jsonify({
        "status": "success",
        "data": {
            "visualization_types": [
                {
                    "id": "cube_3d",
                    "name": "3D Cube",
                    "description": "Interactive 3D cube visualization of P3IF dimensions",
                    "features": ["interactive", "zoom", "rotate", "filter", "search"],
                    "supported_formats": ["html", "json"],
                },
                {
                    "id": "network_graph",
                    "name": "Network Graph",
                    "description": "Force-directed graph of pattern relationships",
                    "features": ["interactive", "drag", "filter", "search", "export"],
                    "supported_formats": ["html", "json", "png", "svg"],
                },
                {
                    "id": "matrix_view",
                    "name": "Matrix View",
                    "description": "Matrix representation of relationships",
                    "features": ["interactive", "filter", "heatmap"],
                    "supported_formats": ["html", "json"],
                },
                {
                    "id": "dashboard",
                    "name": "Analytics Dashboard",
                    "description": "Comprehensive dashboard with multiple views",
                    "features": ["multi-tab", "charts", "filters", "export"],
                    "supported_formats": ["html", "json"],
                },
            ],
            "themes": ["default", "dark", "light", "blue"],
            "interaction_modes": ["view_only", "select", "edit", "filter", "annotate"],
        },
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    })


@visualizations_api_bp.route(f"{API_BASE_URL}/visualizations/generate", methods=["POST"])
@handle_api_errors
@validate_json
def generate_visualization():
    """Generate a visualization with specified parameters."""
    try:
        params = request.get_json() or {}
        visualization_type = params.get("type")
        if not visualization_type:
            return jsonify({
                "status": "error",
                "error": "Missing Parameter",
                "message": "Visualization type is required",
                "status_code": 400,
            }), 400

        return jsonify({
            "status": "success",
            "data": {
                "visualization_id": str(uuid.uuid4()),
                "type": visualization_type,
                "status": "generating",
                "estimated_completion": "2024-01-01T00:00:00Z",
                "parameters": params,
                "output_formats": ["html", "json"],
                "estimated_size": "2.5 MB",
            },
            "metadata": {
                "requested_at": datetime.now(timezone.utc).isoformat(),
                "api_version": API_VERSION,
            },
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": "Generation Error",
            "message": f"Error generating visualization: {str(e)}",
            "status_code": 500,
        }), 500


@visualizations_api_bp.route(f"{API_BASE_URL}/visualizations/<viz_id>/status")
@handle_api_errors
def get_visualization_status(viz_id: str):
    """Get the status of a visualization generation request."""
    try:
        from p3if.utils.storage import VisualizationStorage
        storage = VisualizationStorage()

        viz_status = storage.get_visualization_status(viz_id)
        if not viz_status:
            return jsonify({
                "status": "error",
                "error": "Visualization Not Found",
                "message": f"No visualization found with ID: {viz_id}",
                "status_code": 404,
            }), 404

        output_files = []
        if viz_status.get("status") == "completed":
            files = storage.get_visualization_files(viz_id)
            for file_info in files:
                output_files.append(file_info["url"])

        return jsonify({
            "status": "success",
            "data": {
                "visualization_id": viz_id,
                "status": viz_status["status"],
                "progress": viz_status.get("progress", 100),
                "output_files": output_files,
                "generated_at": viz_status.get("generated_at"),
                "expires_at": viz_status.get("expires_at"),
                "error_message": viz_status.get("error_message"),
            },
            "metadata": {
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "processing_time_seconds": viz_status.get("processing_time", 0),
                "visualization_type": viz_status.get("type", "unknown"),
            },
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": "Status Check Error",
            "message": f"Error retrieving visualization status: {str(e)}",
            "status_code": 500,
        }), 500
