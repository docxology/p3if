"""
Domain Routes

This module provides routes for exploring P3IF domains from the data/domains directory.
"""

import os
import json
from pathlib import Path
from flask import Blueprint, render_template, abort, current_app, jsonify

domains_bp = Blueprint('domains', __name__, template_folder='../templates')

@domains_bp.route('/')
def index():
    """Domains overview page."""
    domains_dir = Path(current_app.root_path).parent / 'data' / 'domains'
    index_path = domains_dir / 'index.json'
    
    # Load the domain index
    try:
        with open(index_path, 'r') as f:
            domain_index = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        domain_index = {'domains': []}
    
    # Get all domain files
    domains = []
    for item in domains_dir.glob('*.json'):
        if item.name == 'index.json' or item.name == 'template_domain.json':
            continue
            
        domain_name = item.stem
        # Try to get domain info from the index
        domain_info = next((d for d in domain_index.get('domains', []) 
                         if d.get('id', '').lower() == domain_name.lower()), None)
        
        if not domain_info:
            # If not in index, create basic info
            domain_info = {
                'id': domain_name,
                'name': domain_name.replace('_', ' ').title(),
                'description': f"Domain data for {domain_name}"
            }
        
        domains.append(domain_info)
    
    # Sort domains alphabetically by name
    domains.sort(key=lambda x: x.get('name', ''))
    
    return render_template('domains/index.html', 
                          title='Domains',
                          domains=domains)

@domains_bp.route('/<domain_id>')
def show_domain(domain_id):
    """Display a specific domain."""
    domains_dir = Path(current_app.root_path).parent / 'data' / 'domains'
    domain_path = domains_dir / f"{domain_id}.json"
    
    if not domain_path.exists():
        abort(404)
    
    # Load the domain data
    try:
        with open(domain_path, 'r') as f:
            domain_data = json.load(f)
    except json.JSONDecodeError:
        abort(500)
    
    # Get basic stats
    pattern_count = len(domain_data.get('patterns', []))
    process_count = len(domain_data.get('processes', []))
    perspective_count = len(domain_data.get('perspectives', []))
    
    # Get domain visualizations if they exist
    viz_path = Path(current_app.root_path).parent / 'output' / 'final' / 'visualizations'
    domain_viz = {}
    
    if viz_path.exists():
        # Check for domain-specific visualizations
        domain_dir = viz_path / 'domain'
        if domain_dir.exists():
            for img in domain_dir.glob('*.png'):
                domain_viz[img.stem] = f'/output/final/visualizations/domain/{img.name}'
        
        # Check for domain in comparative visualizations
        compare_dir = viz_path / 'compare'
        if compare_dir.exists():
            for img in compare_dir.glob('*.png'):
                domain_viz[f'compare_{img.stem}'] = f'/output/final/visualizations/compare/{img.name}'
    
    return render_template('domains/detail.html',
                          title=domain_data.get('name', domain_id.title()),
                          domain=domain_data,
                          pattern_count=pattern_count,
                          process_count=process_count,
                          perspective_count=perspective_count,
                          visualizations=domain_viz)

@domains_bp.route('/<domain_id>/patterns')
def domain_patterns(domain_id):
    """Show patterns for a specific domain."""
    domains_dir = Path(current_app.root_path).parent / 'data' / 'domains'
    domain_path = domains_dir / f"{domain_id}.json"
    
    if not domain_path.exists():
        abort(404)
    
    # Load the domain data
    try:
        with open(domain_path, 'r') as f:
            domain_data = json.load(f)
    except json.JSONDecodeError:
        abort(500)
    
    patterns = domain_data.get('patterns', [])
    
    # Group patterns by type
    pattern_groups = {
        'property': [],
        'process': [],
        'perspective': []
    }
    
    for pattern in patterns:
        pattern_type = pattern.get('type', '').lower()
        if pattern_type in pattern_groups:
            pattern_groups[pattern_type].append(pattern)
    
    return render_template('domains/patterns.html',
                          title=f"Patterns: {domain_data.get('name', domain_id.title())}",
                          domain=domain_data,
                          pattern_groups=pattern_groups)

@domains_bp.route('/<domain_id>/api/data')
def domain_api_data(domain_id):
    """API endpoint to get domain data as JSON."""
    domains_dir = Path(current_app.root_path).parent / 'data' / 'domains'
    domain_path = domains_dir / f"{domain_id}.json"
    
    if not domain_path.exists():
        return jsonify({'error': 'Domain not found'}), 404
    
    # Load the domain data
    try:
        with open(domain_path, 'r') as f:
            domain_data = json.load(f)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid domain data'}), 500
    
    return jsonify(domain_data) 