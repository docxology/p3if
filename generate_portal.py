#!/usr/bin/env python3
"""
Generate Portal Script for P3IF Website

This script generates the visualization portal for the P3IF website by
creating an index page that links to all visualizations.
"""
import logging
import json
import argparse
import os
import sys
import webbrowser
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import p3if
sys.path.append(str(Path(__file__).parent.parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

from p3if.utils.json import P3IFEncoder

def generate_portal(domains_dir, domain_index, output_dir, open_browser=False):
    """
    Generate the visualization portal.
    
    Args:
        domains_dir: Directory containing domain data files
        domain_index: Path to the domain index file
        output_dir: Directory to save the portal to
        open_browser: Whether to open the browser after generation
        
    Returns:
        Path to the generated portal HTML file
    """
    logger.info(f"Generating portal from {domain_index}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load domain index
    with open(domain_index, 'r') as f:
        index_data = json.load(f)
    
    # Generate HTML
    portal_html = generate_portal_html(index_data)
    
    # Write to file
    portal_file = os.path.join(output_dir, "index.html")
    with open(portal_file, 'w') as f:
        f.write(portal_html)
    
    logger.info(f"Portal saved to {portal_file}")
    
    # Open in browser if requested
    if open_browser:
        logger.info(f"Opening portal in browser")
        webbrowser.open(f"file://{os.path.abspath(portal_file)}")
    
    return portal_file

def generate_portal_html(index_data):
    """
    Generate the HTML for the visualization portal.
    
    Args:
        index_data: Domain index data
        
    Returns:
        HTML string for the portal
    """
    # Start with HTML header
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>P3IF Visualization Portal</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        h2 {
            color: #444;
            margin-top: 30px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .domain-list, .relationship-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .domain-card, .relationship-card {
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        .domain-card:hover, .relationship-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .domain-card h3, .relationship-card h3 {
            margin-top: 0;
            color: #333;
        }
        .domain-card p, .relationship-card p {
            color: #666;
            font-size: 14px;
        }
        a {
            color: #0066cc;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .combined-viz {
            margin-top: 30px;
            text-align: center;
        }
        .combined-button {
            display: inline-block;
            background-color: #0066cc;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
        }
        .combined-button:hover {
            background-color: #0055bb;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>P3IF Visualization Portal</h1>
"""
    
    # Add domains section
    html += """
        <h2>Domain Visualizations</h2>
        <div class="domain-list">
"""
    
    # Add domain cards
    for domain in index_data.get("domains", []):
        domain_id = domain.get("id")
        domain_name = domain.get("name", domain_id.title())
        domain_desc = domain.get("description", "")
        
        html += f"""
            <div class="domain-card">
                <h3>{domain_name}</h3>
                <p>{domain_desc}</p>
                <a href="../visualizations/{domain_id}_visualization.html" target="_blank">View Visualization</a>
            </div>
"""
    
    html += """
        </div>
"""
    
    # Add relationship sets section
    html += """
        <h2>Cross-Domain Relationship Sets</h2>
        <div class="relationship-list">
"""
    
    # Add relationship cards
    for relationship_set in index_data.get("relationshipSets", []):
        rel_id = relationship_set.get("id")
        rel_name = relationship_set.get("name", rel_id.title())
        rel_desc = relationship_set.get("description", "")
        
        html += f"""
            <div class="relationship-card">
                <h3>{rel_name}</h3>
                <p>{rel_desc}</p>
                <a href="../visualizations/{rel_id}_visualization.html" target="_blank">View Visualization</a>
            </div>
"""
    
    html += """
        </div>
"""
    
    # Add combined visualization link
    html += """
        <div class="combined-viz">
            <h2>Combined Visualization</h2>
            <p>View all domains and relationships in a single interactive visualization.</p>
            <a href="../visualizations/combined_visualization.html" target="_blank" class="combined-button">
                Launch Combined Visualization
            </a>
        </div>
"""
    
    # Close HTML
    html += """
    </div>
</body>
</html>
"""
    
    return html

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate visualization portal for P3IF website')
    parser.add_argument('--domains-dir', required=True, help='Directory containing domain data files')
    parser.add_argument('--domain-index', required=True, help='Path to domain index file')
    parser.add_argument('--output-dir', required=True, help='Directory to save portal to')
    parser.add_argument('--open-browser', action='store_true', help='Open portal in browser after generation')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    generate_portal(args.domains_dir, args.domain_index, args.output_dir, args.open_browser) 