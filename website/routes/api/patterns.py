"""
Pattern retrieval API routes.
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from p3if.core.framework import P3IFFramework
from .common import API_BASE_URL, handle_api_errors

patterns_api_bp = Blueprint("api_patterns", __name__)


@patterns_api_bp.route(f"{API_BASE_URL}/patterns")
@handle_api_errors
def get_patterns():
    """Get all patterns with optional filtering."""
    try:
        framework = P3IFFramework()

        pattern_type = request.args.get("type")
        domain = request.args.get("domain")
        tag = request.args.get("tag")
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)
        search = request.args.get("search")

        patterns = []

        if pattern_type:
            patterns = framework.get_patterns_by_type(pattern_type)
        elif search:
            patterns = framework.search_patterns(search, limit)
        elif domain:
            patterns = framework.get_patterns_by_domain(domain)
        elif tag:
            patterns = framework.get_patterns_by_tag(tag)
        else:
            collection = framework.get_pattern_collection()
            patterns = collection.all_patterns()

        total_count = len(patterns)
        paginated_patterns = patterns[offset:offset + limit]

        return jsonify({
            "status": "success",
            "data": {
                "patterns": [pattern.model_dump(by_alias=True) for pattern in paginated_patterns],
                "total_count": total_count,
                "returned_count": len(paginated_patterns),
                "pagination": {
                    "offset": offset,
                    "limit": limit,
                    "has_more": offset + limit < total_count,
                },
            },
            "metadata": {
                "filters_applied": {
                    "type": pattern_type,
                    "domain": domain,
                    "tag": tag,
                    "search": search,
                },
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": "Query Error",
            "message": f"Error retrieving patterns: {str(e)}",
            "status_code": 500,
        }), 500


@patterns_api_bp.route(f"{API_BASE_URL}/patterns/<pattern_id>")
@handle_api_errors
def get_pattern(pattern_id: str):
    """Get a specific pattern by ID."""
    try:
        framework = P3IFFramework()
        pattern = framework.get_pattern(pattern_id)

        if not pattern:
            return jsonify({
                "status": "error",
                "error": "Pattern Not Found",
                "message": f"Pattern with ID '{pattern_id}' not found",
                "status_code": 404,
            }), 404

        relationships = framework.get_relationships_by_pattern(pattern_id)

        return jsonify({
            "status": "success",
            "data": {
                "pattern": pattern.model_dump(by_alias=True),
                "relationships": [rel.model_dump(by_alias=True) for rel in relationships],
            },
            "metadata": {
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            },
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": "Retrieval Error",
            "message": f"Error retrieving pattern: {str(e)}",
            "status_code": 500,
        }), 500
