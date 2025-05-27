import os
import json
import logging
from fastapi import APIRouter, HTTPException, Depends, Body, File, UploadFile
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from fastapi.responses import JSONResponse, FileResponse
import shutil
from api import protected, get_env_file_path
from model_utils import ModelManager

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router creation for models.json API routes
jsonmodels_router = APIRouter(prefix="/api/jsonmodels")

MODELS_JSON = "models.json"
WORKFLOW_DIR = None  # Will be retrieved dynamically

def get_models_json_path():
    """Returns the full path of the models.json file by trying several possible locations."""
    return ModelManager.get_models_json_path()

def load_models_json():
    """Loads the complete models.json file with improved error handling."""
    return ModelManager.load_models_json()

def save_models_json(data):
    """Saves the complete models.json file with improved error handling."""
    return ModelManager.save_models_json(data)

def normalize_path(path, base_dir=None):
    """
    Normalizes a path to:
    1. Replace all Windows separators with Unix separators (/)
    2. Make it relative to ${BASE_DIR} if necessary while respecting directory structure
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
        base_dir = ModelManager.get_base_dir()
    
    # Normalize base_dir (forward slashes and no trailing slash)
    base_dir = base_dir.replace('\\', '/').rstrip('/')
    
    # Determine if the path is already relative to base_dir
    is_absolute = os.path.isabs(path)
    
    if is_absolute:
        # If the path is absolute, check if it's in base_dir
        if path.startswith(base_dir):
            # Extract the relative part
            relative_path = path[len(base_dir):].lstrip('/')
            return f"${{BASE_DIR}}/{relative_path}"
        else:
            # The absolute path is not in base_dir, can't make it relative
            logger.warning(f"Path '{path}' is not in '{base_dir}', cannot make it relative")
            return path
    else:
        # For relative paths, check if they start with a subdirectory of base_dir
        
        # Extract the last directory of base_dir as a potential marker
        # For example, if base_dir is '/path/to/models', the marker is 'models'
        base_dir_parts = base_dir.split('/')
        base_dir_marker = base_dir_parts[-1] if base_dir_parts else None
        
        if base_dir_marker and path.startswith(f"{base_dir_marker}/"):
            # The path already starts with the base directory name, consider it relative to parent(base_dir)
            return f"${{BASE_DIR}}/{path[len(base_dir_marker)+1:]}"
        elif any(part == base_dir_marker for part in path.split('/')):
            # If a part of the path is the marker, extract from that part
            parts = path.split('/')
            if base_dir_marker in parts:
                idx = parts.index(base_dir_marker)
                return f"${{BASE_DIR}}/{'/'.join(parts[idx+1:])}"
        
        # No pattern recognized, simply add ${BASE_DIR}/ as prefix
        return f"${{BASE_DIR}}/{path}"

def model_exists_on_disk(entry, base_dir):
    """
    Determines if the model (file) exists on disk.
    """
    if not base_dir:
        base_dir = ModelManager.get_base_dir()
    return ModelManager.model_exists_on_disk(entry, base_dir)

class ModelEntry(BaseModel):
    url: Optional[str] = None
    dest: Optional[str] = None
    git: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[List[str]] = []
    src: Optional[str] = None
    hash: Optional[str] = None
    size: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    system_requirements: Optional[Dict[str, Any]] = None

class ModelEntryRequest(BaseModel):
    group: str
    entry: ModelEntry

class ModelGroupRequest(BaseModel):
    group: str

class UpdateModelGroupRequest(BaseModel):
    old_group: str
    new_group: str

class ConfigUpdateRequest(BaseModel):
    base_dir: str

@jsonmodels_router.get("/", response_model=Dict[str, Any])
def get_models_data(user=Depends(protected)):
    """
    Route: GET /api/jsonmodels/
    Role: Retrieves the complete models.json file with existence check for each model
    Input arguments: None (authenticated user via dependency)
    Output format: Dict containing:
      - config: Dict with BASE_DIR configuration
      - groups: Dict where keys are group names and values are lists of ModelEntry objects
      - Each ModelEntry includes an 'exists' boolean field indicating if the model file exists on disk
    """
    data = load_models_json()
    base_dir = ModelManager.get_base_dir()
    # Add 'exists' field for each model in each group
    groups = data.get("groups", {})
    for group_name, entries in groups.items():
        for entry in entries:
            entry["exists"] = model_exists_on_disk(entry, base_dir)
    return data

@jsonmodels_router.get("/config", response_model=Dict[str, str])
def get_config(user=Depends(protected)):
    """
    Route: GET /api/jsonmodels/config
    Role: Retrieves the configuration section from models.json
    Input arguments: None (authenticated user via dependency)
    Output format: Dict containing configuration key-value pairs (typically BASE_DIR)
    """
    data = load_models_json()
    return data.get("config", {})

@jsonmodels_router.post("/config")
def update_config(config: ConfigUpdateRequest, user=Depends(protected)):
    """
    Route: POST /api/jsonmodels/config
    Role: Updates the configuration section in models.json
    Input arguments: 
      - config: ConfigUpdateRequest with base_dir string
      - user: authenticated user via dependency
    Output format: Dict with 'ok' boolean and 'message' string confirming update
    """
    data = load_models_json()
    data["config"] = {"BASE_DIR": config.base_dir}
    save_models_json(data)
    return {"ok": True, "message": "Configuration updated"}

@jsonmodels_router.get("/groups", response_model=List[str])
def get_groups(user=Depends(protected)):
    """
    Route: GET /api/jsonmodels/groups
    Role: Retrieves the list of all model group names
    Input arguments: None (authenticated user via dependency)
    Output format: List of strings representing group names
    """
    data = load_models_json()
    return list(data.get("groups", {}).keys())

@jsonmodels_router.post("/groups")
def create_group(group_request: ModelGroupRequest, user=Depends(protected)):
    """
    Route: POST /api/jsonmodels/groups
    Role: Creates a new empty model group
    Input arguments:
      - group_request: ModelGroupRequest with group name string
      - user: authenticated user via dependency
    Output format: Dict with 'ok' boolean and 'message' string confirming creation
    Raises HTTPException 400 if group already exists
    """
    data = load_models_json()
    if "groups" not in data:
        data["groups"] = {}
    
    if group_request.group in data["groups"]:
        raise HTTPException(status_code=400, detail=f"Group '{group_request.group}' already exists")
    
    data["groups"][group_request.group] = []
    save_models_json(data)
    return {"ok": True, "message": f"Group '{group_request.group}' created"}

@jsonmodels_router.put("/groups")
def update_group_name(update_request: UpdateModelGroupRequest, user=Depends(protected)):
    """
    Route: PUT /api/jsonmodels/groups
    Role: Renames an existing model group
    Input arguments:
      - update_request: UpdateModelGroupRequest with old_group and new_group strings
      - user: authenticated user via dependency
    Output format: Dict with 'ok' boolean and 'message' string confirming rename
    Raises HTTPException 404 if old group doesn't exist, 400 if new group already exists
    """
    data = load_models_json()
    
    if "groups" not in data:
        raise HTTPException(status_code=404, detail="No groups found")
    
    if update_request.old_group not in data["groups"]:
        raise HTTPException(status_code=404, detail=f"Group '{update_request.old_group}' does not exist")
    
    if update_request.new_group in data["groups"]:
        raise HTTPException(status_code=400, detail=f"Group '{update_request.new_group}' already exists")
    
    # Copy content and delete old group
    data["groups"][update_request.new_group] = data["groups"][update_request.old_group]
    del data["groups"][update_request.old_group]
    
    save_models_json(data)
    return {"ok": True, "message": f"Group renamed from '{update_request.old_group}' to '{update_request.new_group}'"}

@jsonmodels_router.delete("/groups")
def delete_group(group_request: ModelGroupRequest, user=Depends(protected)):
    """
    Route: DELETE /api/jsonmodels/groups
    Role: Deletes an existing model group and all its models
    Input arguments:
      - group_request: ModelGroupRequest with group name string
      - user: authenticated user via dependency
    Output format: Dict with 'ok' boolean and 'message' string confirming deletion
    Raises HTTPException 404 if group doesn't exist
    """
    data = load_models_json()
    
    if "groups" not in data:
        raise HTTPException(status_code=404, detail="No groups found")
    
    if group_request.group not in data["groups"]:
        raise HTTPException(status_code=404, detail=f"Group '{group_request.group}' does not exist")
    
    del data["groups"][group_request.group]
    save_models_json(data)
    return {"ok": True, "message": f"Group '{group_request.group}' deleted"}

@jsonmodels_router.get("/group/{group_name}", response_model=List[ModelEntry])
def get_group_models(group_name: str, user=Depends(protected)):
    """
    Route: GET /api/jsonmodels/group/{group_name}
    Role: Retrieves all models from a specific group
    Input arguments:
      - group_name: string path parameter specifying the group name
      - user: authenticated user via dependency
    Output format: List of ModelEntry objects containing model definitions
    Raises HTTPException 404 if group doesn't exist
    """
    data = load_models_json()
    
    if "groups" not in data:
        raise HTTPException(status_code=404, detail="No groups found")
    
    if group_name not in data["groups"]:
        raise HTTPException(status_code=404, detail=f"Group '{group_name}' does not exist")
    
    return data["groups"][group_name]

@jsonmodels_router.post("/entry")
def add_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """
    Route: POST /api/jsonmodels/entry
    Role: Adds a new model entry to a specified group
    Input arguments:
      - entry_request: ModelEntryRequest with group name and ModelEntry object
      - user: authenticated user via dependency
    Output format: Dict with 'ok' boolean and 'message' string confirming addition
    Raises HTTPException 400 if entry lacks URL/git, 409 if model already exists in group
    Note: Automatically normalizes destination paths and creates group if it doesn't exist
    """
    data = load_models_json()
    
    if "groups" not in data:
        data["groups"] = {}
    
    if entry_request.group not in data["groups"]:
        data["groups"][entry_request.group] = []
    
    # Check for presence of URL or git
    if not entry_request.entry.url and not entry_request.entry.git:
        raise HTTPException(status_code=400, detail="Entry must contain either a URL or a git repository")
    
    # Get BASE_DIR for path normalization
    base_dir = data.get("config", {}).get("BASE_DIR", "")
    
    # Normalize destination path if present
    if entry_request.entry.dest:
        entry_request.entry.dest = normalize_path(entry_request.entry.dest, base_dir)
    
    # Check if model already exists in group by destination
    if entry_request.entry.dest:
        for existing_entry in data["groups"][entry_request.group]:
            if existing_entry.get("dest") == entry_request.entry.dest:
                raise HTTPException(status_code=409, detail=f"A model with this destination already exists in group '{entry_request.group}'")
    
    # Add model to group
    data["groups"][entry_request.group].append(entry_request.entry.dict(exclude_none=True))
    save_models_json(data)
    
    return {"ok": True, "message": "Model entry added successfully"}

@jsonmodels_router.put("/entry")
def update_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """
    Route: PUT /api/jsonmodels/entry
    Role: Updates an existing model entry or creates it if not found
    Input arguments:
      - entry_request: ModelEntryRequest with group name and ModelEntry object
      - user: authenticated user via dependency
    Output format: Dict with 'ok' boolean and 'message' string confirming update/creation
    Raises HTTPException 400 if entry lacks dest/git for identification
    Note: Uses dest or git as identifier, automatically creates group if missing
    """
    data = load_models_json()
    
    # Ensure groups structure exists
    if "groups" not in data:
        data["groups"] = {}
    
    # Get BASE_DIR for path normalization
    base_dir = data.get("config", {}).get("BASE_DIR", "")
    
    # Normalize destination path if present
    if entry_request.entry.dest:
        entry_request.entry.dest = normalize_path(entry_request.entry.dest, base_dir)
    
    # Automatically create group if it doesn't exist
    if entry_request.group not in data["groups"]:
        logger.info(f"Auto-creating missing group: {entry_request.group}")
        data["groups"][entry_request.group] = []
    
    # Identifier for search
    model_id = entry_request.entry.dest or entry_request.entry.git
    if not model_id:
        raise HTTPException(status_code=400, detail="Entry must contain either a destination or git repository for identification")
    
    # Search for entry to update
    found = False
    for i, entry in enumerate(data["groups"][entry_request.group]):
        entry_id = entry.get("dest") or entry.get("git")
        if entry_id == model_id:
            data["groups"][entry_request.group][i] = entry_request.entry.dict(exclude_none=True)
            found = True
            break
    
    # If model doesn't exist, add it to the group
    if not found:
        logger.info(f"Model not found, auto-adding to group {entry_request.group}")
        data["groups"][entry_request.group].append(entry_request.entry.dict(exclude_none=True))
    
    save_models_json(data)
    message = "Model entry updated successfully" if found else "Model entry added successfully"
    return {"ok": True, "message": message}

@jsonmodels_router.delete("/entry")
def delete_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """
    Route: DELETE /api/jsonmodels/entry
    Role: Deletes an existing model entry from a specified group
    Input arguments:
      - entry_request: ModelEntryRequest with group name and ModelEntry object (only dest or git needed for identification)
      - user: authenticated user via dependency
    Output format: Dict with 'ok' boolean and 'message' string confirming deletion
    Raises HTTPException 404 if group or entry doesn't exist, 400 if entry lacks dest/git for identification
    Note: Uses dest or git as identifier to find the entry to delete
    """
    data = load_models_json()
    
    if "groups" not in data or entry_request.group not in data["groups"]:
        raise HTTPException(status_code=404, detail=f"Group '{entry_request.group}' does not exist")
    
    # Identifier for search
    model_id = entry_request.entry.dest or entry_request.entry.git
    if not model_id:
        raise HTTPException(status_code=400, detail="Entry must contain either a destination or git repository for identification")
    
    # Search for entry to delete
    original_length = len(data["groups"][entry_request.group])
    data["groups"][entry_request.group] = [
        entry for entry in data["groups"][entry_request.group] 
        if (entry.get("dest") or entry.get("git")) != model_id
    ]
    
    if len(data["groups"][entry_request.group]) == original_length:
        raise HTTPException(status_code=404, detail=f"Entry not found in group '{entry_request.group}'")
    
    save_models_json(data)
    return {"ok": True, "message": "Model entry deleted successfully"}
