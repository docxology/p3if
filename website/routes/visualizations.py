"""
Visualization Routes

This module provides routes for displaying P3IF visualizations from the output directory.
"""

import os
import json
from pathlib import Path
from flask import Blueprint, render_template, abort, current_app, redirect, url_for

viz_bp = Blueprint('visualizations', __name__, template_folder='../templates')

@viz_bp.route('/')
def index():
    """Visualization gallery home page."""
    output_root = Path(current_app.root_path).parent / 'output'
    
    # Get all visualization output directories
    viz_dirs = []
    for item in output_root.iterdir():
        if not item.is_dir():
            continue
            
        # Check if this directory has visualizations
        viz_path = item / 'visualizations'
        if not viz_path.exists():
            continue
            
        # Get visualization info
        viz_info = {
            'id': item.name,
            'name': item.name.replace('_', ' ').title(),
            'path': str(item.relative_to(output_root)),
            'has_3d_cube': (viz_path / '3d-cube.html').exists(),
            'has_force_graph': (viz_path / 'force-graph.html').exists(),
            'has_overview': (viz_path / 'overview').exists(),
            'has_domain': (viz_path / 'domain').exists(),
            'has_compare': (viz_path / 'compare').exists(),
            'date': get_directory_date(item)
        }
        
        viz_dirs.append(viz_info)
    
    # Sort by date (newest first)
    viz_dirs.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('visualizations/index.html',
                          title='Visualizations',
                          visualization_dirs=viz_dirs)

@viz_bp.route('/<output_dir>')
def show_visualization(output_dir):
    """Show a specific visualization output directory."""
    output_root = Path(current_app.root_path).parent / 'output'
    viz_path = output_root / output_dir / 'visualizations'
    
    if not viz_path.exists():
        abort(404)
    
    # Get available visualization types
    viz_types = {
        '3d_cube': {
            'path': '3d-cube.html',
            'exists': (viz_path / '3d-cube.html').exists(),
            'name': '3D Cube',
            'description': 'Interactive 3D visualization of the P3IF framework'
        },
        'force_graph': {
            'path': 'force-graph.html',
            'exists': (viz_path / 'force-graph.html').exists(),
            'name': 'Force Graph',
            'description': 'Network visualization of pattern relationships'
        },
        'overview': {
            'path': 'overview',
            'exists': (viz_path / 'overview').exists(),
            'name': 'Overview',
            'description': 'Overview dashboard visualizations'
        },
        'domain': {
            'path': 'domain',
            'exists': (viz_path / 'domain').exists(),
            'name': 'Domain',
            'description': 'Domain-specific visualizations'
        },
        'compare': {
            'path': 'compare',
            'exists': (viz_path / 'compare').exists(),
            'name': 'Compare',
            'description': 'Comparative visualizations across domains'
        }
    }
    
    # Get summary data if available
    summary_data = {}
    summary_path = output_root / output_dir / 'data' / 'summary.json'
    if summary_path.exists():
        try:
            with open(summary_path, 'r') as f:
                summary_data = json.load(f)
        except json.JSONDecodeError:
            pass
    
    return render_template('visualizations/detail.html',
                          title=f'Visualization: {output_dir}',
                          output_dir=output_dir,
                          viz_types=viz_types,
                          summary=summary_data)

@viz_bp.route('/<output_dir>/type/<viz_type>')
def show_visualization_type(output_dir, viz_type):
    """Show a specific visualization type from an output directory."""
    output_root = Path(current_app.root_path).parent / 'output'
    
    # Handle interactive visualizations
    if viz_type in ['3d_cube', 'force_graph']:
        file_name = '3d-cube.html' if viz_type == '3d_cube' else 'force-graph.html'
        return redirect(f'/output/{output_dir}/visualizations/{file_name}')
    
    # Handle static visualization directories
    if viz_type in ['overview', 'domain', 'compare']:
        viz_path = output_root / output_dir / 'visualizations' / viz_type
        
        if not viz_path.exists():
            abort(404)
        
        # Get all image files in the directory
        images = []
        for img in viz_path.glob('*.png'):
            images.append({
                'name': img.stem.replace('_', ' ').title(),
                'path': f'/output/{output_dir}/visualizations/{viz_type}/{img.name}',
                'filename': img.name
            })
        
        return render_template('visualizations/gallery.html',
                              title=f'{viz_type.title()} Visualizations',
                              output_dir=output_dir,
                              viz_type=viz_type,
                              images=images)
    
    abort(404)

def get_directory_date(dir_path):
    """Get the modification date of a directory."""
    try:
        return dir_path.stat().st_mtime
    except:
        return 0 