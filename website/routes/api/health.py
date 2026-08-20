"""
Health check route for P3IF API.
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify
from .common import API_BASE_URL, API_VERSION

health_bp = Blueprint("api_health", __name__)


@health_bp.route(f"{API_BASE_URL}/health")
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": API_VERSION,
        "service": "p3if-api"
    })
