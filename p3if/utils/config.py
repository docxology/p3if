"""
P3IF Configuration Utility

This module provides configuration management for P3IF.
"""
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union


class Config:
    """Configuration manager for P3IF."""
    
    DEFAULT_CONFIG = {
        "storage": {
            "type": "json",
            "path": "p3if-data.json"
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "visualization": {
            "default_style": "modern",
            "themes": {
                "modern": {
                    "colormap": "viridis",
                    "node_size": 50,
                    "edge_width": 1.5
                },
                "classic": {
                    "colormap": "coolwarm",
                    "node_size": 30,
                    "edge_width": 1.0
                }
            }
        },
        "analysis": {
            "default_algorithms": ["basic_stats", "centrality", "clustering"],
            "network_layout": "spring"
        },
        "export": {
            "formats": ["json", "csv", "graphml"]
        }
    }
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to configuration file
        """
        self._config = self.DEFAULT_CONFIG.copy()
        
        # Load from file if provided
        if config_file:
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: Union[str, Path]) -> None:
        """
        Load configuration from file.
        
        Args:
            config_file: Path to configuration file
        """
        path = Path(config_file)
        if path.exists():
            with open(path, 'r') as f:
                try:
                    loaded_config = json.load(f)
                    self._merge_config(loaded_config)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid configuration file: {e}")
        else:
            # Create default config file
            self.save_to_file(config_file)
    
    def save_to_file(self, config_file: Union[str, Path]) -> None:
        """
        Save configuration to file.
        
        Args:
            config_file: Path to save configuration file
        """
        path = Path(config_file)
        os.makedirs(path.parent, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """
        Merge new configuration with existing configuration.
        
        Args:
            new_config: New configuration to merge
        """
        for key, value in new_config.items():
            if key in self._config and isinstance(self._config[key], dict) and isinstance(value, dict):
                self._merge_dict(self._config[key], value)
            else:
                self._config[key] = value
    
    def _merge_dict(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively merge source dict into target dict.
        
        Args:
            target: Target dictionary
            source: Source dictionary
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dict(target[key], value)
            else:
                target[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by key.
        
        Args:
            key: Configuration key (dot notation supported)
            value: Configuration value
        """
        keys = key.split('.')
        target = self._config
        
        # Navigate to the last parent
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
            
        # Set the value
        target[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get the entire configuration.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy() 