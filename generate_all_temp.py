#!/usr/bin/env python3
"""
Generate All Script for P3IF Website (Temporary Version)

This script only runs the sample data generation step, skipping the problematic steps.
"""
import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger()

def run_script(script_path, args=None):
    """
    Run a Python script with the given arguments.
    
    Args:
        script_path: Path to the script to run
        args: List of arguments to pass to the script
        
    Returns:
        True if the script executed successfully, False otherwise
    """
    if args is None:
        args = []
    
    cmd = [sys.executable, str(script_path)] + args
    logger.info(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running script {script_path}: {e}")
        return False

def ensure_directory(path):
    """
    Ensure a directory exists.
    
    Args:
        path: Path to the directory
        
    Returns:
        The Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def generate_all(output_dir=None, open_browser=False):
    """
    Generate website content (only sample data).
    
    Args:
        output_dir: Base output directory
        open_browser: Whether to open the browser after generation
        
    Returns:
        True if all steps completed successfully, False otherwise
    """
    # Set up paths
    scripts_dir = Path(__file__).parent
    website_dir = scripts_dir.parent
    
    if output_dir is None:
        output_dir = website_dir / "output"
    else:
        output_dir = Path(output_dir)
    
    # Ensure output directories exist
    ensure_directory(output_dir)
    visualization_data_dir = ensure_directory(output_dir / "visualization_data")
    
    # Step 1: Generate sample data
    logger.info("Step 1: Generating sample data")
    sample_data_script = scripts_dir / "generate_sample_data.py"
    if not run_script(sample_data_script):
        logger.error("Failed to generate sample data")
        return False
    
    logger.info("Sample data generation completed successfully!")
    logger.info(f"Output directory: {output_dir}")
    
    return True

def main():
    """Main function to parse arguments and run the generation process."""
    parser = argparse.ArgumentParser(description="Generate P3IF sample data only")
    parser.add_argument("--output-dir", help="Base output directory")
    parser.add_argument("--open-browser", action="store_true", help="Open the browser after generation")
    args = parser.parse_args()
    
    generate_all(output_dir=args.output_dir, open_browser=args.open_browser)

if __name__ == "__main__":
    main() 