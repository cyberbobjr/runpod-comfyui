import os
import json
import logging
import shutil
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Body, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union

from api import protected, get_env_file_path  # Import authentication utilities
from model_utils import DownloadManager, ModelManager

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Main router for all model-related routes
models_router = APIRouter(prefix="/api/models")

MODELS_JSON = "models.json"
WORKFLOW_DIR = None  # Sera récupéré dynamiquement
INSTALLED_BUNDLES_FILE = "installed_bundles.json"

# Data model classes
class TokenConfig(BaseModel):
    hf_token: Optional[str]
    civitai_token: Optional[str]

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

class ModelFilters(BaseModel):
    include_tags: List[str] = Field(default_factory=list)
    exclude_tags: List[str] = Field(default_factory=list)

class HardwareProfile(BaseModel):
    description: str
    model_filters: ModelFilters

class Bundle(BaseModel):
    description: str
    workflows: List[str]
    models: List[str]
    hardware_profiles: Dict[str, HardwareProfile] = Field(default_factory=dict)
    workflow_params: Optional[Dict[str, Any]] = None

class BundleRequest(BaseModel):
    name: str
    bundle: Bundle

class BundleInstallRequest(BaseModel):
    bundle: str
    profile: str

# Supprimer les fonctions dupliquées - utiliser directement ModelManager
def get_models_json_path():
    """Return the full path to models.json."""
    return ModelManager.get_models_json_path()

def load_models_json():
    """Load the complete models.json file."""
    return ModelManager.load_models_json()

def save_models_json(data):
    """Save the complete models.json file."""
    return ModelManager.save_models_json(data)

def get_models_base_dir():
    """Return the root directory for models."""
    return ModelManager.get_models_dir()

def get_workflows_dir():
    """Return the workflows directory."""
    return ModelManager.get_workflows_dir()

def get_installed_bundles_path():
    """Return the path to the installed bundles tracking file."""
    return ModelManager.get_installed_bundles_file()

def model_exists_on_disk(entry, base_dir):
    """Check if a model exists on disk."""
    return ModelManager.model_exists_on_disk(entry, base_dir)

def get_model_id(entry):
    """Generate a unique identifier for a model."""
    return entry.get("dest") or entry.get("git")

# Supprimer les fonctions read_env_file et write_env_file dupliquées
def read_env_file():
    """Read tokens from the .env file."""
    hf_token = None
    civitai_token = None
    env_path = ModelManager.get_env_file_path()
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("HF_TOKEN="):
                    hf_token = line.strip().split("=", 1)[1]
                elif line.startswith("CIVITAI_TOKEN="):
                    civitai_token = line.strip().split("=", 1)[1]
    return hf_token, civitai_token

def write_env_file(hf_token: Optional[str], civitai_token: Optional[str]):
    """Write tokens to the .env file."""
    lines = []
    if hf_token is not None:
        lines.append(f"HF_TOKEN={hf_token}")
    if civitai_token is not None:
        lines.append(f"CIVITAI_TOKEN={civitai_token}")
    env_path = ModelManager.get_env_file_path()
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

# ==== HTTP Routes ====# Point d'entrée principal - récupère toutes les données
@models_router.get("/", response_model=Dict[str, Any])
def get_models_data(user=Depends(protected)):
    """
    GET /api/models/
    
    Retrieves the complete models.json file including configuration, model groups, and bundles.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Dictionary containing:
      - config (Dict): Configuration settings including BASE_DIR
      - groups (Dict): Model groups with their entries
      - bundles (Dict): Available bundles
      - For each model entry, additional properties:
        - exists (bool): Whether the model file exists on disk
        - status (str, optional): Download status if in progress ("downloading", "completed", "failed")
        - progress (int, optional): Download progress percentage (0-100)
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading models.json file
    
    Usage: Main endpoint to get current state of all models and their download status.
    """
    data = load_models_json()
    base_dir = data.get("config", {}).get("BASE_DIR", "")
    # Add 'exists' and 'status' properties to each model
    groups = data.get("groups", {})
    # Get ongoing downloads
    downloads = DownloadManager.get_all_progress()
    for group_name, entries in groups.items():
        for entry in entries:
            entry["exists"] = model_exists_on_disk(entry, base_dir)
            model_id = entry.get("dest") or entry.get("git")
            if model_id in downloads:
                entry["status"] = downloads[model_id].get("status", "downloading")
                entry["progress"] = downloads[model_id].get("progress", 0)
            else:
                entry["status"] = None
                entry["progress"] = None
    return data

@models_router.post("/tokens")
def set_tokens(cfg: TokenConfig, user=Depends(protected)):
    """
    POST /api/models/tokens
    
    Sets API tokens (HuggingFace and CivitAI) in the .env file for authenticated downloads.
    
    Arguments:
    - cfg (TokenConfig): JSON object in request body with:
      - hf_token (str, optional): HuggingFace API token
      - civitai_token (str, optional): CivitAI API token
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true}
    
    Possible errors:
    - 401: Not authenticated
    - 400: Invalid request format
    - 500: Error writing to .env file
    
    Usage: Configure API tokens needed for downloading models from private repositories.
    """
    write_env_file(cfg.hf_token, cfg.civitai_token)
    return {"ok": True}

@models_router.get("/tokens")
def get_tokens(user=Depends(protected)):
    """
    GET /api/models/tokens
    
    Retrieves currently configured API tokens from the .env file.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Object containing:
      - hf_token (str or null): Current HuggingFace token
      - civitai_token (str or null): Current CivitAI token
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading .env file
    
    Usage: Check what API tokens are currently configured for downloads.
    """
    hf_token, civitai_token = read_env_file()
    return {"hf_token": hf_token, "civitai_token": civitai_token}

@models_router.get("/config", response_model=Dict[str, str])
def get_config(user=Depends(protected)):
    """
    GET /api/models/config
    
    Retrieves the configuration section from models.json.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Configuration dictionary containing:
      - BASE_DIR (str): Base directory path for models
      - Other configuration keys as defined in models.json
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading models.json file
    
    Usage: Get current configuration settings, primarily the base directory path.
    """
    data = load_models_json()
    return data.get("config", {})

@models_router.post("/config")
def update_config(config: ConfigUpdateRequest, user=Depends(protected)):
    """
    POST /api/models/config
    
    Updates the configuration in models.json, primarily the BASE_DIR setting.
    
    Arguments:
    - config (ConfigUpdateRequest): JSON object in request body with:
      - base_dir (str): New base directory path for models
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Configuration updated"}
    
    Possible errors:
    - 401: Not authenticated
    - 400: Invalid request format or missing base_dir
    - 500: Error writing to models.json file
    
    Usage: Change the base directory where models are stored.
    """
    data = load_models_json()
    data["config"] = {"BASE_DIR": config.base_dir}
    save_models_json(data)
    return {"ok": True, "message": "Configuration updated"}

@models_router.get("/groups", response_model=List[str])
def get_groups(user=Depends(protected)):
    """
    GET /api/models/groups
    
    Retrieves the list of all existing model groups.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Array of group names (strings)
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading models.json file
    
    Usage: Get all available model group names for organizing models.
    """
    data = load_models_json()
    return list(data.get("groups", {}).keys())

@models_router.post("/groups")
def create_group(group_request: ModelGroupRequest, user=Depends(protected)):
    """
    POST /api/models/groups
    
    Creates a new empty model group.
    
    Arguments:
    - group_request (ModelGroupRequest): JSON object in request body with:
      - group (str): Name of the new group to create
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Group 'name' created"}
    
    Possible errors:
    - 401: Not authenticated
    - 400: Group name already exists or invalid format
    - 500: Error writing to models.json file
    
    Usage: Create a new group to organize models by category.
    """
    data = load_models_json()
    if group_request.group in data.get("groups", {}):
        raise HTTPException(status_code=400, detail=f"Group '{group_request.group}' already exists")
    
    if "groups" not in data:
        data["groups"] = {}
    data["groups"][group_request.group] = []
    save_models_json(data)
    return {"ok": True, "message": f"Group '{group_request.group}' created"}

@models_router.put("/groups")
def update_group_name(update_request: UpdateModelGroupRequest, user=Depends(protected)):
    """
    PUT /api/models/groups
    
    Renames an existing model group and updates all bundle references.
    
    Arguments:
    - update_request (UpdateModelGroupRequest): JSON object in request body with:
      - old_group (str): Current name of the group
      - new_group (str): New name for the group
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Group renamed from 'old' to 'new'"}
    
    Possible errors:
    - 401: Not authenticated
    - 404: Old group name does not exist
    - 400: New group name already exists
    - 500: Error writing to models.json file
    
    Usage: Rename a model group while preserving all models and bundle references.
    """
    data = load_models_json()
    
    if update_request.old_group not in data.get("groups", {}):
        raise HTTPException(status_code=404, detail=f"Group '{update_request.old_group}' does not exist")
    
    if update_request.new_group in data.get("groups", {}):
        raise HTTPException(status_code=400, detail=f"Group '{update_request.new_group}' already exists")
    
    # Copy content and delete old group
    data["groups"][update_request.new_group] = data["groups"][update_request.old_group]
    del data["groups"][update_request.old_group]
    
    # Update references in bundles
    if "bundles" in data:
        for bundle_name, bundle in data["bundles"].items():
            if "models" in bundle and update_request.old_group in bundle["models"]:
                # Replace old group name with new one
                index = bundle["models"].index(update_request.old_group)
                bundle["models"][index] = update_request.new_group
    
    save_models_json(data)
    return {"ok": True, "message": f"Group renamed from '{update_request.old_group}' to '{update_request.new_group}'"}

@models_router.delete("/groups")
def delete_group(group_request: ModelGroupRequest, user=Depends(protected)):
    """
    DELETE /api/models/groups
    
    Deletes a model group if it's not referenced by any bundles.
    
    Arguments:
    - group_request (ModelGroupRequest): JSON object in request body with:
      - group (str): Name of the group to delete
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Group 'name' deleted"}
    
    Possible errors:
    - 401: Not authenticated
    - 404: Group does not exist
    - 400: Group is used in bundles (cannot delete)
    - 500: Error writing to models.json file
    
    Usage: Remove an empty or unused model group.
    """
    data = load_models_json()
    
    if group_request.group not in data.get("groups", {}):
        raise HTTPException(status_code=404, detail=f"Group '{group_request.group}' does not exist")
    
    # Check if group is used in bundles
    group_used_in_bundles = []
    if "bundles" in data:
        for bundle_name, bundle in data["bundles"].items():
            if "models" in bundle and group_request.group in bundle["models"]:
                group_used_in_bundles.append(bundle_name)
    
    if group_used_in_bundles:
        raise HTTPException(
            status_code=400, 
            detail=f"Group '{group_request.group}' is used in bundles: {', '.join(group_used_in_bundles)}"
        )
    
    del data["groups"][group_request.group]
    save_models_json(data)
    return {"ok": True, "message": f"Group '{group_request.group}' deleted"}

@models_router.get("/group/{group_name}", response_model=List[ModelEntry])
def get_group_models(group_name: str, user=Depends(protected)):
    """
    GET /api/models/group/{group_name}
    
    Retrieves all model entries for a specific group.
    
    Arguments:
    - group_name (str): Name of the group (in URL path)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Array of ModelEntry objects containing:
      - url (str, optional): Download URL
      - dest (str, optional): Destination path
      - git (str, optional): Git repository URL
      - type (str, optional): Model type
      - tags (List[str], optional): Model tags
      - src (str, optional): Source page URL
      - hash (str, optional): File hash
      - size (int, optional): File size in bytes
      - headers (Dict, optional): Custom headers for download
      - system_requirements (Dict, optional): System requirements
    
    Possible errors:
    - 401: Not authenticated
    - 404: Group does not exist
    - 500: Error reading models.json file
    
    Usage: Get all models in a specific group for display or processing.
    """
    data = load_models_json()
    
    if group_name not in data.get("groups", {}):
        raise HTTPException(status_code=404, detail=f"Group '{group_name}' does not exist")
    
    return data["groups"][group_name]

# Gestion des entrées de modèle
@models_router.post("/entry")
def add_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """
    POST /api/models/entry
    
    Adds a new model entry to a specific group.
    
    Arguments:
    - entry_request (ModelEntryRequest): JSON object in request body with:
      - group (str): Target group name
      - entry (ModelEntry): Model entry object with url/git and dest fields
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Model entry added successfully"}
    
    Possible errors:
    - 401: Not authenticated
    - 400: Missing URL/git, invalid destination, or duplicate model
    - 409: Model with same destination already exists
    - 500: Error writing to models.json file
    
    Usage: Add a new model to a group with download URL and destination path.
    """
    data = load_models_json()
    
    if "groups" not in data:
        data["groups"] = {}
    
    if entry_request.group not in data["groups"]:
        data["groups"][entry_request.group] = []
    
    # Check for URL or git presence
    if not entry_request.entry.url and not entry_request.entry.git:
        raise HTTPException(status_code=400, detail="Entry must contain either a URL or git repository")
    
    # Normalize path
    base_dir = data.get("config", {}).get("BASE_DIR", "")
    if entry_request.entry.dest:
        from api_json_models import normalize_path      
        entry_request.entry.dest = normalize_path(entry_request.entry.dest, base_dir)
    
    # Check if model already exists
    if entry_request.entry.dest:
        for existing_entry in data["groups"][entry_request.group]:
            if existing_entry.get("dest") == entry_request.entry.dest:
                raise HTTPException(status_code=409, detail=f"Model with this destination already exists")
    
    # Add model to group
    data["groups"][entry_request.group].append(entry_request.entry.dict(exclude_none=True))
    save_models_json(data)
    
    return {"ok": True, "message": "Model entry added successfully"}

@models_router.put("/entry")
def update_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """
    PUT /api/models/entry
    
    Updates an existing model entry or adds it if it doesn't exist.
    
    Arguments:
    - entry_request (ModelEntryRequest): JSON object in request body with:
      - group (str): Target group name
      - entry (ModelEntry): Model entry object to update/add
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Model entry updated" or "Model entry added"}
    
    Possible errors:
    - 401: Not authenticated
    - 400: Missing destination/git identifier
    - 500: Error writing to models.json file
    
    Usage: Update an existing model's properties or add a new one if not found.
    """
    data = load_models_json()
    
    # Ensure groups structure exists
    if "groups" not in data:
        data["groups"] = {}
    
    # Normalize path
    base_dir = data.get("config", {}).get("BASE_DIR", "")
    if entry_request.entry.dest:
        # Use ModelManager normalization function if available
        try:
            from api_json_models import normalize_path
            entry_request.entry.dest = normalize_path(entry_request.entry.dest, base_dir)
        except ImportError:
            # Simple fallback if function not available
            if not entry_request.entry.dest.startswith("${BASE_DIR}"):
                entry_request.entry.dest = f"${{BASE_DIR}}/{entry_request.entry.dest.lstrip('/')}"
    # Create group if it doesn't exist
    if entry_request.group not in data["groups"]:
        data["groups"][entry_request.group] = []
    
    # Identifier for search
    model_id = entry_request.entry.dest or entry_request.entry.git
    if not model_id:
        raise HTTPException(status_code=400, detail="Entry must have a destination or git repository")
    
    # Search for entry to update
    found = False
    for i, entry in enumerate(data["groups"][entry_request.group]):
        entry_id = entry.get("dest") or entry.get("git")
        if entry_id == model_id:
            data["groups"][entry_request.group][i] = entry_request.entry.dict(exclude_none=True)
            found = True
            break
    
    # If not found, add as new
    if not found:
        data["groups"][entry_request.group].append(entry_request.entry.dict(exclude_none=True))
    
    save_models_json(data)
    message = "Model entry updated" if found else "Model entry added"
    return {"ok": True, "message": message}

@models_router.delete("/entry")
def delete_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """
    DELETE /api/models/entry
    
    Removes a model entry from a group.
    
    Arguments:
    - entry_request (ModelEntryRequest): JSON object in request body with:
      - group (str): Group name containing the model
      - entry (ModelEntry): Entry to delete (must contain dest or git)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Model entry deleted successfully"}
    
    Possible errors:
    - 401: Not authenticated
    - 404: Group or model not found
    - 400: Cannot identify model to delete
    - 500: Error writing to models.json file
    
    Usage: Remove a model entry from the configuration.
    """
    data = load_models_json()
    
    if entry_request.group not in data.get("groups", {}):
        raise HTTPException(status_code=404, detail=f"Group '{entry_request.group}' does not exist")
    
    # Identifier for search
    model_id = entry_request.entry.dest or entry_request.entry.git
    if not model_id:
        raise HTTPException(status_code=400, detail="Cannot identify model to delete")
    
    # Search and delete
    original_length = len(data["groups"][entry_request.group])
    data["groups"][entry_request.group] = [
        entry for entry in data["groups"][entry_request.group] 
        if (entry.get("dest") or entry.get("git")) != model_id
    ]
    
    if len(data["groups"][entry_request.group]) == original_length:
        raise HTTPException(status_code=404, detail=f"Model not found in group '{entry_request.group}'")
    
    save_models_json(data)
    return {"ok": True, "message": "Model entry deleted successfully"}

@models_router.get("/downloads")
def get_all_downloads(user=Depends(protected)):
    """
    GET /api/models/downloads
    
    Returns the status of all ongoing model downloads.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Dictionary with model_id as keys and objects as values containing:
      - progress (int): Download progress percentage (0-100)
      - status (str): Download status ("downloading", "completed", "failed", etc.)
      - Additional download information
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error accessing download manager
    
    Usage: Monitor progress of all active downloads in real-time.
    """
    return DownloadManager.get_all_progress()

@models_router.post("/download")
async def download_model(
    request: Request,
    background_tasks: BackgroundTasks,
    user=Depends(protected)
):
    """
    POST /api/models/download
    
    Starts downloading one or more models in the background.
    
    Arguments:
    - request: HTTP request containing JSON body with:
      - Single model entry object, or
      - Array of model entry objects
      - Each entry must have 'url' or 'git', and 'dest'
    - background_tasks: FastAPI background tasks handler
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Single result object or array of result objects:
      - ok (bool): Whether download started successfully
      - msg (str, optional): Error message if ok is false
    
    Possible errors:
    - 401: Not authenticated
    - 400: Invalid input format, missing tokens, or invalid paths
    - 500: Error starting download
    
    Download process:
    1. Validates each model entry has required fields
    2. Checks for required API tokens (HuggingFace, CivitAI)
    3. Resolves destination paths using BASE_DIR
    4. Creates destination directories if needed
    5. Starts background download tasks
    6. Prevents duplicate downloads to same destination
    
    Usage: Initiate model downloads from URLs or git repositories.
    """
    data = await request.json()
    # Use BASE_DIR directly, not models subdirectory
    base_dir = ModelManager.get_base_dir()
    hf_token, civitai_token = read_env_file()
    is_single = False
    if isinstance(data, dict):
        entries = [data]
        is_single = True
    elif isinstance(data, list):
        entries = data
    else:
        return {"ok": False, "msg": "Invalid input format"}

    launched_dests = set()
    results = []
    for entry in entries:
        url = entry.get("url", "")
        dest = entry.get("dest")
        git_url = entry.get("git")
        model_id = get_model_id(entry)
        
        # Log the download request
        if url:
            logger.info(f"Download request - URL: {url}")
        elif git_url:
            logger.info(f"Download request - Git: {git_url}")
        
        # Token checks
        if "huggingface.co" in url and not hf_token:
            results.append({"ok": False, "msg": "HuggingFace token required for this download"})
            continue
        if "civitai.com" in url and not civitai_token:
            results.append({"ok": False, "msg": "CivitAI token required for this download"})
            continue

        # Use ModelManager to resolve the path properly
        if dest:
            path = ModelManager.resolve_path(dest, base_dir)
            if not path:
                results.append({"ok": False, "msg": "Invalid destination path"})
                continue
            
            # Log the resolved destination path
            logger.info(f"Destination path resolved: {path}")
            logger.info(f"Directory: {os.path.dirname(path)}")
            
            # Check if directory exists, create if not
            dest_dir = os.path.dirname(path)
            if not os.path.exists(dest_dir):
                logger.info(f"Creating destination directory: {dest_dir}")
                try:
                    os.makedirs(dest_dir, exist_ok=True)
                except Exception as e:
                    logger.error(f"Failed to create directory {dest_dir}: {e}")
                    results.append({"ok": False, "msg": f"Failed to create directory: {e}"})
                    continue
            else:
                logger.info(f"Destination directory exists: {dest_dir}")
        else:
            path = None

        # Only launch each download once per dest
        if path and path in launched_dests:
            logger.info(f"Download already in progress for: {path}")
            results.append({"ok": True, "msg": "Already downloading"})
            continue
        if path:
            launched_dests.add(path)

        try:
            logger.info(f"Starting download - Model ID: {model_id}")
            logger.info(f"Final destination: {path}")
            DownloadManager.download_model(entry, base_dir, hf_token, civitai_token, background=True)
            results.append({"ok": True})
            logger.info(f"Download initiated successfully for: {model_id}")
        except Exception as e:
            logger.error(f"Failed to start download for {model_id}: {e}")
            results.append({"ok": False, "msg": str(e)})
    # Always return a response
    return results[0] if is_single else results

@models_router.post("/progress")
def get_progress(entry: dict = Body(...), user=Depends(protected)):
    """
    POST /api/models/progress
    
    Returns the download progress for a specific model.
    
    Arguments:
    - entry (dict): JSON object in request body with:
      - dest (str) or git (str): Model identifier
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Progress object containing:
      - progress (int): Download progress percentage (0-100)
      - status (str): Current download status
      - Additional progress information
    
    Possible errors:
    - 401: Not authenticated
    - 400: Cannot identify model from entry
    - 404: No download found for this model
    
    Usage: Check download progress for a specific model.
    """
    model_id = get_model_id(entry)
    return DownloadManager.get_progress(model_id)

@models_router.post("/stop_download")
def stop_download(entry: dict, user=Depends(protected)):
    """
    POST /api/models/stop_download
    
    Stops an ongoing model download.
    
    Arguments:
    - entry (dict): JSON object in request body with:
      - dest (str) or git (str): Model identifier
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Result object:
      - ok (bool): Whether stop was successful
      - msg (str): Status message
    
    Possible errors:
    - 401: Not authenticated
    - 400: Cannot identify model from entry
    
    Usage: Cancel an active model download.
    """
    model_id = get_model_id(entry)
    stopped = DownloadManager.stop_download(model_id)
    if stopped:
        return {"ok": True, "msg": "Stop requested"}
    return {"ok": False, "msg": "No active download for this model"}

@models_router.post("/delete")
async def delete_models(
    request: Request,
    user=Depends(protected)
):
    """
    POST /api/models/delete
    
    Deletes one or more model files from disk.
    
    Arguments:
    - request: HTTP request containing JSON body with:
      - Single model object with 'dest' field, or
      - Array of model objects each with 'dest' field
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Single result object or array of result objects:
      - ok (bool): Whether deletion was successful
      - msg (str, optional): Error message if ok is false
    
    Possible errors:
    - 401: Not authenticated
    - 400: Invalid input format or missing destination
    - 500: Error deleting files
    
    Deletion process:
    1. Resolves destination paths using ModelManager
    2. Prevents duplicate deletions of same file
    3. Checks file existence before deletion
    4. Removes files from disk
    
    Usage: Remove downloaded model files to free up disk space.
    """
    data = await request.json()
    # Accept both a single object or a list
    is_single = False
    if isinstance(data, dict):
        entries = [data]
        is_single = True
    elif isinstance(data, list):
        entries = data
    else:
        return {"ok": False, "msg": "Invalid input format"}

    # Track which dest have already been deleted
    deleted_dests = set()
    results = []
    for entry in entries:
        dest = entry.get("dest")
        if not dest:
            results.append({"ok": False, "msg": "No destination path provided"})
            continue

        # Use ModelManager to resolve the path properly
        path = ModelManager.resolve_path(dest)
        if not path:
            results.append({"ok": False, "msg": "Invalid destination path"})
            continue

        # Only attempt to delete each file once
        if path in deleted_dests:
            results.append({"ok": True, "msg": "Already deleted"})
            continue
        deleted_dests.add(path)

        if os.path.exists(path):
            try:
                os.remove(path)
                results.append({"ok": True})
            except Exception as e:
                results.append({"ok": False, "msg": f"Error deleting file: {e}"})
        else:
            results.append({"ok": False, "msg": f"File not found: {path}"})
    # Return a single object if input was a single object
    return results[0] if is_single else results

# Exporter le router
# Cette variable sera importée dans le fichier main.py
