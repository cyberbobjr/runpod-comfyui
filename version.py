"""
Version management for the application.
This module provides version information for the entire application.
"""

import json
from pathlib import Path

# Application version information
__version__ = "2.0.0"
__build__ = "20250622-1430"
__description__ = "Configuration and Settings Management Refactoring"

def get_version_info():
    """
    Get comprehensive version information from version.json file.
    
    Returns:
        dict: Version information including version, build, and components
    """
    try:
        # Get the directory where this script is located
        current_dir = Path(__file__).parent
        version_file = current_dir / "version.json"
        
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Fallback to hardcoded values if version.json not found
            return {
                "version": __version__,
                "build": __build__,
                "buildDate": "2025-06-22T14:30:00Z",
                "components": {
                    "api": __version__,
                    "ui": __version__
                },
                "description": __description__
            }
    except Exception as e:
        print(f"Warning: Could not load version.json: {e}")
        return {
            "version": __version__,
            "build": __build__,
            "description": __description__
        }

def get_version():
    """
    Get the current application version.
    
    Returns:
        str: Version string (e.g., "2.0.0")
    """
    return get_version_info().get("version", __version__)

def get_build():
    """
    Get the current build identifier.
    
    Returns:
        str: Build string (e.g., "20250622-1430")
    """
    return get_version_info().get("build", __build__)

def print_version_info():
    """
    Print comprehensive version information to console.
    Useful for startup logs and debugging.
    """
    info = get_version_info()
    print("=" * 50)
    print(f"🚀 ComfyUI Model Manager v{info.get('version', __version__)}")
    print(f"📦 Build: {info.get('build', __build__)}")
    print(f"📅 Build Date: {info.get('buildDate', 'Unknown')}")
    print(f"📝 Description: {info.get('description', __description__)}")
    
    components = info.get('components', {})
    if components:
        print("🔧 Components:")
        for component, version in components.items():
            print(f"   - {component.upper()}: v{version}")
    
    print("=" * 50)

# For backward compatibility
VERSION = __version__
BUILD = __build__
