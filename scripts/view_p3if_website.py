#!/usr/bin/env python3
"""
Simple script to open the P3IF interactive visualization website in a web browser.
"""
import os
import sys
import webbrowser
from pathlib import Path


def open_website():
    """Open the P3IF website in the default web browser."""
    # Define the path to the website
    website_path = Path("output/p3if_full_website.html")
    
    if not website_path.exists():
        print(f"Error: Website file not found at {website_path}")
        print("Please run 'python3 scripts/test_3d_cube_with_domains.py' first to generate the website.")
        print("Then move the generated files to the output directory.")
        return False
    
    # Convert to absolute path with file:// protocol
    file_url = f"file://{os.path.abspath(website_path)}"
    
    print(f"Opening P3IF interactive visualization website at: {file_url}")
    webbrowser.open(file_url)
    
    print("\nNavigation Instructions:")
    print("- Click and drag to rotate the 3D cube")
    print("- Use mouse wheel to zoom in/out")
    print("- Hold Shift and drag to pan the view")
    print("- Use the domain dropdown at the top to select different domains")
    
    return True


if __name__ == "__main__":
    if not open_website():
        sys.exit(1)
    
    print("\nFor more information, see:")
    print("- docs/visualization/technical_documentation.md - Comprehensive documentation")
    print("- docs/visualization/user_guide.md - Step-by-step user guide") 