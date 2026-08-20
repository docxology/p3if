"""
OpenAPI 3.0 specification endpoint for P3IF API.
"""
from flask import Blueprint, jsonify
from .common import API_BASE_URL, API_VERSION

spec_api_bp = Blueprint("api_spec", __name__)


@spec_api_bp.route(f"{API_BASE_URL}/openapi.json")
def get_openapi_spec():
    """Return OpenAPI specification for this API."""
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "P3IF Enhanced API",
            "description": "Modern RESTful API for the Properties, Processes, and Perspectives Inter-Framework",
            "version": API_VERSION,
            "contact": {
                "name": "P3IF Development Team",
                "url": "https://github.com/p3if/p3if",
            },
        },
        "servers": [
            {
                "url": "http://localhost:5000/api/v2",
                "description": "Development server",
            }
        ],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health Check",
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                        }
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "FrameworkMetrics": {
                    "type": "object",
                    "properties": {
                        "total_patterns": {"type": "integer"},
                        "total_relationships": {"type": "integer"},
                        "average_relationship_strength": {"type": "number"},
                        "average_confidence": {"type": "number"},
                        "domain_count": {"type": "integer"},
                        "pattern_types": {"type": "object"},
                        "relationship_types": {"type": "object"},
                        "orphaned_patterns": {"type": "integer"},
                        "deprecated_patterns": {"type": "integer"},
                        "validation_issues": {"type": "integer"},
                    },
                }
            }
        },
    }
    return jsonify(spec)
