#!/usr/bin/env python3
"""
P3IF Website - Main Application

This is the main entry point for the P3IF website, which provides a web interface
to explore and interact with the P3IF framework, including:

1. Documentation browsing
2. Domain exploration
3. Visualization access
4. Framework demonstration
"""

import os
import json
import markdown
import logging
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort

# Import route modules
from website.routes.docs import docs_bp
from website.routes.domains import domains_bp
from website.routes.visualizations import viz_bp
from website.routes.api import api_bp
from website.routes.viz_generate import viz_generate_bp

# Ensure directories exist
os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)

# Initialize Flask app
app = Flask(__name__, 
           static_folder="static",
           template_folder="templates")

# Set a secret key for session management
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'p3if-development-key')

# Register blueprints
app.register_blueprint(docs_bp, url_prefix='/docs')
app.register_blueprint(domains_bp, url_prefix='/domains')
app.register_blueprint(viz_bp, url_prefix='/visualizations')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(viz_generate_bp, url_prefix='/visualizations')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logs', 'website.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set the project root
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_ROOT = PROJECT_ROOT / 'docs'
OUTPUT_ROOT = PROJECT_ROOT / 'output'
DOMAINS_ROOT = PROJECT_ROOT / 'data' / 'domains'

# Main routes
@app.route('/')
def index():
    """Home page route."""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page route."""
    return render_template('about.html')

@app.context_processor
def utility_processor():
    """Make utility functions available to templates."""
    def markdown_to_html(md_content):
        return markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
    
    return dict(markdown_to_html=markdown_to_html)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.error(f"Server error: {str(e)}")
    return render_template('500.html'), 500

# Direct static file serving for specific directories
@app.route('/output/<path:path>')
def serve_output(path):
    """Serve files from the output directory."""
    if '..' in path or path.startswith('/'):
        abort(404)  # Security check
    full_path = OUTPUT_ROOT / path
    if not full_path.exists():
        abort(404)
    directory = str(full_path.parent)
    filename = full_path.name
    return send_from_directory(directory, filename)

# Alias for backward compatibility
app.add_url_rule('/static-output/<path:filename>', 'static_output', serve_output)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, 
           extra_files=None,  # Don't watch any extra files
           use_reloader=True,
           reloader_interval=1,
           reloader_type="watchdog",
           exclude_patterns=["**/tests/*", "**/setup.py"])  # Exclude test files and setup.py 