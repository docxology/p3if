#!/usr/bin/env python3
"""
P3IF Website Runner - Stable Version

This script starts the P3IF website with improved stability by ignoring 
most project files to prevent constant restarting.
"""

import os
import sys
import logging
from pathlib import Path

# Ensure we're in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Import the Flask app
from app import app

print("\n" + "=" * 80)
print(" P3IF Web Interface ".center(80, "="))
print("=" * 80)
print(f"  * Running on http://localhost:5000")
print(f"  * Documentation at http://localhost:5000/docs/")
print(f"  * Visualizations at http://localhost:5000/visualizations/")
print(f"  * Domains explorer at http://localhost:5000/domains/")
print("=" * 80 + "\n")

if __name__ == '__main__':
    try:
        # Only watch files in the website directory
        app.run(
            debug=True, 
            host='0.0.0.0', 
            port=5000,
            use_reloader=True,
            extra_files=None,
            reloader_type="stat",  # Use stat instead of watchdog for fewer triggers
            exclude_patterns=[
                # Exclude all test files
                "**/tests/*",
                # Exclude all library files
                "**/core/*", 
                "**/data/*",
                "**/analysis/*",
                "**/visualization/*",
                "**/utils/*",
                "**/scripts/*"
            ]
        )
    except KeyboardInterrupt:
        print("\nServer shutdown requested. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        sys.exit(1) 