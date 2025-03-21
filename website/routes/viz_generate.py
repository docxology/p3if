#!/usr/bin/env python3
"""
Visualization generation routes for P3IF website.
Handles routes for visualization creation and processing.
"""

import os
import sys
import json
import logging
import uuid
import time
from datetime import datetime
from pathlib import Path
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    current_app, flash, jsonify, session
)

# Make sure the core module is available
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import necessary functionality from the visualization module
try:
    from visualization.matrix import MatrixVisualizer
    from visualization.network import NetworkVisualizer
    from visualization.interactive import InteractiveVisualizer
    
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    logging.error(f"Failed to import from visualization module: {str(e)}")
    VISUALIZATION_AVAILABLE = False

try:
    from core.framework import P3IFFramework
    FRAMEWORK_AVAILABLE = True
except ImportError as e:
    logging.error(f"Failed to import P3IFFramework: {str(e)}")
    FRAMEWORK_AVAILABLE = False

# Create blueprint
viz_generate_bp = Blueprint('viz_generate_bp', __name__)

# Define the output directory for visualizations
OUTPUT_DIR = Path('output')

def get_available_domains():
    """Get list of available domains from the data directory."""
    domain_dir = Path('data/domains')
    domains = []
    
    if domain_dir.exists():
        # Try to load index.json first
        index_path = domain_dir / 'index.json'
        if index_path.exists():
            try:
                with open(index_path, 'r') as f:
                    domains_data = json.load(f)
                    # Process index data
                    for domain in domains_data.get('domains', []):
                        domains.append({
                            'id': domain.get('id'),
                            'name': domain.get('name'),
                            'description': domain.get('description', ''),
                            'pattern_count': domain.get('pattern_count', 0)
                        })
                return domains
            except json.JSONDecodeError:
                logging.error(f"Failed to parse {index_path}")
        
        # Fall back to reading individual domain files
        for file_path in domain_dir.glob('*.json'):
            if file_path.name == 'index.json':
                continue
                
            try:
                with open(file_path, 'r') as f:
                    domain_data = json.load(f)
                    pattern_count = len(domain_data.get('patterns', []))
                    domains.append({
                        'id': file_path.stem,
                        'name': domain_data.get('name', file_path.stem),
                        'description': domain_data.get('description', ''),
                        'pattern_count': pattern_count
                    })
            except json.JSONDecodeError:
                logging.error(f"Failed to parse {file_path}")
                continue
    
    # Sort domains by name
    domains.sort(key=lambda x: x['name'])
    return domains

def get_recent_visualizations(limit=5):
    """Get list of recently generated visualizations."""
    if not OUTPUT_DIR.exists():
        return []
    
    visualizations = []
    viz_dirs = [d for d in OUTPUT_DIR.iterdir() if d.is_dir()]
    
    # Sort by modification time (most recent first)
    viz_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for viz_dir in viz_dirs[:limit]:
        # Try to load metadata
        meta_path = viz_dir / 'metadata.json'
        if meta_path.exists():
            try:
                with open(meta_path, 'r') as f:
                    meta = json.load(f)
                
                visualizations.append({
                    'id': viz_dir.name,
                    'title': meta.get('title', viz_dir.name),
                    'description': meta.get('description', ''),
                    'type': meta.get('visualization_type', 'Unknown'),
                    'domains': meta.get('domains', []),
                    'date': datetime.fromtimestamp(meta.get('created_at', 0)).strftime('%Y-%m-%d')
                })
            except (json.JSONDecodeError, KeyError) as e:
                logging.error(f"Failed to parse metadata for {viz_dir.name}: {e}")
                # Fallback to basic info
                visualizations.append({
                    'id': viz_dir.name,
                    'title': viz_dir.name,
                    'description': 'Visualization output',
                    'type': 'Unknown',
                    'domains': [],
                    'date': datetime.fromtimestamp(viz_dir.stat().st_mtime).strftime('%Y-%m-%d')
                })
    
    return visualizations

@viz_generate_bp.route('/generate', methods=['GET'])
def show_generate_form():
    """Display form for generating visualizations."""
    available_domains = get_available_domains()
    recent_visualizations = get_recent_visualizations()
    
    # Get query parameters for preselecting domains
    preselected_domains = request.args.getlist('domains')
    
    return render_template(
        'visualizations/generate.html',
        domains=available_domains,
        recent_visualizations=recent_visualizations,
        preselected_domains=preselected_domains,
        core_available=VISUALIZATION_AVAILABLE
    )

@viz_generate_bp.route('/generate', methods=['POST'])
def generate_visualization():
    """Handle visualization generation form submission."""
    # Check if core functionality is available
    if not VISUALIZATION_AVAILABLE:
        flash("Visualization generation is unavailable: Visualization module could not be imported", "error")
        return redirect(url_for('viz_generate_bp.show_generate_form'))
    
    # Get form data
    selected_domains = request.form.getlist('domains')
    viz_type = request.form.get('viz_type')
    output_name = request.form.get('output_name')
    similarity_threshold = float(request.form.get('similarity_threshold', 0.5))
    include_summary = 'include_summary' in request.form
    save_data = 'save_data' in request.form
    
    # Validate selected domains
    if len(selected_domains) < 2:
        flash("Please select at least two domains for comparison", "error")
        return redirect(url_for('viz_generate_bp.show_generate_form'))
    
    # Create output directory name if not provided
    if not output_name:
        timestamp = int(time.time())
        domains_part = "_".join(selected_domains[:3])
        if len(selected_domains) > 3:
            domains_part += f"_plus{len(selected_domains)-3}"
        output_name = f"{domains_part}_{viz_type}_{timestamp}"
    
    # Clean output name (replace spaces, remove special chars)
    output_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in output_name)
    
    # Create output directory
    output_path = OUTPUT_DIR / output_name
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if output_path.exists():
        # Append unique identifier if directory already exists
        output_name = f"{output_name}_{uuid.uuid4().hex[:8]}"
        output_path = OUTPUT_DIR / output_name
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load domain data
    domain_data = {}
    domains_info = []
    for domain_id in selected_domains:
        domain_file = Path(f"data/domains/{domain_id}.json")
        if not domain_file.exists():
            flash(f"Domain file not found: {domain_id}", "error")
            continue
            
        try:
            with open(domain_file, 'r') as f:
                data = json.load(f)
                domain_data[domain_id] = data
                domains_info.append({
                    'id': domain_id,
                    'name': data.get('name', domain_id),
                    'description': data.get('description', '')
                })
        except json.JSONDecodeError:
            flash(f"Failed to parse domain file: {domain_id}", "error")
            continue
    
    if not domain_data:
        flash("No valid domain data found", "error")
        return redirect(url_for('viz_generate_bp.show_generate_form'))
    
    # Set generation status in session
    session['viz_generation'] = {
        'status': 'processing',
        'output_dir': output_name,
        'start_time': time.time()
    }
    
    # Create metadata file
    metadata = {
        'title': f"Visualization of {', '.join(d['name'] for d in domains_info)}",
        'description': f"Comparison of patterns across {len(domains_info)} domains",
        'domains': [d['id'] for d in domains_info],
        'domain_names': [d['name'] for d in domains_info],
        'visualization_type': viz_type,
        'created_at': time.time(),
        'similarity_threshold': similarity_threshold,
        'generated_by': 'web_interface'
    }
    
    with open(output_path / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Save source data if requested
    if save_data:
        data_dir = output_path / 'data'
        data_dir.mkdir(exist_ok=True)
        for domain_id, data in domain_data.items():
            with open(data_dir / f"{domain_id}.json", 'w') as f:
                json.dump(data, f, indent=2)
    
    # Begin generation based on visualization type
    try:
        if viz_type == 'matrix':
            matrix_visualizer = MatrixVisualizer(None)  # We'll just use static methods
            # Create output file path
            output_file = output_path / "similarity_matrix.html"
            matrix_visualizer.visualize_similarity_matrix(
                file_path=output_file,
                pattern_type="property"  # default to properties
            )
            result = str(output_file)
        elif viz_type == 'network':
            network_visualizer = NetworkVisualizer(None)  # We'll just use static methods
            # Create output file path
            output_file = output_path / "network_graph.html"
            network_visualizer.visualize_full_network(
                file_path=output_file,
                layout="spring"
            )
            result = str(output_file)
        elif viz_type == 'cube':
            interactive_visualizer = InteractiveVisualizer(None)  # We'll just use static methods
            # Create output file path
            output_file = output_path / "3d_cube.html"
            interactive_visualizer.generate_3d_cube_html(
                output_file=output_file,
                title=f"3D Pattern Cube - {', '.join(selected_domains)}"
            )
            result = str(output_file)
        else:
            flash(f"Unknown visualization type: {viz_type}", "error")
            return redirect(url_for('viz_generate_bp.show_generate_form'))
        
        # Update metadata with result
        metadata['output_file'] = result
        
        # Generate analysis summary if requested
        if include_summary:
            # For now, skip summary generation as we don't have the method
            # Just mark it as false in metadata
            metadata['has_summary'] = False
        
        # Update session status
        session['viz_generation'] = {
            'status': 'complete',
            'output_dir': output_name,
            'end_time': time.time()
        }
        
        flash(f"Visualization successfully generated", "success")
        return redirect(url_for('visualizations.show_visualization', output_dir=output_name))
        
    except Exception as e:
        logging.error(f"Visualization generation failed: {e}", exc_info=True)
        
        # Update session status
        session['viz_generation'] = {
            'status': 'failed',
            'output_dir': output_name,
            'error': str(e),
            'end_time': time.time()
        }
        
        # Create error file for debugging
        with open(output_path / 'error.txt', 'w') as f:
            f.write(f"Error generating visualization: {e}\n")
        
        flash(f"Failed to generate visualization: {e}", "error")
        return redirect(url_for('viz_generate_bp.show_generate_form'))

@viz_generate_bp.route('/generate/status')
def generation_status():
    """Get the status of the current visualization generation."""
    status_data = session.get('viz_generation', {})
    return jsonify(status_data) 