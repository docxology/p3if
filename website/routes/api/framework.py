"""
Framework metrics and validation API routes.
"""
import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify
from p3if.core.framework import P3IFFramework
from .common import API_BASE_URL, handle_api_errors

logger = logging.getLogger(__name__)
framework_api_bp = Blueprint("api_framework", __name__)


@framework_api_bp.route(f"{API_BASE_URL}/framework/metrics")
@handle_api_errors
def get_framework_metrics():
    """Get comprehensive framework metrics."""
    try:
        framework = P3IFFramework()
        metrics = framework.get_metrics()

        metrics_data = {
            "total_patterns": metrics.total_patterns,
            "total_relationships": metrics.total_relationships,
            "average_relationship_strength": metrics.average_relationship_strength,
            "average_confidence": metrics.average_confidence,
            "domain_count": metrics.domain_count,
            "pattern_types": metrics.pattern_types_count,
            "relationship_types": metrics.relationship_types_count,
            "orphaned_patterns": metrics.orphaned_patterns,
            "deprecated_patterns": metrics.deprecated_patterns,
            "validation_issues": metrics.validation_issues,
        }

        return jsonify({
            "status": "success",
            "data": metrics_data,
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "cache_info": "Metrics are cached for 5 minutes",
            },
        })
    except Exception:
        logger.exception("Error retrieving framework metrics")
        return jsonify({
            "status": "error",
            "error": "Framework Error",
            "message": "Error retrieving framework metrics",
            "status_code": 500,
        }), 500


@framework_api_bp.route(f"{API_BASE_URL}/framework/validate")
@handle_api_errors
def validate_framework():
    """Validate framework consistency and quality."""
    try:
        framework = P3IFFramework()
        validation_result = framework.validate_framework()

        return jsonify({
            "status": "success",
            "data": {
                "is_valid": validation_result.get("valid", True),
                "issues": validation_result.get("issues", []),
                "warnings": validation_result.get("warnings", []),
                "recommendations": validation_result.get("recommendations", []),
            },
            "metadata": {
                "validated_at": datetime.now(timezone.utc).isoformat(),
            },
        })
    except Exception:
        logger.exception("Error validating framework")
        return jsonify({
            "status": "error",
            "error": "Validation Error",
            "message": "Error validating framework",
            "status_code": 500,
        }), 500
