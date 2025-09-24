"""
Configuration settings for P3IF visualization tests.

This module provides test configuration constants and helper functions 
to set up the visualization test environment.
"""
import os
import tempfile
from pathlib import Path
import logging
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('viz_test_config')

# Define the standard output directory for all tests
TEST_OUTPUT_DIR = Path(__file__).parent / "test_output"
os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

# Test configuration constants
DEFAULT_TEST_SETTINGS = {
    # Test framework generation settings
    "FRAMEWORK": {
        "SMALL": {
            "num_properties": 5,
            "num_processes": 5,
            "num_perspectives": 5,
            "num_relationships": 20,
        },
        "MEDIUM": {
            "num_properties": 10,
            "num_processes": 10,
            "num_perspectives": 10,
            "num_relationships": 50,
        },
        "LARGE": {
            "num_properties": 20,
            "num_processes": 20,
            "num_perspectives": 20,
            "num_relationships": 150,
        }
    },
    
    # Multi-domain test settings
    "MULTI_DOMAIN": {
        "SMALL": {
            "domains": ["Domain1", "Domain2"],
            "patterns_per_domain": 5,
            "relationships_per_domain": 10,
            "cross_domain_relationships": 5,
        },
        "MEDIUM": {
            "domains": ["Domain1", "Domain2", "Domain3"],
            "patterns_per_domain": 10,
            "relationships_per_domain": 20,
            "cross_domain_relationships": 10,
        },
        "LARGE": {
            "domains": ["Domain1", "Domain2", "Domain3", "Domain4", "Domain5"],
            "patterns_per_domain": 15,
            "relationships_per_domain": 30,
            "cross_domain_relationships": 20,
        }
    },
    
    # Visualization settings
    "VISUALIZATION": {
        "DEFAULT_OUTPUT_DIR": str(TEST_OUTPUT_DIR),
        "FIGURE_SIZE": (10, 8),
        "DPI": 100,
        "COLOR_PALETTE": "viridis",
        "NODE_SIZE": 300,
        "EDGE_WIDTH": 1.5,
        "FONT_SIZE": 10
    },
    
    # Test datasets
    "TEST_DATASETS": [
        {"id": "dataset1", "name": "Simple Framework"},
        {"id": "dataset2", "name": "Multi-Domain Framework"},
        {"id": "dataset3", "name": "Large Complex Framework"}
    ],
    
    # Visualization components
    "VISUALIZATION_COMPONENTS": [
        {"id": "3d-cube", "name": "3D Cube", "description": "3D visualization of P3IF relationships"},
        {"id": "network", "name": "Network Graph", "description": "Network visualization of P3IF elements"},
        {"id": "matrix", "name": "Matrix View", "description": "Matrix visualization of P3IF relationships"},
        {"id": "dashboard", "name": "Dashboard", "description": "Interactive dashboard with multiple views"}
    ],
    
    # Libraries check
    "REQUIRED_LIBRARIES": [
        "numpy",
        "matplotlib",
        "seaborn",
        "networkx",
        "pandas",
        "plotly",
        "dash",
        "beautifulsoup4"
    ]
}


def get_temp_output_dir():
    """
    Create a directory for test outputs.
    
    Returns:
        Path: Path object to the output directory
    """
    # Always return the standard test output directory
    return TEST_OUTPUT_DIR


def save_test_config(config=None, path=None):
    """
    Save the test configuration to a JSON file.
    
    Args:
        config (dict): Configuration dictionary (uses DEFAULT_TEST_SETTINGS if None)
        path (str): Path to save the configuration file (uses test output dir if None)
        
    Returns:
        Path: Path to the saved configuration file
    """
    config = config or DEFAULT_TEST_SETTINGS
    
    if path is None:
        # Save to the standard test output directory
        path = TEST_OUTPUT_DIR / "test_config.json"
    
    with open(path, 'w') as f:
        json.dump(config, f, indent=4)
    
    logger.info(f"Test configuration saved to {path}")
    return Path(path)


def load_test_config(path=None):
    """
    Load the test configuration from a JSON file.
    
    Args:
        path (str): Path to the configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    if path is None:
        # Return default settings if no path provided
        return DEFAULT_TEST_SETTINGS
    
    try:
        with open(path, 'r') as f:
            config = json.load(f)
        logger.info(f"Test configuration loaded from {path}")
        return config
    except Exception as e:
        logger.error(f"Error loading test configuration: {e}")
        logger.info("Using default test settings")
        return DEFAULT_TEST_SETTINGS


def check_library_availability():
    """
    Check if all required libraries are available.
    
    Returns:
        tuple: (all_available, missing_libraries)
    """
    missing_libraries = []
    
    for library in DEFAULT_TEST_SETTINGS["REQUIRED_LIBRARIES"]:
        try:
            __import__(library)
        except ImportError:
            missing_libraries.append(library)
    
    all_available = len(missing_libraries) == 0
    
    if not all_available:
        logger.warning(f"Missing required libraries: {', '.join(missing_libraries)}")
        logger.warning("Some tests may fail due to missing dependencies")
    else:
        logger.info("All required libraries are available")
    
    return all_available, missing_libraries


def setup_test_environment():
    """
    Set up the test environment with default settings.
    
    Returns:
        dict: Environment settings
    """
    # Check library availability
    libraries_available, missing_libraries = check_library_availability()
    
    # Create the standard output directory
    output_dir = get_temp_output_dir()
    
    # Save default configuration
    config_path = save_test_config()
    
    # Return environment settings
    return {
        "libraries_available": libraries_available,
        "missing_libraries": missing_libraries,
        "output_dir": output_dir,
        "config_path": config_path,
        "settings": DEFAULT_TEST_SETTINGS
    }


# Initialize the test environment if this module is imported
if __name__ != "__main__":
    check_library_availability()


# Example usage if run as a script
if __name__ == "__main__":
    env = setup_test_environment()
    print(f"Test environment set up:")
    print(f"- Output directory: {env['output_dir']}")
    print(f"- Configuration file: {env['config_path']}")
    print(f"- Libraries available: {env['libraries_available']}")
    if not env['libraries_available']:
        print(f"- Missing libraries: {', '.join(env['missing_libraries'])}") 