import os
from typing import Dict, List, Optional, Any
from .model_manager import ModelManager
from .download_manager import DownloadManager
from .config_service import ConfigService
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)


class ModelManagementService:
    """
    Advanced model management service following Single Responsibility Principle.
    
    **Purpose:** Handles complex model management operations including:
    - Complete model data with download progress integration
    - Model group management and manipulation
    - Advanced model entry operations (add/edit/delete)
    - Model installation coordination
    - Model status aggregation with download progress
    
    **SRP Responsibility:** Complex model management operations and state coordination.
    This service coordinates between ModelManager and DownloadManager for
    comprehensive model management operations.
    """
    
    @staticmethod
    def get_complete_models_data() -> Dict[str, Any]:
        """
        Retrieves the complete models.json file with status information.
        
        **Description:** Gets all model data including existence status and download progress.
        **Parameters:** None
        **Returns:** Dict containing configuration, groups, bundles with status info
        """
        data = ModelManager.load_models_json()
        base_dir = ConfigService.get_base_dir()
        
        # Add 'exists' and 'status' properties to each model
        groups = data.get("groups", {})
        downloads = DownloadManager.get_all_progress()
        
        for _, entries in groups.items():
            for entry in entries:
                entry["exists"] = ModelManager.model_exists_on_disk(entry, base_dir)
                model_id = entry.get("dest") or entry.get("git")
                if model_id in downloads:
                    entry["status"] = downloads[model_id].get("status", "downloading")
                    entry["progress"] = downloads[model_id].get("progress", 0)
                else:
                    entry["status"] = None
                    entry["progress"] = None
        
        return data
    
    @staticmethod
    def get_groups() -> List[str]:
        """
        Retrieves all existing model group names.
        
        **Description:** Gets a list of all model group names.
        **Parameters:** None
        **Returns:** List of group names
        """
        data = ModelManager.load_models_json()
        return list(data.get("groups", {}).keys())
    
    @staticmethod
    def create_group(group_name: str) -> bool:
        """
        Creates a new empty model group.
        
        **Description:** Creates a new model group if it doesn't exist.
        **Parameters:**
        - `group_name` (str): Name of the group to create
        **Returns:** bool indicating success
        """
        data = ModelManager.load_models_json()
        
        if group_name in data.get("groups", {}):
            raise ValueError(f"Group '{group_name}' already exists")
        
        if "groups" not in data:
            data["groups"] = {}
        
        data["groups"][group_name] = []
        ModelManager.save_models_json(data)
        return True
    
    @staticmethod
    def rename_group(old_name: str, new_name: str) -> bool:
        """
        Renames a model group and updates bundle references.
        
        **Description:** Renames a group while preserving all models and updating bundle references.
        **Parameters:**
        - `old_name` (str): Current group name
        - `new_name` (str): New group name
        **Returns:** bool indicating success
        """
        data = ModelManager.load_models_json()
        
        if old_name not in data.get("groups", {}):
            raise ValueError(f"Group '{old_name}' does not exist")
        
        if new_name in data.get("groups", {}):
            raise ValueError(f"Group '{new_name}' already exists")
        
        # Copy content and delete old group
        data["groups"][new_name] = data["groups"][old_name]
        del data["groups"][old_name]
        
        # Update references in bundles
        if "bundles" in data:
            for bundle_name, bundle in data["bundles"].items():
                if "models" in bundle and old_name in bundle["models"]:
                    index = bundle["models"].index(old_name)
                    bundle["models"][index] = new_name
        
        ModelManager.save_models_json(data)
        return True
    
    @staticmethod
    def delete_group(group_name: str) -> bool:
        """
        Deletes a model group if not referenced by bundles.
        
        **Description:** Deletes a group only if it's not used in any bundles.
        **Parameters:**
        - `group_name` (str): Name of the group to delete
        **Returns:** bool indicating success
        """
        data = ModelManager.load_models_json()
        
        if group_name not in data.get("groups", {}):
            raise ValueError(f"Group '{group_name}' does not exist")
        
        # Check if group is used in bundles
        group_used_in_bundles = []
        if "bundles" in data:
            for bundle_name, bundle in data["bundles"].items():
                if "models" in bundle and group_name in bundle["models"]:
                    group_used_in_bundles.append(bundle_name)
        
        if group_used_in_bundles:
            raise ValueError(f"Group '{group_name}' is used in bundles: {', '.join(group_used_in_bundles)}")
        
        del data["groups"][group_name]
        ModelManager.save_models_json(data)
        return True
    
    @staticmethod
    def get_group_models(group_name: str) -> List[Dict[str, Any]]:
        """
        Retrieves all models in a specific group.
        
        **Description:** Gets all model entries for a given group.
        **Parameters:**
        - `group_name` (str): Name of the group
        **Returns:** List of model entries
        """
        data = ModelManager.load_models_json()
        
        if group_name not in data.get("groups", {}):
            raise ValueError(f"Group '{group_name}' does not exist")
        
        return data["groups"][group_name]
    
    @staticmethod
    def add_model_entry(group_name: str, entry: Dict[str, Any]) -> bool:
        """
        Adds a new model entry to a group.
        
        **Description:** Adds a model entry with validation and conflict checking.
        **Parameters:**
        - `group_name` (str): Target group name
        - `entry` (Dict[str, Any]): Model entry data
        **Returns:** bool indicating success
        """
        data = ModelManager.load_models_json()
        
        if "groups" not in data:
            data["groups"] = {}
        
        if group_name not in data["groups"]:
            data["groups"][group_name] = []
        
        # Validation
        if not entry.get("url") and not entry.get("git"):
            raise ValueError("Entry must contain either a URL or git repository")
        
        # Normalize path
        base_dir = data.get("config", {}).get("BASE_DIR", "")
        if entry.get("dest"):
            try:
                from back.services.json_models_service import JsonModelsService
                json_service = JsonModelsService()
                entry["dest"] = json_service.normalize_path(entry["dest"], base_dir)
            except ImportError:
                pass  # Function not available, use as-is
        
        # Check for duplicates
        if entry.get("dest"):
            for existing_entry in data["groups"][group_name]:
                if existing_entry.get("dest") == entry["dest"]:
                    raise ValueError("Model with this destination already exists")
        
        # Add model to group
        data["groups"][group_name].append(entry)
        ModelManager.save_models_json(data)
        return True
    
    @staticmethod
    def update_model_entry(group_name: str, entry: Dict[str, Any]) -> bool:
        """
        Updates an existing model entry or adds it if not found.
        
        **Description:** Updates a model entry based on dest or git identifier.
        **Parameters:**
        - `group_name` (str): Target group name
        - `entry` (Dict[str, Any]): Model entry data
        **Returns:** bool indicating if entry was updated (True) or added (False)
        """
        data = ModelManager.load_models_json()
        
        if "groups" not in data:
            data["groups"] = {}
        
        # Normalize path
        base_dir = data.get("config", {}).get("BASE_DIR", "")
        if entry.get("dest"):
            try:
                from back.services.json_models_service import JsonModelsService
                json_service = JsonModelsService()
                entry["dest"] = json_service.normalize_path(entry["dest"], base_dir)
            except ImportError:
                pass
        
        if group_name not in data["groups"]:
            data["groups"][group_name] = []
        
        # Identifier for search
        model_id = entry.get("dest") or entry.get("git")
        if not model_id:
            raise ValueError("Entry must have dest or git for identification")
        
        # Search for entry to update
        found = False
        for i, existing_entry in enumerate(data["groups"][group_name]):
            existing_id = existing_entry.get("dest") or existing_entry.get("git")
            if existing_id == model_id:
                data["groups"][group_name][i] = entry
                found = True
                break
        
        # If not found, add as new
        if not found:
            data["groups"][group_name].append(entry)
        
        ModelManager.save_models_json(data)
        return found
    
    @staticmethod
    def delete_model_entry(group_name: str, entry: Dict[str, Any]) -> bool:
        """
        Deletes a model entry from a group.
        
        **Description:** Removes a model entry based on dest or git identifier.
        **Parameters:**
        - `group_name` (str): Group containing the model
        - `entry` (Dict[str, Any]): Entry to delete
        **Returns:** bool indicating success
        """
        data = ModelManager.load_models_json()
        
        if group_name not in data.get("groups", {}):
            raise ValueError(f"Group '{group_name}' does not exist")
        
        # Identifier for search
        model_id = entry.get("dest") or entry.get("git")
        if not model_id:
            raise ValueError("Entry must have dest or git for identification")
        
        # Search and remove
        for i, existing_entry in enumerate(data["groups"][group_name]):
            existing_id = existing_entry.get("dest") or existing_entry.get("git")
            if existing_id == model_id:
                del data["groups"][group_name][i]
                ModelManager.save_models_json(data)
                return True
        
        raise ValueError("Model entry not found")
    
    @staticmethod
    def delete_model_file(entry: Dict[str, Any]) -> bool:
        """
        Deletes a model file from disk.
        
        **Description:** Removes the actual model file from the filesystem.
        **Parameters:**
        - `entry` (Dict[str, Any]): Model entry containing file path
        **Returns:** bool indicating success
        """
        base_dir = ConfigService.get_base_dir()
        dest = entry.get("dest")
        
        if not dest:
            raise ValueError("Entry must have a destination path")
        
        file_path = dest.replace("${BASE_DIR}", base_dir)
        
        if not os.path.exists(file_path):
            raise ValueError("File does not exist")
        
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path)
            return True
        except OSError as e:
            raise ValueError(f"Failed to delete file: {e}")
    
    @staticmethod
    def get_model_id(entry: Dict[str, Any]) -> str:
        """
        Generate a unique identifier for a model entry.
        
        **Description:** Creates a unique ID based on destination or git URL.
        **Parameters:**
        - `entry` (Dict[str, Any]): Model entry
        **Returns:** str containing the unique identifier
        """
        return entry.get("dest") or entry.get("git")
