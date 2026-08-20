"""
Modular API Blueprint initialization and router composition.
"""
from flask import Blueprint
from flask_cors import CORS
from .common import (
    API_AVAILABLE,
    API_BASE_URL,
    API_VERSION,
    handle_api_errors,
    validate_json,
)
from .health import health_bp, health_check
from .domains import domains_api_bp, get_domains, get_domain
from .framework import framework_api_bp, get_framework_metrics, validate_framework
from .patterns import patterns_api_bp, get_patterns, get_pattern
from .relationships import relationships_api_bp, get_relationships
from .analysis import analysis_api_bp, analyze_patterns
from .visualizations import (
    visualizations_api_bp,
    get_visualizations,
    generate_visualization,
    get_visualization_status,
)
from .export import export_api_bp, export_data
from .spec import spec_api_bp, get_openapi_spec

api_bp = Blueprint("api", __name__)
CORS(api_bp)

# Register sub-blueprints without prefix (submodule route paths already include API_BASE_URL)
api_bp.register_blueprint(health_bp)
api_bp.register_blueprint(domains_api_bp)
api_bp.register_blueprint(framework_api_bp)
api_bp.register_blueprint(patterns_api_bp)
api_bp.register_blueprint(relationships_api_bp)
api_bp.register_blueprint(analysis_api_bp)
api_bp.register_blueprint(visualizations_api_bp)
api_bp.register_blueprint(export_api_bp)
api_bp.register_blueprint(spec_api_bp)

__all__ = [
    "api_bp",
    "API_AVAILABLE",
    "API_BASE_URL",
    "API_VERSION",
    "handle_api_errors",
    "validate_json",
    "health_check",
    "get_domains",
    "get_domain",
    "get_framework_metrics",
    "validate_framework",
    "get_patterns",
    "get_pattern",
    "get_relationships",
    "analyze_patterns",
    "get_visualizations",
    "generate_visualization",
    "get_visualization_status",
    "export_data",
    "get_openapi_spec",
]
