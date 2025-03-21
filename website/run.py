#!/usr/bin/env python3
"""
P3IF Website Runner

This script starts the P3IF website with improved startup information
and handles shutdown more gracefully.
"""

import os
import sys
import logging
from pathlib import Path

# Ensure we're in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("p3if.runner")

def print_route_info():
    """Print information about available routes."""
    print("\n" + "=" * 80)
    print(" P3IF Web Interface ".center(80, "="))
    print("=" * 80)
    
    rules = sorted([(rule.endpoint, rule.rule) for rule in app.url_map.iter_rules()
                  if not rule.rule.startswith('/static')])
    
    # Group routes by blueprint
    blueprints = {}
    for endpoint, rule in rules:
        bp_name = endpoint.split('.')[0] if '.' in endpoint else 'app'
        if bp_name not in blueprints:
            blueprints[bp_name] = []
        blueprints[bp_name].append((endpoint, rule))
    
    # Print routes by blueprint
    for bp_name, routes in sorted(blueprints.items()):
        print(f"\n[{bp_name.upper()}]")
        for endpoint, rule in routes:
            print(f"  {rule:<40} -> {endpoint}")
    
    print("\n" + "=" * 80)
    print(" Server Information ".center(80, "="))
    print(f"  * Running on http://localhost:5000")
    print(f"  * Documentation available at http://localhost:5000/docs/")
    print(f"  * Visualizations available at http://localhost:5000/visualizations/")
    print(f"  * Domains explorer available at http://localhost:5000/domains/")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    try:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Print welcome message and route information
        print_route_info()
        
        # Run the Flask application
        app.run(
            debug=True, 
            host='0.0.0.0', 
            port=5000,
            extra_files=None,
            use_reloader=True,
            reloader_interval=1,
            reloader_type="watchdog",
            exclude_patterns=["**/tests/*", "**/setup.py"]
        )
    except KeyboardInterrupt:
        print("\nServer shutdown requested. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        sys.exit(1) 