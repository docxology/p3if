"""
Domain discovery and retrieval API routes.
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from flask import Blueprint, jsonify, current_app
from .common import API_BASE_URL, handle_api_errors

logger = logging.getLogger(__name__)
domains_api_bp = Blueprint("api_domains", __name__)


@domains_api_bp.route(f"{API_BASE_URL}/domains")
@handle_api_errors
def get_domains():
    """Get list of all available domains with enhanced metadata."""
    domains_dir = Path(current_app.root_path).parent / "data" / "domains"
    index_path = domains_dir / "index.json"

    domains = []

    try:
        # Try to load domain index first
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                domain_index = json.load(f)
                return jsonify({
                    "status": "success",
                    "data": {
                        "domains": domain_index.get("domains", []),
                        "total": len(domain_index.get("domains", [])),
                        "metadata": {
                            "source": "index_file",
                            "last_updated": datetime.fromtimestamp(
                                index_path.stat().st_mtime, tz=timezone.utc
                            ).isoformat(),
                        },
                    },
                })
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Domain index not available: {e}")

    # Build domain list from files if index doesn't exist or is invalid
    for item in domains_dir.glob("*.json"):
        if item.name in ["index.json", "template_domain.json"]:
            continue

        domain_name = item.stem
        try:
            with open(item, "r", encoding="utf-8") as f:
                domain_data = json.load(f)

            metadata = domain_data.get("metadata", {})
            properties_count = len(domain_data.get("properties", []))
            processes_count = len(domain_data.get("processes", []))
            perspectives_count = len(domain_data.get("perspectives", []))

            domains.append({
                "id": domain_name,
                "name": domain_data.get("domain", domain_name.replace("_", " ").title()),
                "description": domain_data.get("description", ""),
                "version": domain_data.get("version", "1.0"),
                "properties_count": properties_count,
                "processes_count": processes_count,
                "perspectives_count": perspectives_count,
                "relationships_count": len(domain_data.get("relationships", [])),
                "file_path": str(item.relative_to(domains_dir)),
                "last_modified": datetime.fromtimestamp(
                    item.stat().st_mtime, tz=timezone.utc
                ).isoformat(),
                "metadata": metadata,
            })
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Error reading domain file {domain_name}: {e}")
            continue

    return jsonify({
        "status": "success",
        "data": {
            "domains": domains,
            "total": len(domains),
            "metadata": {
                "source": "file_scan",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        },
    })


@domains_api_bp.route(f"{API_BASE_URL}/domains/<domain_id>")
@handle_api_errors
def get_domain(domain_id: str):
    """Get detailed data for a specific domain."""
    domains_dir = Path(current_app.root_path).parent / "data" / "domains"

    domain_id = Path(domain_id).name
    domain_path = (domains_dir / f"{domain_id}.json").resolve()
    domains_root = domains_dir.resolve()
    if domain_path.parent != domains_root:
        return jsonify({
            "status": "error",
            "error": "Domain Not Found",
            "message": f"Domain '{domain_id}' not found",
            "status_code": 404,
        }), 404

    if not domain_path.exists():
        return jsonify({
            "status": "error",
            "error": "Domain Not Found",
            "message": f"Domain '{domain_id}' not found",
            "available_domains": [
                f.stem for f in domains_dir.glob("*.json")
                if f.name not in ["index.json", "template_domain.json"]
            ],
            "status_code": 404,
        }), 404

    try:
        with open(domain_path, "r", encoding="utf-8") as f:
            domain_data = json.load(f)

        domain_data["_metadata"] = {
            "file_path": str(domain_path.relative_to(domains_dir)),
            "last_modified": datetime.fromtimestamp(
                domain_path.stat().st_mtime, tz=timezone.utc
            ).isoformat(),
            "file_size": domain_path.stat().st_size,
            "requested_at": datetime.now(timezone.utc).isoformat(),
        }

        return jsonify({"status": "success", "data": domain_data})
    except json.JSONDecodeError as e:
        return jsonify({
            "status": "error",
            "error": "Invalid Domain Data",
            "message": f"Domain file '{domain_id}.json' contains invalid JSON",
            "details": str(e),
            "status_code": 500,
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": "Internal Error",
            "message": f"Error reading domain file '{domain_id}.json': {e}",
            "status_code": 500,
        }), 500
