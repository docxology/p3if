#!/usr/bin/env python3
"""
Verify Imports for P3IF Project.

This script verifies that all necessary modules can be imported,
which helps confirm that the package structure is correct.
"""
import sys
import os
from pathlib import Path

def check_import(module_name):
    """Try to import a module and return True if successful."""
    try:
        __import__(module_name)
        print(f"✅ Successfully imported {module_name}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False

def main():
    """Check all required imports."""
    print("Verifying P3IF imports...")
    
    # Add project root to path
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    
    print(f"Project root: {project_root}")
    print(f"Current path: {sys.path}")
    
    # Add the project root to the path
    sys.path.insert(0, str(project_root))
    
    # Try both namespaced and direct imports
    imports_to_check = [
        # Core modules
        "core.framework",
        "core.models",
        "p3if.core.framework",
        "p3if.core.models",
        
        # Data modules
        "data.synthetic",
        "data.domains",
        "data.importers",
        "data.exporters",
        "p3if.data.synthetic",
        "p3if.data.domains",
        "p3if.data.importers",
        "p3if.data.exporters",
        
        # Visualization modules
        "visualization.portal",
        "visualization.network",
        "visualization.matrix",
        "visualization.dashboard",
        "visualization.interactive",
        "p3if.visualization.portal",
        "p3if.visualization.network",
        "p3if.visualization.matrix",
        "p3if.visualization.dashboard",
        "p3if.visualization.interactive",
        
        # Scripts
        "scripts.fix_visualization_paths",
        "scripts.ensure_website_references",
        "p3if.scripts.fix_visualization_paths",
        "p3if.scripts.ensure_website_references",
        
        # Utils
        "utils.config",
        "utils.storage",
        "p3if.utils.config",
        "p3if.utils.storage",
        
        # Third-party dependencies
        "numpy",
        "pandas",
        "matplotlib",
        "beautifulsoup4",
        "markdown",
    ]
    
    success_count = 0
    for module_name in imports_to_check:
        if check_import(module_name):
            success_count += 1
    
    print(f"\nImport verification complete: {success_count}/{len(imports_to_check)} imports successful")
    
if __name__ == "__main__":
    main() 