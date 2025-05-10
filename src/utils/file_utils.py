"""
Utility functions for file operations.
"""
import os
import json
from typing import Dict, Any, Optional


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration values
        
    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        json.JSONDecodeError: If the configuration file is not valid JSON
    """
    with open(config_path, 'r') as f:
        return json.load(f)


def save_config(config_path: str, config: Dict[str, Any]) -> None:
    """
    Save configuration to a JSON file.
    
    Args:
        config_path: Path to the configuration file
        config: Dictionary containing configuration values
    """
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def ensure_directory(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
    """
    os.makedirs(directory_path, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """
    Get the extension of a file.
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension (including the dot)
    """
    return os.path.splitext(filename)[1]
