#!/usr/bin/env python3
"""
Script to update import statements across the codebase.
Replaces 'from ' with 'from ' in all Python files.
"""
import os
import re
from pathlib import Path


def update_imports_in_file(file_path):
    """Update import statements in a single file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace 'from ' with 'from '
    updated_content = re.sub(r'from p3if\.', 'from ', content)
    
    # Check if any changes were made
    if content != updated_content:
        print(f"Updating {file_path}")
        with open(file_path, 'w') as f:
            f.write(updated_content)


def update_all_imports(root_path='.'):
    """Update imports in all Python files in the directory tree."""
    root = Path(root_path)
    python_files = list(root.glob("**/*.py"))
    
    # Add common paths to check first
    key_directories = [
        "core", "data", "utils", "analysis", "visualization", "scripts", "tests"
    ]
    
    updated_count = 0
    
    # First process files in key directories
    for directory in key_directories:
        dir_path = root / directory
        if dir_path.exists() and dir_path.is_dir():
            dir_files = [f for f in python_files if str(f).startswith(str(dir_path))]
            for file_path in dir_files:
                update_imports_in_file(file_path)
                updated_count += 1
    
    print(f"Updated imports in {updated_count} files.")


if __name__ == "__main__":
    update_all_imports() 