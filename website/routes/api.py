"""
API Routes

This module provides API endpoints for dynamic content and data access.
"""

import os
import json
import sys
from pathlib import Path
from flask import Blueprint, jsonify, request, current_app, abort

# Add the project root to the path for importing core modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import core modules
from core.framework import P3IFFramework
from core.models import Pattern, Relationship
from data.synthetic import SyntheticDataGenerator

api_bp = Blueprint('api', __name__)

@api_bp.route('/domains')
def get_domains():
    """Get list of all available domains."""
    domains_dir = Path(current_app.root_path).parent / 'data' / 'domains'
    index_path = domains_dir / 'index.json'
    
    # Load the domain index if it exists
    try:
        with open(index_path, 'r') as f:
            domain_index = json.load(f)
            return jsonify(domain_index)
    except (FileNotFoundError, json.JSONDecodeError):
        # Build domain list from files
        domains = []
        for item in domains_dir.glob('*.json'):
            if item.name == 'index.json' or item.name == 'template_domain.json':
                continue
                
            domain_name = item.stem
            domains.append({
                'id': domain_name,
                'name': domain_name.replace('_', ' ').title()
            })
        
        return jsonify({'domains': domains})

@api_bp.route('/domains/<domain_id>')
def get_domain(domain_id):
    """Get data for a specific domain."""
    domains_dir = Path(current_app.root_path).parent / 'data' / 'domains'
    domain_path = domains_dir / f"{domain_id}.json"
    
    if not domain_path.exists():
        return jsonify({'error': 'Domain not found'}), 404
    
    try:
        with open(domain_path, 'r') as f:
            domain_data = json.load(f)
        return jsonify(domain_data)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid domain data'}), 500

@api_bp.route('/viz/outputs')
def get_visualization_outputs():
    """Get list of all visualization outputs."""
    output_root = Path(current_app.root_path).parent / 'output'
    
    outputs = []
    for item in output_root.iterdir():
        if not item.is_dir():
            continue
            
        # Check if this directory has visualizations
        viz_path = item / 'visualizations'
        if not viz_path.exists():
            continue
            
        outputs.append({
            'id': item.name,
            'name': item.name.replace('_', ' ').title(),
            'path': f'/output/{item.name}'
        })
    
    return jsonify({'outputs': outputs})

@api_bp.route('/viz/outputs/<output_id>')
def get_visualization_output(output_id):
    """Get visualization details for a specific output."""
    output_root = Path(current_app.root_path).parent / 'output'
    output_path = output_root / output_id
    
    if not output_path.exists() or not output_path.is_dir():
        return jsonify({'error': 'Output not found'}), 404
    
    viz_path = output_path / 'visualizations'
    if not viz_path.exists():
        return jsonify({'error': 'No visualizations in this output'}), 404
    
    # Get available visualizations
    visualizations = []
    
    # Check for interactive visualizations
    if (viz_path / '3d-cube.html').exists():
        visualizations.append({
            'id': '3d_cube',
            'name': '3D Cube',
            'type': 'interactive',
            'path': f'/output/{output_id}/visualizations/3d-cube.html'
        })
    
    if (viz_path / 'force-graph.html').exists():
        visualizations.append({
            'id': 'force_graph',
            'name': 'Force Graph',
            'type': 'interactive',
            'path': f'/output/{output_id}/visualizations/force-graph.html'
        })
    
    # Check for static visualization directories
    for viz_type in ['overview', 'domain', 'compare']:
        type_path = viz_path / viz_type
        if type_path.exists():
            images = []
            for img in type_path.glob('*.png'):
                images.append({
                    'name': img.stem.replace('_', ' ').title(),
                    'path': f'/output/{output_id}/visualizations/{viz_type}/{img.name}'
                })
            
            if images:
                visualizations.append({
                    'id': viz_type,
                    'name': viz_type.title(),
                    'type': 'static',
                    'images': images
                })
    
    return jsonify({
        'id': output_id,
        'name': output_id.replace('_', ' ').title(),
        'visualizations': visualizations
    })

@api_bp.route('/generate', methods=['POST'])
def generate_visualization():
    """Generate a new visualization based on provided parameters."""
    params = request.json
    
    if not params:
        return jsonify({'error': 'No parameters provided'}), 400
    
    # This would integrate with the core framework to generate a visualization
    # For now, just return a placeholder response
    return jsonify({
        'status': 'success',
        'message': 'This endpoint would generate visualizations by invoking the core framework',
        'params': params
    }) 