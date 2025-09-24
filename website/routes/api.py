"""
Enhanced RESTful API Routes

This module provides modern, comprehensive API endpoints with OpenAPI specification,
proper error handling, validation, and enhanced functionality for the P3IF framework.
"""

import os
import json
import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from flask import Blueprint, jsonify, request, current_app, abort, Response
from flask_cors import CORS
import logging
from functools import wraps

# Add the project root to the path for importing core modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import enhanced core modules
from p3if_methods.framework import P3IFFramework, FrameworkMetrics
from p3if_methods.models import (
    BasePattern, Property, Process, Perspective, Relationship,
    PatternType, PatternCollection, RelationshipAnalysis
)
from data.synthetic import SyntheticDataGenerator
from p3if_methods.analysis.meta import MetaAnalyzer
from utils.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# API Configuration
API_VERSION = "v2"
API_BASE_URL = f"/api/{API_VERSION}"

# Enable CORS for cross-origin requests
CORS(api_bp)

# API Decorators and Error Handlers
def handle_api_errors(f):
    """Decorator to handle API errors consistently."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"API validation error: {e}")
            return jsonify({
                "error": "Validation Error",
                "message": str(e),
                "status_code": 400
            }), 400
        except FileNotFoundError as e:
            logger.error(f"API file not found: {e}")
            return jsonify({
                "error": "Resource Not Found",
                "message": "The requested resource was not found",
                "status_code": 404
            }), 404
        except Exception as e:
            logger.error(f"API internal error: {e}")
            return jsonify({
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "status_code": 500
            }), 500
    return wrapper

def validate_json(f):
    """Decorator to validate JSON request data."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            if not request.is_json:
                return jsonify({
                    "error": "Invalid Content Type",
                    "message": "Request must have Content-Type: application/json",
                    "status_code": 400
                }), 400
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                "error": "Invalid JSON",
                "message": "Request contains invalid JSON",
                "status_code": 400
            }), 400
    return wrapper

# Enhanced API Endpoints

@api_bp.route(f'{API_BASE_URL}/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": API_VERSION,
        "service": "p3if-api"
    })

@api_bp.route(f'{API_BASE_URL}/domains')
@handle_api_errors
def get_domains():
    """Get list of all available domains with enhanced metadata."""
    domains_dir = Path(current_app.root_path).parent / 'data' / 'domains'
    index_path = domains_dir / 'index.json'
    
    domains = []

    try:
        # Try to load domain index first
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
            domain_index = json.load(f)
                return jsonify({
                    "domains": domain_index.get('domains', []),
                    "total": len(domain_index.get('domains', [])),
                    "metadata": {
                        "source": "index_file",
                        "last_updated": datetime.fromtimestamp(index_path.stat().st_mtime, tz=timezone.utc).isoformat()
                    }
                })
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Domain index not available: {e}")

    # Build domain list from files if index doesn't exist or is invalid
        for item in domains_dir.glob('*.json'):
        if item.name in ['index.json', 'template_domain.json']:
                continue
                
            domain_name = item.stem
        try:
            with open(item, 'r', encoding='utf-8') as f:
                domain_data = json.load(f)

            # Extract metadata from domain file
            metadata = domain_data.get('metadata', {})
            properties_count = len(domain_data.get('properties', []))
            processes_count = len(domain_data.get('processes', []))
            perspectives_count = len(domain_data.get('perspectives', []))

            domains.append({
                'id': domain_name,
                'name': domain_data.get('domain', domain_name.replace('_', ' ').title()),
                'description': domain_data.get('description', ''),
                'version': domain_data.get('version', '1.0'),
                'properties_count': properties_count,
                'processes_count': processes_count,
                'perspectives_count': perspectives_count,
                'relationships_count': len(domain_data.get('relationships', [])),
                'file_path': str(item.relative_to(domains_dir)),
                'last_modified': datetime.fromtimestamp(item.stat().st_mtime, tz=timezone.utc).isoformat(),
                'metadata': metadata
            })
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Error reading domain file {domain_name}: {e}")
            continue

    return jsonify({
        "domains": domains,
        "total": len(domains),
        "metadata": {
            "source": "file_scan",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    })

@api_bp.route(f'{API_BASE_URL}/domains/<domain_id>')
@handle_api_errors
def get_domain(domain_id: str):
    """Get detailed data for a specific domain."""
    domains_dir = Path(current_app.root_path).parent / 'data' / 'domains'
    domain_path = domains_dir / f"{domain_id}.json"
    
    if not domain_path.exists():
        return jsonify({
            "error": "Domain Not Found",
            "message": f"Domain '{domain_id}' does not exist",
            "available_domains": [f.stem for f in domains_dir.glob('*.json')
                                if f.name not in ['index.json', 'template_domain.json']],
            "status_code": 404
        }), 404

    try:
        with open(domain_path, 'r', encoding='utf-8') as f:
            domain_data = json.load(f)

        # Add metadata
        domain_data['_metadata'] = {
            'file_path': str(domain_path.relative_to(domains_dir)),
            'last_modified': datetime.fromtimestamp(domain_path.stat().st_mtime, tz=timezone.utc).isoformat(),
            'file_size': domain_path.stat().st_size,
            'requested_at': datetime.now(timezone.utc).isoformat()
        }

        return jsonify(domain_data)
    except json.JSONDecodeError as e:
        return jsonify({
            "error": "Invalid Domain Data",
            "message": f"Domain file '{domain_id}.json' contains invalid JSON",
            "details": str(e),
            "status_code": 500
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Internal Error",
            "message": f"Error reading domain file '{domain_id}.json'",
            "status_code": 500
        }), 500

# Framework and Analysis Endpoints

@api_bp.route(f'{API_BASE_URL}/framework/metrics')
@handle_api_errors
def get_framework_metrics():
    """Get comprehensive framework metrics."""
    try:
        framework = P3IFFramework()
        metrics = framework.get_metrics()

        return jsonify({
            "status": "success",
            "data": {
                "total_patterns": metrics.total_patterns,
                "total_relationships": metrics.total_relationships,
                "average_relationship_strength": metrics.average_relationship_strength,
                "average_confidence": metrics.average_confidence,
                "domain_count": metrics.domain_count,
                "pattern_types": metrics.pattern_types_count,
                "relationship_types": metrics.relationship_types_count,
                "orphaned_patterns": metrics.orphaned_patterns,
                "deprecated_patterns": metrics.deprecated_patterns,
                "validation_issues": metrics.validation_issues
            },
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "cache_info": "Metrics are cached for 5 minutes"
            }
        })
    except Exception as e:
        return jsonify({
            "error": "Framework Error",
            "message": f"Error retrieving framework metrics: {str(e)}",
            "status_code": 500
        }), 500

@api_bp.route(f'{API_BASE_URL}/framework/validate')
@handle_api_errors
def validate_framework():
    """Validate framework consistency and quality."""
    try:
        framework = P3IFFramework()
        validation_result = framework.validate_framework()

        return jsonify({
            "status": "success",
            "data": validation_result,
            "metadata": {
                "validated_at": datetime.now(timezone.utc).isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            "error": "Validation Error",
            "message": f"Error validating framework: {str(e)}",
            "status_code": 500
        }), 500

@api_bp.route(f'{API_BASE_URL}/patterns')
@handle_api_errors
def get_patterns():
    """Get all patterns with optional filtering."""
    try:
        framework = P3IFFramework()

        # Parse query parameters
        pattern_type = request.args.get('type')
        domain = request.args.get('domain')
        tag = request.args.get('tag')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        search = request.args.get('search')

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
            # Get all patterns
            collection = framework.get_pattern_collection()
            patterns = collection.all_patterns()

        # Apply pagination
        total_count = len(patterns)
        paginated_patterns = patterns[offset:offset + limit]

        return jsonify({
            "status": "success",
            "data": {
                "patterns": [pattern.dict(by_alias=True) for pattern in paginated_patterns],
                "total_count": total_count,
                "returned_count": len(paginated_patterns),
                "pagination": {
                    "offset": offset,
                    "limit": limit,
                    "has_more": offset + limit < total_count
                }
            },
            "metadata": {
                "filters_applied": {
                    "type": pattern_type,
                    "domain": domain,
                    "tag": tag,
                    "search": search
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            "error": "Query Error",
            "message": f"Error retrieving patterns: {str(e)}",
            "status_code": 500
        }), 500

@api_bp.route(f'{API_BASE_URL}/patterns/<pattern_id>')
@handle_api_errors
def get_pattern(pattern_id: str):
    """Get a specific pattern by ID."""
    try:
        framework = P3IFFramework()
        pattern = framework.get_pattern(pattern_id)

        if not pattern:
            return jsonify({
                "error": "Pattern Not Found",
                "message": f"Pattern with ID '{pattern_id}' not found",
                "status_code": 404
            }), 404

        # Get related relationships
        relationships = framework.get_relationships_by_pattern(pattern_id)

        return jsonify({
            "status": "success",
            "data": {
                "pattern": pattern.dict(by_alias=True),
                "relationships": [rel.dict(by_alias=True) for rel in relationships]
            },
            "metadata": {
                "retrieved_at": datetime.now(timezone.utc).isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            "error": "Retrieval Error",
            "message": f"Error retrieving pattern: {str(e)}",
            "status_code": 500
        }), 500

@api_bp.route(f'{API_BASE_URL}/relationships')
@handle_api_errors
def get_relationships():
    """Get all relationships with optional filtering."""
    try:
        framework = P3IFFramework()

        # Parse query parameters
        property_id = request.args.get('property_id')
        process_id = request.args.get('process_id')
        perspective_id = request.args.get('perspective_id')
        relationship_type = request.args.get('type')
        min_strength = request.args.get('min_strength', type=float)
        min_confidence = request.args.get('min_confidence', type=float)
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        relationships = []

        if property_id or process_id or perspective_id:
            # Get relationships for specific patterns
            pattern_ids = [pid for pid in [property_id, process_id, perspective_id] if pid]
            for pid in pattern_ids:
                relationships.extend(framework.get_relationships_by_pattern(pid))
        elif relationship_type:
            relationships = framework.get_relationships_by_type(relationship_type)
        else:
            # Get all relationships
            relationships = list(framework._relationships.values())

        # Apply filters
        filtered_relationships = []
        for rel in relationships:
            if min_strength and rel.strength < min_strength:
                continue
            if min_confidence and rel.confidence < min_confidence:
                continue
            filtered_relationships.append(rel)

        # Apply pagination
        total_count = len(filtered_relationships)
        paginated_relationships = filtered_relationships[offset:offset + limit]

        return jsonify({
            "status": "success",
            "data": {
                "relationships": [rel.dict(by_alias=True) for rel in paginated_relationships],
                "total_count": total_count,
                "returned_count": len(paginated_relationships),
                "pagination": {
                    "offset": offset,
                    "limit": limit,
                    "has_more": offset + limit < total_count
                }
            },
            "metadata": {
                "filters_applied": {
                    "property_id": property_id,
                    "process_id": process_id,
                    "perspective_id": perspective_id,
                    "relationship_type": relationship_type,
                    "min_strength": min_strength,
                    "min_confidence": min_confidence
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            "error": "Query Error",
            "message": f"Error retrieving relationships: {str(e)}",
            "status_code": 500
        }), 500

@api_bp.route(f'{API_BASE_URL}/analysis/patterns')
@handle_api_errors
def analyze_patterns():
    """Perform pattern analysis."""
    try:
        analyzer = MetaAnalyzer()
        # This would integrate with the analysis engine
        # For now, return a placeholder
        return jsonify({
            "status": "success",
            "message": "Pattern analysis endpoint - integration with MetaAnalyzer needed",
            "data": {},
            "metadata": {
                "analyzed_at": datetime.now(timezone.utc).isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            "error": "Analysis Error",
            "message": f"Error performing pattern analysis: {str(e)}",
            "status_code": 500
        }), 500

# Visualization and Generation Endpoints

@api_bp.route(f'{API_BASE_URL}/visualizations')
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
                    "supported_formats": ["html", "json"]
                },
                {
                    "id": "network_graph",
                    "name": "Network Graph",
                    "description": "Force-directed graph of pattern relationships",
                    "features": ["interactive", "drag", "filter", "search", "export"],
                    "supported_formats": ["html", "json", "png", "svg"]
                },
                {
                    "id": "matrix_view",
                    "name": "Matrix View",
                    "description": "Matrix representation of relationships",
                    "features": ["interactive", "filter", "heatmap"],
                    "supported_formats": ["html", "json"]
                },
                {
                    "id": "dashboard",
                    "name": "Analytics Dashboard",
                    "description": "Comprehensive dashboard with multiple views",
                    "features": ["multi-tab", "charts", "filters", "export"],
                    "supported_formats": ["html", "json"]
                }
            ],
            "themes": ["default", "dark", "light", "blue"],
            "interaction_modes": ["view_only", "select", "edit", "filter", "annotate"]
        },
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    })

@api_bp.route(f'{API_BASE_URL}/visualizations/generate', methods=['POST'])
@handle_api_errors
@validate_json
def generate_visualization():
    """Generate a visualization with specified parameters."""
    try:
        params = request.get_json()
    
        # Validate required parameters
    if not params:
            return jsonify({
                "error": "Invalid Request",
                "message": "Request body is required",
                "status_code": 400
            }), 400

        visualization_type = params.get('type')
        if not visualization_type:
            return jsonify({
                "error": "Missing Parameter",
                "message": "Visualization type is required",
                "status_code": 400
            }), 400

        # This would integrate with the enhanced visualization engine
        # For now, return enhanced response structure
        return jsonify({
            "status": "success",
            "data": {
                "visualization_id": str(uuid.uuid4()),
                "type": visualization_type,
                "status": "generating",
                "estimated_completion": "2024-01-01T00:00:00Z",  # Would be calculated
                "parameters": params,
                "output_formats": ["html", "json"],
                "estimated_size": "2.5 MB"
            },
            "metadata": {
                "requested_at": datetime.now(timezone.utc).isoformat(),
                "api_version": API_VERSION
            }
        })
    except Exception as e:
        return jsonify({
            "error": "Generation Error",
            "message": f"Error generating visualization: {str(e)}",
            "status_code": 500
        }), 500

@api_bp.route(f'{API_BASE_URL}/visualizations/<viz_id>/status')
@handle_api_errors
def get_visualization_status(viz_id: str):
    """Get the status of a visualization generation request."""
    # This would check the actual status of a visualization generation
    # For now, return a placeholder
    return jsonify({
        "status": "success",
        "data": {
            "visualization_id": viz_id,
            "status": "completed",
            "progress": 100,
            "output_files": [
                f"/api/v2/visualizations/{viz_id}/download/html",
                f"/api/v2/visualizations/{viz_id}/download/json"
            ]
        },
        "metadata": {
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
    })

@api_bp.route(f'{API_BASE_URL}/export', methods=['POST'])
@handle_api_errors
@validate_json
def export_data():
    """Export framework data in various formats."""
    try:
        params = request.get_json()
        export_format = params.get('format', 'json')
        domains = params.get('domains', [])
        include_relationships = params.get('include_relationships', True)

        # Create framework instance and export
        framework = P3IFFramework()

        if export_format.lower() == 'json':
            if domains:
                # Filter patterns by domains
                all_patterns = []
                for domain in domains:
                    domain_patterns = framework.get_patterns_by_domain(domain)
                    all_patterns.extend(domain_patterns)

                # Create filtered framework data
                filtered_patterns = {p.id: p for p in all_patterns}
                filtered_relationships = {}

                if include_relationships:
                    for rel in framework._relationships.values():
                        if any(pid in filtered_patterns for pid in rel.get_connected_patterns()):
                            filtered_relationships[rel.id] = rel

                export_data = {
                    "patterns": [p.dict(by_alias=True) for p in filtered_patterns.values()],
                    "relationships": [r.dict(by_alias=True) for r in filtered_relationships.values()],
                    "metadata": {
                        "exported_at": datetime.now(timezone.utc).isoformat(),
                        "export_format": "json",
                        "domains": domains,
                        "total_patterns": len(filtered_patterns),
                        "total_relationships": len(filtered_relationships)
                    }
                }

                response = jsonify(export_data)
                response.headers['Content-Disposition'] = f'attachment; filename=p3if_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                return response

        return jsonify({
            "error": "Unsupported Format",
            "message": f"Export format '{export_format}' is not supported",
            "supported_formats": ["json"],
            "status_code": 400
        }), 400

    except Exception as e:
        return jsonify({
            "error": "Export Error",
            "message": f"Error exporting data: {str(e)}",
            "status_code": 500
        }), 500

@api_bp.route(f'{API_BASE_URL}/openapi.json')
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
                "url": "https://github.com/p3if/p3if"
            }
        },
        "servers": [
            {
                "url": "http://localhost:5000/api/v2",
                "description": "Development server"
            }
        ],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health Check",
                    "responses": {
                        "200": {
                            "description": "Service is healthy"
                        }
                    }
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
                        "validation_issues": {"type": "integer"}
                    }
                }
            }
        }
    }

    return jsonify(spec) 