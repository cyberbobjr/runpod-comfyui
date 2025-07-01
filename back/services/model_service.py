import os
from typing import Dict, List, Any
from .model_manager import ModelManager
from .download_service import DownloadService
from .config_service import ConfigService
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)


class ModelService:
    """
    High-level model querying service following Single Responsibility Principle.
    
    **Purpose:** Provides high-level model information and listing operations:
    - Simple model listing with basic status
    - Model existence checking
    - Basic model metadata operations
    - User-facing model queries
    
    **SRP Responsibility:** User-facing model information queries.
    This service provides simple, user-friendly model information.
    For complex model management use ModelManagementService.
    """
    
    @staticmethod
    def load_models() -> Dict[str, List[Dict[str, Any]]]:
        """
        Load models from the models.json file.
        
        **Description:** Loads model definitions from the configuration file.
        **Parameters:** None
        **Returns:** Dict containing model groups
        """
        data = ModelManager.load_models_json()
        groups = data.get("groups", {})
        return groups

    @staticmethod
    def list_models() -> List[Dict[str, Any]]:
        """
        Lists all models from JSON and their status on disk.
        
        **Description:** Returns a comprehensive list of all models with their status and progress.
        **Parameters:** None
        **Returns:** List of model information dictionaries
        """
        groups = ModelService.load_models()
        base_dir = ConfigService.get_base_dir()
        result = []
        
        for group, entries in groups.items():
            for entry in entries:
                dest = entry.get("dest")
                # Replace ${BASE_DIR} with the path determined above
                path = dest.replace("${BASE_DIR}", base_dir) if dest else None
                exists = os.path.exists(path) if path else False
                model_id = DownloadService.get_model_id(entry)
                progress = DownloadService.get_progress(model_id)
                
                # Explicit addition of tags in response (copy of entry to not modify original)
                entry_with_tags = dict(entry)
                if "tags" not in entry_with_tags:
                    entry_with_tags["tags"] = []
                
                # Check disk size if model exists and expected size is defined
                if exists and entry.get("size") is not None:
                    try:
                        actual_size = os.path.getsize(path)
                        expected_size = entry.get("size")
                        if actual_size != expected_size:
                            # Add "incorrect size" if not already present
                            tags = entry_with_tags["tags"]
                            if "incorrect size" not in tags:
                                tags.append("incorrect size")
                        else:
                            # Remove "incorrect size" if size is correct and tag is present
                            tags = entry_with_tags["tags"]
                            if "incorrect size" in tags:
                                tags.remove("incorrect size")
                    except Exception:
                        # If error reading size, add the tag
                        tags = entry_with_tags["tags"]
                        if "incorrect size" not in tags:
                            tags.append("incorrect size")
                
                result.append({
                    "group": group,
                    "entry": entry_with_tags,
                    "exists": exists,
                    "progress": progress.get("progress", 0),
                    "status": progress.get("status", "idle"),
                })
        
        return result

    @staticmethod
    def get_total_directory_size(path: str) -> int:
        """
        Calculate the total size of a directory.
        
        **Description:** Recursively calculates the total size of all files in a directory.
        **Parameters:**
        - `path` (str): Directory path to calculate size for
        **Returns:** int containing the total size in bytes
        """
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except Exception:
                    pass
        return total

    @staticmethod
    def get_total_size() -> Dict[str, Any]:
        """
        Returns the total size (in bytes) of the base_dir directory.
        
        **Description:** Calculates and returns the total disk space used by the ComfyUI installation.
        **Parameters:** None
        **Returns:** Dict containing base directory path and total size
        """
        base_dir = os.environ.get("COMFYUI_MODEL_DIR", ".")
        size = ModelService.get_total_directory_size(base_dir)
        return {"base_dir": base_dir, "total_size": size}
