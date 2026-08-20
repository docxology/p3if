"""
Relationship retrieval API routes.
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from p3if.core.framework import P3IFFramework
from .common import API_BASE_URL, handle_api_errors

relationships_api_bp = Blueprint("api_relationships", __name__)


@relationships_api_bp.route(f"{API_BASE_URL}/relationships")
@handle_api_errors
def get_relationships():
    """Get all relationships with optional filtering."""
    try:
        framework = P3IFFramework()

        property_id = request.args.get("property_id")
        process_id = request.args.get("process_id")
        perspective_id = request.args.get("perspective_id")
        relationship_type = request.args.get("type")
        min_strength = request.args.get("min_strength", type=float)
        min_confidence = request.args.get("min_confidence", type=float)
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)

        relationships = []

        if property_id or process_id or perspective_id:
            pattern_ids = [pid for pid in [property_id, process_id, perspective_id] if pid]
            for pid in pattern_ids:
                relationships.extend(framework.get_relationships_by_pattern(pid))
        elif relationship_type:
            relationships = framework.get_relationships_by_type(relationship_type)
        else:
            relationships = list(framework._relationships.values())

        # Apply filters
        filtered_relationships = []
        for rel in relationships:
            if min_strength and rel.strength < min_strength:
                continue
            if min_confidence and rel.confidence < min_confidence:
                continue
            filtered_relationships.append(rel)

        total_count = len(filtered_relationships)
        paginated_relationships = filtered_relationships[offset:offset + limit]

        return jsonify({
            "status": "success",
            "data": {
                "relationships": [
                    rel.model_dump(by_alias=True) for rel in paginated_relationships
                ],
                "total_count": total_count,
                "returned_count": len(paginated_relationships),
                "pagination": {
                    "offset": offset,
                    "limit": limit,
                    "has_more": offset + limit < total_count,
                },
            },
            "metadata": {
                "filters_applied": {
                    "property_id": property_id,
                    "process_id": process_id,
                    "perspective_id": perspective_id,
                    "relationship_type": relationship_type,
                    "min_strength": min_strength,
                    "min_confidence": min_confidence,
                },
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": "Query Error",
            "message": f"Error retrieving relationships: {str(e)}",
            "status_code": 500,
        }), 500
