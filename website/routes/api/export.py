"""
Export endpoints for P3IF data in JSON, CSV, and GraphML formats.
"""
import io
import csv
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
import networkx as nx
from p3if.core.framework import P3IFFramework
from .common import API_BASE_URL, API_AVAILABLE, handle_api_errors, validate_json

export_api_bp = Blueprint("api_export", __name__)


@export_api_bp.route(f"{API_BASE_URL}/export", methods=["POST"])
@handle_api_errors
@validate_json
def export_data():
    """Export framework data in various formats."""
    if not API_AVAILABLE:
        return jsonify({
            "status": "error",
            "message": "P3IF API not available",
        }), 503

    try:
        params = request.get_json() or {}
        export_format = params.get("format", "json")
        domains = params.get("domains", [])
        include_relationships = params.get("include_relationships", True)

        framework = P3IFFramework()

        if export_format.lower() == "json":
            if domains:
                all_patterns = []
                for domain in domains:
                    domain_patterns = framework.get_patterns_by_domain(domain)
                    all_patterns.extend(domain_patterns)

                filtered_patterns = {p.id: p for p in all_patterns}
                filtered_relationships = {}

                if include_relationships:
                    for rel in framework._relationships.values():
                        if any(pid in filtered_patterns for pid in rel.get_connected_patterns()):
                            filtered_relationships[rel.id] = rel

                export_data_dict = {
                    "patterns": [p.model_dump(by_alias=True) for p in filtered_patterns.values()],
                    "relationships": [
                        r.model_dump(by_alias=True) for r in filtered_relationships.values()
                    ],
                    "metadata": {
                        "exported_at": datetime.now(timezone.utc).isoformat(),
                        "export_format": "json",
                        "domains": domains,
                        "total_patterns": len(filtered_patterns),
                        "total_relationships": len(filtered_relationships),
                    },
                }
            else:
                all_patterns = []
                for pattern_type in ["property", "process", "perspective"]:
                    all_patterns.extend(framework.get_patterns_by_type(pattern_type))

                all_relationships = (
                    list(framework._relationships.values()) if include_relationships else []
                )

                export_data_dict = {
                    "patterns": [p.model_dump(by_alias=True) for p in all_patterns],
                    "relationships": [r.model_dump(by_alias=True) for r in all_relationships],
                    "metadata": {
                        "exported_at": datetime.now(timezone.utc).isoformat(),
                        "export_format": "json",
                        "domains": [],
                        "total_patterns": len(all_patterns),
                        "total_relationships": len(all_relationships),
                    },
                }

            response = jsonify(export_data_dict)
            response.headers["Content-Disposition"] = (
                f'attachment; filename=p3if_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )
            return response

        elif export_format.lower() == "csv":
            patterns_output = io.StringIO()
            patterns_writer = csv.writer(patterns_output)
            patterns_writer.writerow(["id", "type", "name", "description", "domain", "tags"])

            for pattern_type in ["property", "process", "perspective"]:
                for pattern in framework.get_patterns_by_type(pattern_type):
                    tags_str = ",".join(pattern.tags) if pattern.tags else ""
                    patterns_writer.writerow([
                        pattern.id,
                        pattern_type,
                        pattern.name,
                        pattern.description,
                        pattern.domain or "",
                        tags_str,
                    ])

            relationships_output = io.StringIO()
            relationships_writer = csv.writer(relationships_output)
            relationships_writer.writerow([
                "id", "property_id", "process_id", "perspective_id", "strength", "confidence"
            ])

            for rel in framework.get_all_relationships():
                relationships_writer.writerow([
                    rel.id,
                    rel.property_id or "",
                    rel.process_id or "",
                    rel.perspective_id or "",
                    rel.strength,
                    rel.confidence,
                ])

            response_data = {
                "patterns_csv": patterns_output.getvalue(),
                "relationships_csv": relationships_output.getvalue(),
                "metadata": {
                    "exported_at": datetime.now(timezone.utc).isoformat(),
                    "export_format": "csv",
                },
            }

            response = jsonify(response_data)
            response.headers["Content-Disposition"] = (
                f'attachment; filename=p3if_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )
            return response

        elif export_format.lower() == "graphml":
            G = nx.Graph()

            for pattern_type in ["property", "process", "perspective"]:
                for pattern in framework.get_patterns_by_type(pattern_type):
                    G.add_node(
                        pattern.id,
                        type=pattern_type,
                        name=pattern.name,
                        description=pattern.description or "",
                        domain=pattern.domain or "",
                        tags=",".join(pattern.tags) if pattern.tags else "",
                    )

            for rel in framework.get_all_relationships():
                patterns = []
                if rel.property_id:
                    patterns.append(rel.property_id)
                if rel.process_id:
                    patterns.append(rel.process_id)
                if rel.perspective_id:
                    patterns.append(rel.perspective_id)

                for i in range(len(patterns)):
                    for j in range(i + 1, len(patterns)):
                        G.add_edge(
                            patterns[i],
                            patterns[j],
                            rel_id=rel.id,
                            strength=rel.strength,
                            confidence=rel.confidence,
                        )

            graphml_output = io.BytesIO()
            nx.write_graphml(G, graphml_output)
            graphml_str = graphml_output.getvalue().decode("utf-8")

            response_data = {
                "graphml": graphml_str,
                "metadata": {
                    "exported_at": datetime.now(timezone.utc).isoformat(),
                    "export_format": "graphml",
                    "node_count": G.number_of_nodes(),
                    "edge_count": G.number_of_edges(),
                },
            }

            response = jsonify(response_data)
            response.headers["Content-Disposition"] = (
                f'attachment; filename=p3if_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.graphml.json'
            )
            return response

        return jsonify({
            "status": "error",
            "error": "Unsupported Format",
            "message": f"Export format '{export_format}' is not supported",
            "supported_formats": ["json", "csv", "graphml"],
            "status_code": 400,
        }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": "Export Error",
            "message": f"Error exporting data: {str(e)}",
            "status_code": 500,
        }), 500
