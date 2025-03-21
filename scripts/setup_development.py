#!/usr/bin/env python3
"""
Setup Development Environment for P3IF Project.

This script installs the p3if package in development mode, installs required dependencies,
and sets up the proper environment for running tests.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main function to set up the development environment."""
    print("Setting up P3IF development environment...")
    
    # Get project root directory
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    
    # Change to project root
    os.chdir(project_root)
    print(f"Working in directory: {project_root}")
    
    # Install package in development mode
    print("Installing p3if package in development mode...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
    
    # Install required dependencies
    print("Installing required dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Install web dependencies for website tests
    print("Installing web dependencies for tests...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
    
    print("P3IF development environment setup complete!")
    print("\nYou can now run tests with:")
    print("  cd tests/visualization")
    print("  python run_all_tests.py")

if __name__ == "__main__":
    main() 