"""
Domain Routes

This module provides routes for exploring P3IF domains from the data/domains directory.
"""

import json
from pathlib import Path
from flask import Blueprint, render_template, abort, current_app, jsonify

domains_bp = Blueprint('domains', __name__, template_folder='../templates')


def _safe_domain_path(domain_id: str) -> Path:
    """Resolve a domain id to a file inside data/domains, rejecting traversal.

    Returns a path that is guaranteed to sit directly inside the domains
    directory, or a path that resolves outside it (which callers treat as a
    not-found). Guards against ``domain_id`` values with path separators or
    parent references.
    """
    domain_id = Path(domain_id).name
    domains_dir = Path(current_app.root_path).parent / 'data' / 'domains'
    return (domains_dir / f"{domain_id}.json").resolve()

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
        
        domain_entry = None
        if domain_info:
            domain_entry = dict(domain_info)
            if 'description' not in domain_entry:
                domain_entry['description'] = f"Domain data for {domain_entry.get('name', domain_name)}"
        else:
            domain_entry = {
                'id': domain_name,
                'name': domain_name.replace('_', ' ').title(),
                'description': f"Domain data for {domain_name}"
            }
        
        domains.append(domain_entry)
    
    # Sort domains alphabetically by name
    domains.sort(key=lambda x: x.get('name', ''))
    
    return render_template('domains/index.html', 
                          title='Domains',
                          domains=domains)

@domains_bp.route('/<domain_id>')
def show_domain(domain_id):
    """Display a specific domain."""
    domains_dir = Path(current_app.root_path).parent / 'data' / 'domains'
    domain_path = _safe_domain_path(domain_id)

    if domain_path.parent != domains_dir.resolve() or not domain_path.exists():
        abort(404)
    
    # Load the domain data
    try:
        with open(domain_path, 'r') as f:
            domain_data = json.load(f)
    except json.JSONDecodeError:
        abort(500)
    
    # Extract name and id
    domain_name = domain_data.get('name') or domain_data.get('domain') or domain_id.replace('_', ' ').title()
    domain_dict = dict(domain_data)
    domain_dict['name'] = domain_name
    domain_dict['id'] = domain_id
    if 'description' not in domain_dict:
        domain_dict['description'] = f"Domain data and pattern relationships for {domain_name}"
    
    # Get basic stats
    pattern_count = len(domain_dict.get('patterns', []))
    process_count = len(domain_dict.get('processes', []))
    perspective_count = len(domain_dict.get('perspectives', []))
    
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
    
    return render_template('domains/show.html',
                          title=domain_name,
                          domain=domain_dict,
                          pattern_count=pattern_count,
                          process_count=process_count,
                          perspective_count=perspective_count,
                          visualizations=domain_viz)

@domains_bp.route('/<domain_id>/patterns')
def domain_patterns(domain_id):
    """Show patterns for a specific domain."""
    domains_dir = Path(current_app.root_path).parent / 'data' / 'domains'
    domain_path = _safe_domain_path(domain_id)

    if domain_path.parent != domains_dir.resolve() or not domain_path.exists():
        abort(404)
    
    # Load the domain data
    try:
        with open(domain_path, 'r') as f:
            domain_data = json.load(f)
    except json.JSONDecodeError:
        abort(500)
    
    raw_patterns = domain_data.get('patterns', [])
    patterns_list = []
    if isinstance(raw_patterns, dict):
        for p_type, p_items in raw_patterns.items():
            if isinstance(p_items, list):
                for item in p_items:
                    if isinstance(item, dict):
                        item_copy = dict(item)
                        item_copy.setdefault('type', p_type.rstrip('s'))
                        patterns_list.append(item_copy)
                    elif isinstance(item, str):
                        patterns_list.append({'name': item, 'type': p_type.rstrip('s'), 'description': ''})
    elif isinstance(raw_patterns, list):
        for item in raw_patterns:
            if isinstance(item, dict):
                patterns_list.append(item)
            elif isinstance(item, str):
                patterns_list.append({'name': item, 'type': 'property', 'description': ''})
    else:
        for p_type in ['properties', 'processes', 'perspectives']:
            for item in domain_data.get(p_type, []):
                if isinstance(item, dict):
                    item_copy = dict(item)
                    item_copy.setdefault('type', p_type.rstrip('s'))
                    patterns_list.append(item_copy)
                elif isinstance(item, str):
                    patterns_list.append({'name': item, 'type': p_type.rstrip('s'), 'description': ''})
    
    # Group patterns by type
    pattern_groups = {
        'property': [],
        'process': [],
        'perspective': []
    }
    
    for pattern in patterns_list:
        p_type = pattern.get('type', 'property').lower()
        if p_type in pattern_groups:
            pattern_groups[p_type].append(pattern)
        else:
            pattern_groups['property'].append(pattern)
    
    pattern_types = [k.capitalize() for k, v in pattern_groups.items() if len(v) > 0]
    
    return render_template('domains/patterns.html',
                          title=f"Patterns: {domain_data.get('name', domain_id.title())}",
                          domain=domain_data,
                          patterns=patterns_list,
                          grouped_patterns=pattern_groups,
                          pattern_groups=pattern_groups,
                          pattern_types=pattern_types)

@domains_bp.route('/<domain_id>/api/data')
def domain_api_data(domain_id):
    """API endpoint to get domain data as JSON."""
    domains_dir = Path(current_app.root_path).parent / 'data' / 'domains'
    domain_path = _safe_domain_path(domain_id)

    if domain_path.parent != domains_dir.resolve() or not domain_path.exists():
        return jsonify({'error': 'Domain not found'}), 404
    
    # Load the domain data
    try:
        with open(domain_path, 'r') as f:
            domain_data = json.load(f)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid domain data'}), 500
    
    return jsonify(domain_data) 