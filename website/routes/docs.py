"""
Documentation Routes

This module provides routes for browsing and displaying P3IF documentation
from the /docs directory.
"""

import os
import markdown
from pathlib import Path
from flask import Blueprint, render_template, abort, current_app

docs_bp = Blueprint('docs', __name__, template_folder='../templates')

@docs_bp.route('/')
def index():
    """Documentation home page."""
    docs_root = Path(current_app.root_path).parent / 'docs'
    readme_path = docs_root / 'README.md'
    
    if not readme_path.exists():
        return render_template('docs/index.html')
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    return render_template('docs/markdown.html', 
                          title='Documentation',
                          content=content,
                          breadcrumbs=[{'name': 'Docs', 'url': '/docs/'}])

@docs_bp.route('/<path:doc_path>')
def show_doc(doc_path):
    """Display a specific documentation file."""
    docs_root = Path(current_app.root_path).parent / 'docs'
    
    # Normalize path and prevent directory traversal
    doc_path = os.path.normpath(doc_path)
    if doc_path.startswith('..') or doc_path.startswith('/'):
        abort(404)
    
    # Handle both .md files and directories with README.md
    file_path = docs_root / doc_path
    
    if file_path.is_dir():
        file_path = file_path / 'README.md'
        if not file_path.exists():
            # List directory contents
            return render_template('docs/directory.html',
                                 title=f"Directory: {doc_path}",
                                 path=doc_path,
                                 items=get_directory_contents(docs_root / doc_path),
                                 breadcrumbs=build_breadcrumbs(doc_path))
    
    # If path doesn't have .md extension, try adding it
    if not str(file_path).endswith('.md'):
        test_path = str(file_path) + '.md'
        if os.path.exists(test_path):
            file_path = Path(test_path)
    
    # Ensure the file exists
    if not file_path.exists():
        abort(404)
    
    # Read and render the Markdown content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Create the title from the filename
    title = file_path.stem.replace('_', ' ').title()
    
    return render_template('docs/markdown.html',
                          title=title,
                          content=content,
                          breadcrumbs=build_breadcrumbs(doc_path))

def get_directory_contents(dir_path):
    """Get contents of a directory, organized by type."""
    items = {'directories': [], 'files': []}
    
    if not dir_path.exists() or not dir_path.is_dir():
        return items
    
    for item in dir_path.iterdir():
        if item.name.startswith('.'):
            continue
            
        if item.is_dir():
            items['directories'].append({
                'name': item.name,
                'path': str(item.relative_to(dir_path.parent)),
                'type': 'directory'
            })
        elif item.suffix.lower() == '.md':
            items['files'].append({
                'name': item.stem.replace('_', ' ').title(),
                'path': str(item.relative_to(dir_path.parent)),
                'type': 'file'
            })
    
    # Sort directories and files alphabetically
    items['directories'].sort(key=lambda x: x['name'])
    items['files'].sort(key=lambda x: x['name'])
    
    return items

def build_breadcrumbs(path):
    """Build breadcrumb navigation for the given path."""
    breadcrumbs = [{'name': 'Docs', 'url': '/docs/'}]
    
    if not path:
        return breadcrumbs
    
    parts = path.split('/')
    current_path = ''
    
    for i, part in enumerate(parts):
        current_path = os.path.join(current_path, part)
        name = part.replace('_', ' ').title()
        
        if i == len(parts) - 1:
            # Last part (current page)
            breadcrumbs.append({'name': name, 'url': None})
        else:
            breadcrumbs.append({'name': name, 'url': f'/docs/{current_path}'})
    
    return breadcrumbs 