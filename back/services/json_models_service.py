"""
JSON Models Service - Handle JSON model management operations

This module contains business logic for JSON model management including:
- Configuration management
- Path normalization
- Group ordering
- Model existence checking
"""

import os
from typing import Dict, List, Optional, Any

from .config_service import ConfigService
from .model_manager import ModelManager
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)


class JsonModelsService:
    """
    JSON model configuration service following Single Responsibility Principle.
    
    **Purpose:** Handles JSON model configuration operations including:
    - Model configuration normalization and validation
    - Path normalization and resolution
    - Model group ordering and organization
    - Model existence checking and status tracking
    - Configuration file structure management
    
    **SRP Responsibility:** JSON model configuration management and validation.
    This service should focus on JSON configuration operations and delegate
    file operations to ModelManager and status tracking to other services.
    """
    
    def __init__(self):
        """Initialize the JSON models service."""
        self.base_dir = ConfigService.get_base_dir()
    
    def normalize_path(self, path: str, base_dir: Optional[str] = None) -> str:
        """
        Normalize a path with BASE_DIR variable substitution.
        
        **Description:** Normalizes paths to use forward slashes and BASE_DIR variable.
        **Parameters:**
        - `path` (str): Path to normalize
        - `base_dir` (str, optional): Base directory for relative paths
        **Returns:** Normalized path string
        """
        if not path:
            return path
        
        # Convert all backslashes to forward slashes
        path = path.replace('\\', '/')
        
        # If the path already contains ${BASE_DIR}, don't modify it
        if "${BASE_DIR}" in path:
            return path
        
        # If base_dir is not provided, use the centralized BASE_DIR
        if not base_dir:
            base_dir = self.base_dir
        
        # Normalize the base_dir as well
        base_dir = base_dir.replace('\\', '/')
        
        # Remove trailing slash from base_dir for consistency
        if base_dir.endswith('/'):
            base_dir = base_dir[:-1]
        
        # If path is absolute and starts with base_dir, make it relative with ${BASE_DIR}
        if os.path.isabs(path):
            path_normalized = os.path.normpath(path).replace('\\', '/')
            base_dir_normalized = os.path.normpath(base_dir).replace('\\', '/')
            
            if path_normalized.startswith(base_dir_normalized):
                relative_part = path_normalized[len(base_dir_normalized):].lstrip('/')
                if relative_part:
                    return f"${{BASE_DIR}}/{relative_part}"
                else:
                    return "${BASE_DIR}"
        
        # If path is relative, add ${BASE_DIR}/ prefix
        if not path.startswith('/') and not path.startswith('${BASE_DIR}'):
            return f"${{BASE_DIR}}/{path}"
        
        return path
    
    def model_exists_on_disk(self, entry: Dict[str, Any], base_dir: Optional[str] = None) -> bool:
        """
        Check if a model file exists on disk.
        
        **Description:** Verifies model file existence by checking the dest path.
        **Parameters:**
        - `entry` (Dict[str, Any]): Model entry with dest field
        - `base_dir` (str, optional): Base directory to resolve relative paths
        **Returns:** True if model file exists, False otherwise
        """
        if not base_dir:
            base_dir = self.base_dir
        
        dest = entry.get("dest")
        if not dest:
            return False
        
        # Resolve ${BASE_DIR} variable
        if "${BASE_DIR}" in dest:
            dest = dest.replace("${BASE_DIR}", base_dir)
        
        # Convert to absolute path if relative
        if not os.path.isabs(dest):
            dest = os.path.join(base_dir, dest)
        
        return os.path.isfile(dest)
    
    def get_models_data_with_existence(self) -> Dict[str, Any]:
        """
        Get complete models data with existence checking.
        
        **Description:** Loads models.json and adds existence status for each model.
        **Parameters:** None
        **Returns:** Models data dictionary with existence flags
        """
        data = ModelManager.load_models_json()
        base_dir = self.base_dir
        
        # Add 'exists' field for each model in each group
        groups = data.get("groups", {})
        for group_name, entries in groups.items():
            for entry in entries:
                entry["exists"] = self.model_exists_on_disk(entry, base_dir)
        
        return data
    
    def get_config_info(self) -> Dict[str, str]:
        """
        Get configuration information with source tracking.
        
        **Description:** Returns BASE_DIR and its source (user_config, models_json, etc.).
        **Parameters:** None
        **Returns:** Dictionary with BASE_DIR and source information
        """
        # Get current BASE_DIR via ModelManager priority logic
        current_base_dir = self.base_dir
        
        # Determine the source of BASE_DIR for information
        source = "default"
        if os.environ.get("BASE_DIR"):
            source = "environment"
        elif os.path.exists(ConfigService.get_user_config_path()):
            user_config = ConfigService.load_user_config()
            if user_config.get("BASE_DIR"):
                source = "user_config"
        else:
            data = ModelManager.load_models_json()
            if data.get("config", {}).get("BASE_DIR"):
                source = "models_json"
        
        return {
            "BASE_DIR": current_base_dir,
            "source": source
        }
    
    def update_config(self, base_dir: str) -> Dict[str, Any]:
        """
        Update the BASE_DIR configuration.
        
        **Description:** Updates BASE_DIR in user-specific config.json.
        **Parameters:**
        - `base_dir` (str): New base directory path
        **Returns:** Dictionary with success status and message
        **Raises:** Exception for file system errors
        """
        try:
            # Save to custom config.json file
            ModelManager.update_user_base_dir(base_dir)
            
            logger.info(f"User configuration updated: BASE_DIR = {base_dir}")
            return {
                "ok": True, 
                "message": f"Configuration updated. BASE_DIR set to '{base_dir}' in config.json"
            }
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            raise
    
    def get_group_order(self) -> List[str]:
        """
        Get the current order of model groups.
        
        **Description:** Returns the ordered list of group names.
        **Parameters:** None
        **Returns:** List of group names in current order
        """
        data = ModelManager.load_models_json()
        groups = data.get("groups", {})
        
        # Check if there's a saved order
        config = data.get("config", {})
        saved_order = config.get("group_order", [])
        
        # If saved order exists and contains all groups, use it
        if saved_order and set(saved_order) == set(groups.keys()):
            return saved_order
        
        # Otherwise, return alphabetical order
        return sorted(groups.keys())
    
    def set_group_order(self, order: List[str]) -> Dict[str, Any]:
        """
        Set the order of model groups.
        
        **Description:** Updates the group order configuration.
        **Parameters:**
        - `order` (List[str]): List of group names in desired order
        **Returns:** Dictionary with success status and message
        **Raises:** ValueError for invalid group names
        """
        data = ModelManager.load_models_json()
        groups = data.get("groups", {})
        
        # Validate that all groups in order exist
        existing_groups = set(groups.keys())
        ordered_groups = set(order)
        
        if existing_groups != ordered_groups:
            missing = existing_groups - ordered_groups
            extra = ordered_groups - existing_groups
            error_parts = []
            if missing:
                error_parts.append(f"missing groups: {list(missing)}")
            if extra:
                error_parts.append(f"unknown groups: {list(extra)}")
            raise ValueError(f"Invalid group order - {', '.join(error_parts)}")
        
        # Update config with new order
        if "config" not in data:
            data["config"] = {}
        data["config"]["group_order"] = order
        
        # Save the updated data
        ModelManager.save_models_json(data)
        
        logger.info(f"Group order updated: {order}")
        return {
            "ok": True,
            "message": "Group order updated successfully",
            "order": order
        }
    
    def get_groups_list(self) -> List[str]:
        """
        Get list of all model groups.
        
        **Description:** Returns all group names in current order.
        **Parameters:** None
        **Returns:** List of group names
        """
        return self.get_group_order()
    
    def create_group(self, group_name: str) -> Dict[str, Any]:
        """
        Create a new model group.
        
        **Description:** Creates a new empty model group.
        **Parameters:**
        - `group_name` (str): Name of the group to create
        **Returns:** Dictionary with success status and message
        **Raises:** ValueError if group already exists
        """
        data = ModelManager.load_models_json()
        
        if group_name in data.get("groups", {}):
            raise ValueError(f"Group '{group_name}' already exists")
        
        if "groups" not in data:
            data["groups"] = {}
        data["groups"][group_name] = []
        
        ModelManager.save_models_json(data)
        
        logger.info(f"Group '{group_name}' created")
        return {
            "ok": True,
            "message": f"Group '{group_name}' created successfully"
        }
    
    def update_group_name(self, old_name: str, new_name: str) -> Dict[str, Any]:
        """
        Rename a model group.
        
        **Description:** Renames a group and updates all references.
        **Parameters:**
        - `old_name` (str): Current group name
        - `new_name` (str): New group name
        **Returns:** Dictionary with success status and message
        **Raises:** ValueError for validation errors
        """
        data = ModelManager.load_models_json()
        groups = data.get("groups", {})
        
        if old_name not in groups:
            raise ValueError(f"Group '{old_name}' does not exist")
        
        if new_name in groups:
            raise ValueError(f"Group '{new_name}' already exists")
        
        # Copy content and delete old group
        groups[new_name] = groups[old_name]
        del groups[old_name]
        
        # Update group order if it exists
        config = data.get("config", {})
        if "group_order" in config:
            order = config["group_order"]
            if old_name in order:
                index = order.index(old_name)
                order[index] = new_name
        
        # Update references in bundles
        if "bundles" in data:
            for bundle_name, bundle in data["bundles"].items():
                if "models" in bundle and old_name in bundle["models"]:
                    index = bundle["models"].index(old_name)
                    bundle["models"][index] = new_name
        
        ModelManager.save_models_json(data)
        
        logger.info(f"Group renamed from '{old_name}' to '{new_name}'")
        return {
            "ok": True,
            "message": f"Group renamed from '{old_name}' to '{new_name}'"
        }
    
    def delete_group(self, group_name: str) -> Dict[str, Any]:
        """
        Delete a model group.
        
        **Description:** Deletes a group if it's not referenced by bundles.
        **Parameters:**
        - `group_name` (str): Name of the group to delete
        **Returns:** Dictionary with success status and message
        **Raises:** ValueError if group is in use or doesn't exist
        """
        data = ModelManager.load_models_json()
        groups = data.get("groups", {})
        
        if group_name not in groups:
            raise ValueError(f"Group '{group_name}' does not exist")
        
        # Check if group is used in bundles
        group_used_in_bundles = []
        if "bundles" in data:
            for bundle_name, bundle in data["bundles"].items():
                if "models" in bundle and group_name in bundle["models"]:
                    group_used_in_bundles.append(bundle_name)
        
        if group_used_in_bundles:
            raise ValueError(
                f"Group '{group_name}' is used in bundles: {', '.join(group_used_in_bundles)}"
            )
        
        # Remove from groups
        del groups[group_name]
        
        # Remove from group order if it exists
        config = data.get("config", {})
        if "group_order" in config:
            order = config["group_order"]
            if group_name in order:
                order.remove(group_name)
        
        ModelManager.save_models_json(data)
        
        logger.info(f"Group '{group_name}' deleted")
        return {
            "ok": True,
            "message": f"Group '{group_name}' deleted successfully"
        }
    
    def get_group_models(self, group_name: str) -> List[Dict[str, Any]]:
        """
        Get all models in a specific group.
        
        **Description:** Returns all model entries for the specified group.
        **Parameters:**
        - `group_name` (str): Name of the group
        **Returns:** List of model entries
        **Raises:** ValueError if group doesn't exist
        """
        data = ModelManager.load_models_json()
        groups = data.get("groups", {})
        
        if group_name not in groups:
            raise ValueError(f"Group '{group_name}' does not exist")
        
        return groups[group_name]
    
    def add_model_entry(self, group_name: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a model entry to a group.
        
        **Description:** Adds a new model entry with path normalization.
        **Parameters:**
        - `group_name` (str): Target group name
        - `entry` (Dict[str, Any]): Model entry data
        **Returns:** Dictionary with success status and message
        **Raises:** ValueError for validation errors
        """
        data = ModelManager.load_models_json()
        
        if "groups" not in data:
            data["groups"] = {}
        
        if group_name not in data["groups"]:
            data["groups"][group_name] = []
        
        # Normalize the destination path
        if entry.get("dest"):
            entry["dest"] = self.normalize_path(entry["dest"])
        
        # Check for duplicates
        for existing_entry in data["groups"][group_name]:
            if existing_entry.get("dest") == entry.get("dest"):
                raise ValueError("Model with this destination already exists")
        
        # Add the entry
        data["groups"][group_name].append(entry)
        ModelManager.save_models_json(data)
        
        logger.info(f"Model entry added to group '{group_name}'")
        return {
            "ok": True,
            "message": "Model entry added successfully"
        }
    
    def update_model_entry(self, group_name: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a model entry in a group.
        
        **Description:** Updates an existing model entry or adds if not found.
        **Parameters:**
        - `group_name` (str): Target group name
        - `entry` (Dict[str, Any]): Model entry data
        **Returns:** Dictionary with success status and message
        """
        data = ModelManager.load_models_json()
        
        if "groups" not in data:
            data["groups"] = {}
        
        if group_name not in data["groups"]:
            data["groups"][group_name] = []
        
        # Normalize the destination path
        if entry.get("dest"):
            entry["dest"] = self.normalize_path(entry["dest"])
        
        # Find existing entry by destination or git
        model_id = entry.get("dest") or entry.get("git")
        if not model_id:
            raise ValueError("Entry must have either dest or git field")
        
        found = False
        for i, existing_entry in enumerate(data["groups"][group_name]):
            existing_id = existing_entry.get("dest") or existing_entry.get("git")
            if existing_id == model_id:
                data["groups"][group_name][i] = entry
                found = True
                break
        
        if not found:
            data["groups"][group_name].append(entry)
        
        ModelManager.save_models_json(data)
        
        message = "Model entry updated" if found else "Model entry added"
        logger.info(f"{message} in group '{group_name}'")
        return {
            "ok": True,
            "message": message
        }
    
    def delete_model_entry(self, group_name: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a model entry from a group.
        
        **Description:** Removes a model entry by destination or git identifier.
        **Parameters:**
        - `group_name` (str): Target group name
        - `entry` (Dict[str, Any]): Model entry to delete
        **Returns:** Dictionary with success status and message
        **Raises:** ValueError if entry not found
        """
        data = ModelManager.load_models_json()
        groups = data.get("groups", {})
        
        if group_name not in groups:
            raise ValueError(f"Group '{group_name}' does not exist")
        
        # Find entry to delete
        model_id = entry.get("dest") or entry.get("git")
        if not model_id:
            raise ValueError("Cannot identify model to delete")
        
        found_index = None
        for i, existing_entry in enumerate(groups[group_name]):
            existing_id = existing_entry.get("dest") or existing_entry.get("git")
            if existing_id == model_id:
                found_index = i
                break
        
        if found_index is None:
            raise ValueError("Model entry not found")
        
        # Remove the entry
        del groups[group_name][found_index]
        ModelManager.save_models_json(data)
        
        logger.info(f"Model entry deleted from group '{group_name}'")
        return {
            "ok": True,
            "message": "Model entry deleted successfully"
        }
