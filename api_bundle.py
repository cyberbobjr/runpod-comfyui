import os
import json
import logging
import uuid
import jsonschema
import zipfile
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Body, File, UploadFile, Query
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from fastapi.responses import JSONResponse, FileResponse
import shutil
from auth import protected
from model_utils import ModelManager, DownloadManager

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for data validation
class ModelDefinition(BaseModel):
    url: str
    dest: str
    git: str = ""
    type: str
    tags: List[str] = Field(default_factory=list)
    src: str = ""
    hash: str = ""
    size: Optional[int] = None

class HardwareProfile(BaseModel):
    description: str
    models: List[ModelDefinition] = Field(default_factory=list)

class Bundle(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    version: str = "1.0.0"
    author: Optional[str] = None
    website: Optional[str] = None
    workflows: List[str] = Field(default_factory=list)
    hardware_profiles: Dict[str, HardwareProfile] = Field(default_factory=dict)
    workflow_params: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str

class BundleCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    version: str = "1.0.0"
    author: Optional[str] = None
    website: Optional[str] = None
    workflows: List[str] = Field(default_factory=list)
    hardware_profiles: Dict[str, HardwareProfile] = Field(default_factory=dict)
    workflow_params: Optional[Dict[str, Any]] = None

class BundleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    website: Optional[str] = None
    workflows: Optional[List[str]] = None
    hardware_profiles: Optional[Dict[str, HardwareProfile]] = None
    workflow_params: Optional[Dict[str, Any]] = None

class BundleInstallRequest(BaseModel):
    bundle_id: str
    profile: str

class BundleInstallResponse(BaseModel):
    ok: bool
    message: str
    results: Optional[Dict[str, List[str]]] = None

# JSON schema for bundle validation
BUNDLE_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "version", "created_at", "updated_at"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
        "author": {"type": ["string", "null"]},
        "website": {"type": ["string", "null"]},
        "workflows": {"type": "array", "items": {"type": "string"}},
        "hardware_profiles": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["description"],
                "properties": {
                    "description": {"type": "string"},
                    "models": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["url", "dest", "type"],
                            "properties": {
                                "url": {"type": "string"},
                                "dest": {"type": "string"},
                                "git": {"type": "string"},
                                "type": {"type": "string"},
                                "tags": {"type": "array", "items": {"type": "string"}},
                                "src": {"type": "string"},
                                "hash": {"type": "string"},
                                "size": {"type": ["integer", "null"]}
                            }
                        }
                    }
                }
            }
        },
        "workflow_params": {"type": ["object", "null"]},
        "created_at": {"type": "string"},
        "updated_at": {"type": "string"}
    }
}

# Create router for bundle API routes
bundle_router = APIRouter(prefix="/api/bundles")

def get_bundle_path(bundle_id: str):
    """Returns the full path to a specific bundle file."""
    bundles_dir = ModelManager.get_bundles_dir()
    return os.path.join(bundles_dir, f"{bundle_id}.zip")

def load_bundle(bundle_id: str):
    """Loads a specific bundle from the file system (ZIP format)."""
    bundle_path = get_bundle_path(bundle_id)
    
    if not os.path.exists(bundle_path):
        raise HTTPException(status_code=404, detail=f"Bundle with ID {bundle_id} not found")
    
    try:
        with zipfile.ZipFile(bundle_path, 'r') as zipf:
            # Read bundle JSON from ZIP
            json_filename = f"{bundle_id}.json"
            if json_filename not in zipf.namelist():
                raise HTTPException(status_code=400, detail=f"Bundle JSON file not found in ZIP")
            
            with zipf.open(json_filename) as f:
                data = json.load(f)
        
        # Validate JSON schema
        try:
            jsonschema.validate(instance=data, schema=BUNDLE_SCHEMA)
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Bundle validation error {bundle_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid bundle format: {str(e)}")
        
        return data
    except zipfile.BadZipFile:
        logger.error(f"Invalid ZIP file: {bundle_path}")
        raise HTTPException(status_code=400, detail=f"Invalid ZIP file format")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for {bundle_path}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"JSON decode error: {str(e)}")
    except Exception as e:
        logger.error(f"Error reading bundle {bundle_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reading bundle: {str(e)}")

def save_bundle(bundle_data):
    """Saves a bundle to the file system as a ZIP archive containing the JSON and workflow files."""
    bundle_id = bundle_data.get("id")
    if not bundle_id:
        raise ValueError("Bundle without ID cannot be saved")
    
    bundle_path = get_bundle_path(bundle_id).replace('.json', '.zip')
    
    try:
        # Ensure the bundles directory exists
        bundles_dir = os.path.dirname(bundle_path)
        os.makedirs(bundles_dir, exist_ok=True)
        
        # Validate JSON schema before saving
        jsonschema.validate(instance=bundle_data, schema=BUNDLE_SCHEMA)
        
        # Create ZIP file
        with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add bundle JSON to ZIP
            bundle_json = json.dumps(bundle_data, indent=2)
            zipf.writestr(f"{bundle_id}.json", bundle_json)
            
            # Add workflow files to ZIP
            workflows_dir = ModelManager.get_workflows_dir()
            for workflow in bundle_data.get("workflows", []):
                workflow_path = os.path.join(workflows_dir, workflow)
                if os.path.exists(workflow_path):
                    zipf.write(workflow_path, f"workflows/{workflow}")
                    logger.info(f"Added workflow {workflow} to bundle ZIP")
                else:
                    logger.warning(f"Workflow file {workflow} not found, skipping")
        
        logger.info(f"Bundle {bundle_id} saved successfully to {bundle_path}")
        return bundle_data
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Bundle validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid bundle format: {str(e)}")
    except Exception as e:
        logger.error(f"Error saving bundle {bundle_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving bundle: {str(e)}")

def list_bundles():
    """Lists all available bundles."""
    bundles_dir = ModelManager.get_bundles_dir()
    if not os.path.exists(bundles_dir):
        return []
    
    bundles = []
    installed_bundles_file = ModelManager.get_installed_bundles_file()
    for filename in os.listdir(bundles_dir):
        if filename.endswith(".zip") and filename != os.path.basename(installed_bundles_file):
            try:
                bundle_path = os.path.join(bundles_dir, filename)
                bundle_id = filename.replace('.zip', '')
                
                with zipfile.ZipFile(bundle_path, 'r') as zipf:
                    json_filename = f"{bundle_id}.json"
                    if json_filename in zipf.namelist():
                        with zipf.open(json_filename) as f:
                            bundle_data = json.load(f)
                        # Quick validation that it's actually a bundle
                        if "id" in bundle_data and "name" in bundle_data:
                            bundles.append(bundle_data)
            except Exception as e:
                logger.warning(f"Error loading bundle {filename}: {str(e)}")
    
    return bundles

def get_installed_bundles_path():
    """Returns the path to the installed bundles tracking file."""
    return ModelManager.get_installed_bundles_file()

def load_installed_bundles():
    """Loads the list of installed bundles."""
    path = get_installed_bundles_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_installed_bundles(bundles):
    """Saves the list of installed bundles."""
    path = get_installed_bundles_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bundles, f, indent=2)

@bundle_router.get("/", response_model=List[Bundle])
def get_bundles(installed_only: bool = Query(False), user=Depends(protected)):
    """
    GET /api/bundles/
    
    Retrieves the list of all available bundles in the system.
    
    Arguments:
    - installed_only (bool, optional): If True, returns only installed bundles
      - Default: False (returns all bundles)
      - Usage: ?installed_only=true
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: List of Bundle objects with:
      - id (str): Unique bundle identifier
      - name (str): Bundle name
      - description (str): Bundle description
      - version (str): Bundle version
      - workflows (List[str]): List of associated workflow names
      - hardware_profiles (Dict): Hardware profiles with direct model definitions
      - workflow_params (Dict, optional): Workflow parameters
      - created_at (str): Creation date/time (ISO format)
      - updated_at (str): Last modification date/time (ISO format)
    
    Possible errors:
    - 401: Not authenticated
    - 500: Server error while reading files
    """
    bundles = list_bundles()
    
    if installed_only:
        installed = {b["bundle_id"] for b in load_installed_bundles()}
        bundles = [b for b in bundles if b["id"] in installed]
    
    return bundles

@bundle_router.get("/{bundle_id}", response_model=Bundle)
def get_bundle(bundle_id: str, user=Depends(protected)):
    """
    GET /api/bundles/{bundle_id}
    
    Retrieves the complete details of a specific bundle.
    
    Arguments:
    - bundle_id (str): Unique bundle identifier (UUID in URL)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Complete Bundle object with all details
    
    Possible errors:
    - 401: Not authenticated
    - 404: Bundle not found
    - 400: Invalid JSON format in bundle file
    - 500: Server error while reading
    """
    return load_bundle(bundle_id)

@bundle_router.post("/", response_model=Bundle)
def create_bundle(bundle: BundleCreate, user=Depends(protected)):
    """
    POST /api/bundles/
    
    Creates a new bundle in the system.
    
    Arguments:
    - bundle (BundleCreate): Bundle data to create in JSON body:
      - name (str): Bundle name (required)
      - description (str): Bundle description (optional)
      - version (str): Bundle version in x.y.z format (default: "1.0.0")
      - author (str, optional): Bundle author
      - website (str, optional): Bundle website/repository URL
      - workflows (List[str]): Workflow list (default: [])
      - hardware_profiles (Dict): Hardware profiles with direct model definitions (default: {})
      - workflow_params (Dict, optional): Workflow parameters
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Created bundle with:
      - id (str): New automatically generated UUID
      - created_at (str): Creation timestamp
      - updated_at (str): Creation timestamp (same as created_at)
      - All other provided fields
    
    Possible errors:
    - 401: Not authenticated
    - 400: Invalid data or incorrect format (including invalid version format)
    - 500: Error during saving
    
    Note: Referenced workflows are checked but their absence only generates 
    a warning (not a blocking error). Version must follow x.y.z format.
    """
    # Generate new ID
    bundle_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    # Create complete bundle
    bundle_data = bundle.dict()
    bundle_data.update({
        "id": bundle_id,
        "created_at": timestamp,
        "updated_at": timestamp
    })
    
    # Validate that referenced workflows exist
    workflows_dir = ModelManager.get_workflows_dir()
    for workflow in bundle_data["workflows"]:
        workflow_path = os.path.join(workflows_dir, workflow)
        if not os.path.exists(workflow_path):
            logger.warning(f"Workflow '{workflow}' referenced in bundle does not exist")
            # This is a warning, not a blocking error
    
    # Save bundle
    return save_bundle(bundle_data)

@bundle_router.put("/{bundle_id}", response_model=Bundle)
def update_bundle(bundle_id: str, bundle_update: BundleUpdate, user=Depends(protected)):
    """
    PUT /api/bundles/{bundle_id}
    
    Updates an existing bundle. Only provided fields are modified.
    
    Arguments:
    - bundle_id (str): Unique bundle identifier to modify (UUID in URL)
    - bundle_update (BundleUpdate): Fields to modify in JSON body:
      - name (str, optional): New name
      - description (str, optional): New description
      - version (str, optional): New version in x.y.z format
      - author (str, optional): New author
      - website (str, optional): New website/repository URL
      - workflows (List[str], optional): New workflow list
      - hardware_profiles (Dict, optional): New hardware profiles with direct model definitions
      - workflow_params (Dict, optional): New workflow parameters
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Updated bundle with:
      - updated_at: New modification timestamp
      - Modified fields with new values
      - Unmodified fields preserved
      - id and created_at unchanged
    
    Possible errors:
    - 401: Not authenticated
    - 404: Bundle not found
    - 400: Invalid data or incorrect format (including invalid version format)
    - 500: Error during saving
    """
    # Load existing bundle for validation
    existing_bundle = load_bundle(bundle_id)
    
    # Merge existing data with updates (only non-None values)
    bundle_data = existing_bundle.copy()
    update_data = {k: v for k, v in bundle_update.dict().items() if v is not None}
    bundle_data.update(update_data)
    bundle_data.update({
        "id": bundle_id,  # preserve existing ID
        "created_at": existing_bundle["created_at"],  # preserve creation date
        "updated_at": datetime.utcnow().isoformat()  # update modification date
    })
    
    # Save bundle
    return save_bundle(bundle_data)

@bundle_router.delete("/{bundle_id}")
def delete_bundle(bundle_id: str, user=Depends(protected)):
    """
    DELETE /api/bundles/{bundle_id}
    
    Permanently deletes a bundle from the system.
    
    Arguments:
    - bundle_id (str): Unique bundle identifier to delete (UUID in URL)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Confirmation object:
      - ok (bool): True if deletion succeeded
      - message (str): Confirmation message
    
    Possible errors:
    - 401: Not authenticated
    - 404: Bundle not found
    - 400: Bundle is installed (must be uninstalled before deletion)
    - 500: Error during file deletion
    
    Note: An installed bundle cannot be deleted. It must first be 
    uninstalled via the /uninstall endpoint.
    """
    bundle_path = get_bundle_path(bundle_id)
    
    if not os.path.exists(bundle_path):
        raise HTTPException(status_code=404, detail=f"Bundle with ID {bundle_id} not found")
    
    # Check if bundle is installed
    installed_bundles = load_installed_bundles()
    if any(b["bundle_id"] == bundle_id for b in installed_bundles):
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete bundle {bundle_id} because it is installed. Uninstall it first."
        )
    
    try:
        os.remove(bundle_path)
        return {"ok": True, "message": f"Bundle {bundle_id} successfully deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting bundle: {str(e)}")

@bundle_router.post("/upload")
async def upload_bundle(
    bundle_file: UploadFile = File(...),
    user=Depends(protected)
):
    """
    POST /api/bundles/upload
    
    Imports a bundle from an uploaded ZIP file containing bundle JSON and workflow files.
    
    Arguments:
    - bundle_file (UploadFile): ZIP file containing bundle data and workflows
      - Content type: multipart/form-data
      - Required extension: .zip
      - Format: ZIP containing bundle JSON and workflow files in workflows/ folder
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Confirmation object:
      - ok (bool): True if import succeeded
      - message (str): Confirmation message with bundle name and ID
    
    Possible errors:
    - 401: Not authenticated
    - 400: File is not ZIP, incorrect extension, or invalid format
    - 409: Bundle with same ID already exists
    - 500: Error during saving
    """
    if not bundle_file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="File must be in ZIP format")
    
    try:
        # Read file content
        content = await bundle_file.read()
        
        # Extract to temporary location to validate
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            with zipfile.ZipFile(temp_path, 'r') as zipf:
                # Find bundle JSON file
                json_files = [f for f in zipf.namelist() if f.endswith('.json') and not f.startswith('workflows/')]
                if not json_files:
                    raise HTTPException(status_code=400, detail="No bundle JSON file found in ZIP")
                
                # Read bundle data
                with zipf.open(json_files[0]) as f:
                    bundle_data = json.load(f)
                
                # Validate schema
                try:
                    jsonschema.validate(instance=bundle_data, schema=BUNDLE_SCHEMA)
                except jsonschema.exceptions.ValidationError as e:
                    raise HTTPException(status_code=400, detail=f"Invalid bundle format: {str(e)}")
                
                # Check if bundle with same ID already exists
                bundle_id = bundle_data.get("id")
                if os.path.exists(get_bundle_path(bundle_id)):
                    raise HTTPException(status_code=409, detail=f"Bundle with ID {bundle_id} already exists")
                
                # Extract workflows to workflows directory
                workflows_dir = ModelManager.get_workflows_dir()
                os.makedirs(workflows_dir, exist_ok=True)
                
                for file_info in zipf.infolist():
                    if file_info.filename.startswith('workflows/') and file_info.filename.endswith('.json'):
                        workflow_name = os.path.basename(file_info.filename)
                        workflow_path = os.path.join(workflows_dir, workflow_name)
                        
                        with zipf.open(file_info) as source, open(workflow_path, 'wb') as target:
                            target.write(source.read())
                        logger.info(f"Extracted workflow: {workflow_name}")
                
                # Save bundle (this will create the ZIP with JSON and workflows)
                save_bundle(bundle_data)
                
                return {"ok": True, "message": f"Bundle {bundle_data['name']} (ID: {bundle_id}) imported successfully"}
        finally:
            os.unlink(temp_path)
            
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="File is not a valid ZIP archive")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Bundle JSON file is not valid")
    except Exception as e:
        logger.error(f"Error importing bundle: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error importing bundle: {str(e)}")

@bundle_router.get("/export/{bundle_id}")
def export_bundle(bundle_id: str, user=Depends(protected)):
    """
    GET /api/bundles/export/{bundle_id}
    
    Exports a bundle as a downloadable ZIP file containing JSON and workflow files.
    
    Arguments:
    - bundle_id (str): Unique bundle identifier to export (UUID in URL)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Content-Type: application/zip
    - Content-Disposition: attachment with generated filename
    - Body: ZIP file containing bundle JSON and workflow files
    
    Filename format:
    - bundle_{bundle_name}_{bundle_id}.zip
    - Spaces in name are replaced by underscores
    """
    bundle_data = load_bundle(bundle_id)
    bundle_path = get_bundle_path(bundle_id)
    
    return FileResponse(
        bundle_path,
        media_type="application/zip",
        filename=f"bundle_{bundle_data['name'].replace(' ', '_')}_{bundle_id}.zip"
    )

@bundle_router.post("/install", response_model=BundleInstallResponse)
def install_bundle(request: BundleInstallRequest, user=Depends(protected)):
    """
    POST /api/bundles/install
    
    Installs a bundle with a specific hardware profile. Downloads and configures
    all necessary models and workflows defined in the profile.
    """
    # Load bundle
    bundle_data = load_bundle(request.bundle_id)
    
    # Check that profile exists in bundle
    if "hardware_profiles" not in bundle_data or request.profile not in bundle_data["hardware_profiles"]:
        raise HTTPException(status_code=404, detail=f"Hardware profile '{request.profile}' not found in bundle")
    
    # Install models and workflows
    try:
        profile_data = bundle_data["hardware_profiles"][request.profile]
        models_to_install = profile_data.get("models", [])
        
        # Install models using DownloadManager (en arrière-plan)
        base_dir = ModelManager.get_base_dir()
        
        # Read tokens for authenticated downloads
        from api_models import read_env_file
        hf_token, civitai_token = read_env_file()
        
        install_results = {
            "installed": [],
            "already_exists": [],
            "errors": []
        }
        
        # Process each model in the profile (start downloads in background)
        for model in models_to_install:
            model_id = model.get("dest") or model.get("git", "unknown")
            
            # Check if model already exists
            if ModelManager.model_exists_on_disk(model, base_dir):
                logger.info(f"Model already exists: {model_id}")
                install_results["already_exists"].append(model_id)
                continue
            
            try:
                # Start download using DownloadManager (background=True pour installation async)
                DownloadManager.download_model(
                    model, 
                    base_dir, 
                    hf_token, 
                    civitai_token, 
                    background=True  # Installation asynchrone
                )
                install_results["installed"].append(model_id)
                logger.info(f"Model download started: {model_id}")
            except Exception as e:
                error_msg = f"Error starting download for model {model_id}: {str(e)}"
                install_results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # Install workflows immediately (synchrone car rapide)
        for workflow in bundle_data.get("workflows", []):
            try:
                success, message = ModelManager.copy_workflow_to_comfyui(workflow)
                if success:
                    install_results["installed"].append(f"workflow: {workflow}")
                    logger.info(f"Workflow installed successfully: {workflow}")
                else:
                    install_results["errors"].append(f"workflow: {workflow} - {message}")
                    logger.error(f"Failed to install workflow {workflow}: {message}")
            except Exception as e:
                error_msg = f"Error installing workflow {workflow}: {str(e)}"
                install_results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # Register installation in installed bundles list immediately
        # (les téléchargements continuent en arrière-plan)
        bundles = load_installed_bundles()
        # Avoid duplicates
        if not any(b["bundle_id"] == request.bundle_id and b["profile"] == request.profile for b in bundles):
            bundles.append({
                "bundle_id": request.bundle_id,
                "profile": request.profile,
                "installed_at": datetime.utcnow().isoformat()
            })
            save_installed_bundles(bundles)
        
        # Prepare result message
        num_started = len([x for x in install_results["installed"] if not x.startswith("workflow:")])
        num_workflows = len([x for x in install_results["installed"] if x.startswith("workflow:")])
        num_exists = len(install_results["already_exists"])
        num_errors = len(install_results["errors"])
        
        message = f"Bundle '{bundle_data['name']}' with profile '{request.profile}' installation started. "
        message += f"{num_started} model download(s) started, {num_workflows} workflow(s) installed, "
        message += f"{num_exists} already present, {num_errors} error(s)."
        
        return {
            "ok": num_errors == 0,
            "message": message,
            "results": install_results
        }
    except Exception as e:
        logger.error(f"Error installing bundle: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error installing bundle: {str(e)}")

@bundle_router.post("/uninstall")
def uninstall_bundle(request: BundleInstallRequest, user=Depends(protected)):
    """
    POST /api/bundles/uninstall
    
    Uninstalls a bundle with specific profile. Only removes files
    that are not used by other installed bundles.
    """
    bundle_data = load_bundle(request.bundle_id)
    
    # Check that installation exists
    bundles = load_installed_bundles()
    if not any(b["bundle_id"] == request.bundle_id and b["profile"] == request.profile for b in bundles):
        raise HTTPException(status_code=404, detail=f"Bundle with specified profile is not installed")
    
    base_dir = ModelManager.get_base_dir()
    
    # Identify all installed bundles and their models and workflows
    used_models = set()
    used_workflows = set()
    
    # For each installed bundle (except the one we're uninstalling)
    for installed_bundle in bundles:
        if installed_bundle["bundle_id"] == request.bundle_id and installed_bundle["profile"] == request.profile:
            continue  # Skip the bundle we're uninstalling
            
        try:
            # Load bundle data
            bundle_info = load_bundle(installed_bundle["bundle_id"])
            profile_name = installed_bundle["profile"]
            
            # If profile doesn't exist in this bundle, continue
            if profile_name not in bundle_info.get("hardware_profiles", {}):
                continue
                
            # Get models for this bundle+profile
            profile_data = bundle_info["hardware_profiles"][profile_name]
            models = profile_data.get("models", [])
            
            # Add models to used models list
            for model in models:
                if model.get("dest"):
                    used_models.add(model["dest"])
            
            # Add workflows used by this bundle
            for wf in bundle_info.get("workflows", []):
                used_workflows.add(wf)
                
        except Exception as e:
            logger.warning(f"Error analyzing installed bundle {installed_bundle['bundle_id']}: {str(e)}")
    
    # Identify models and workflows from bundle to uninstall that are not used elsewhere
    unused_models = []
    unused_workflows = []
    
    # Get models from bundle to uninstall
    profile_data = bundle_data["hardware_profiles"][request.profile]
    models = profile_data.get("models", [])
    
    # Check which models are not used elsewhere
    for model in models:
        dest = model.get("dest")
        if dest and dest not in used_models:
            unused_models.append(model)
    
    # Check which workflows are not used elsewhere
    for wf in bundle_data.get("workflows", []):
        if wf not in used_workflows:
            unused_workflows.append(wf)
    
    # Now delete unused files
    deleted_models = []
    deleted_workflows = []
    errors = []
    
    # Delete unused models
    for model in unused_models:
        dest = model.get("dest")
        if dest:
            # Resolve real path
            file_path = ModelManager.resolve_path(dest, base_dir)
            if os.path.exists(file_path):
                try:
                    # If it's a directory (like for git repos), delete recursively
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
                    deleted_models.append(dest)
                    logger.info(f"Model deleted: {file_path}")
                except Exception as e:
                    errors.append(f"Error deleting model {dest}: {str(e)}")
                    logger.error(f"Error deleting model {file_path}: {str(e)}")
    
    # Delete unused workflows
    workflows_dir = ModelManager.get_workflows_dir()
    comfy_workflows_dir = os.path.join(base_dir, "ComfyUI", "workflows")
    
    for wf in unused_workflows:
        wf_path = os.path.join(workflows_dir, wf)
        comfy_wf_path = os.path.join(comfy_workflows_dir, wf)
        
        for path in [wf_path, comfy_wf_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    if wf not in deleted_workflows:  # Éviter les doublons
                        deleted_workflows.append(wf)
                    logger.info(f"Workflow deleted: {path}")
                except Exception as e:
                    errors.append(f"Error deleting workflow {wf}: {str(e)}")
                    logger.error(f"Error deleting workflow {path}: {str(e)}")
    
    # Update installed bundles list
    bundles = [b for b in bundles if not (b["bundle_id"] == request.bundle_id and b["profile"] == request.profile)]
    save_installed_bundles(bundles)
    
    # Prepare result message
    message = f"Bundle '{bundle_data['name']}' with profile '{request.profile}' uninstalled successfully. "
    message += f"{len(deleted_models)} model(s) and {len(deleted_workflows)} workflow(s) deleted."
    if errors:
        message += f" {len(errors)} error(s) encountered."
    
    return {
        "ok": len(errors) == 0,
        "message": message,
        "deleted_models": deleted_models,
        "deleted_workflows": deleted_workflows,
        "errors": errors
    }

@bundle_router.get("/installed/", response_model=List[Dict[str, Any]])
def get_installed_bundles_info(user=Depends(protected)):
    """
    GET /api/bundles/installed/
    
    Retrieves detailed information about all currently installed bundles.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: List of objects with installation information:
      - id (str): UUID of installed bundle
      - name (str): Bundle name (or "Unknown bundle" if not found)
      - profile (str): Hardware profile name used during installation
      - installed_at (str): Installation date/time (ISO format)
      - version (str): Bundle version (or "unknown" if not found)
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading files
    
    Note: If an installed bundle can no longer be read (corrupted/deleted file),
    it still appears in the list with minimal information and 
    name="Unknown bundle", version="unknown".
    
    Usage: Allows viewing current installation state to manage 
    dependencies and plan uninstallations.
    """
    installed = load_installed_bundles()
    result = []
    
    for install_info in installed:
        try:
            bundle_data = load_bundle(install_info["bundle_id"])
            result.append({
                "id": install_info["bundle_id"],
                "name": bundle_data["name"],
                "profile": install_info["profile"],
                "installed_at": install_info.get("installed_at", ""),
                "version": bundle_data["version"]
            })
        except Exception as e:
            logger.warning(f"Error loading installed bundle {install_info['bundle_id']}: {str(e)}")
            # Still add entry with minimal information
            result.append({
                "id": install_info["bundle_id"],
                "name": "Unknown bundle",
                "profile": install_info["profile"],
                "installed_at": install_info.get("installed_at", ""),
                "version": "unknown"
            })
    
    return result

@bundle_router.post("/duplicate/{bundle_id}")
def duplicate_bundle(bundle_id: str, user=Depends(protected)):
    """
    POST /api/bundles/duplicate/{bundle_id}
    
    Creates a complete copy of an existing bundle with a new unique identifier.
    
    Arguments:
    - bundle_id (str): UUID of bundle to duplicate (in URL)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Confirmation object:
      - ok (bool): True if duplication succeeded
      - message (str): Confirmation message
      - id (str): UUID of newly created bundle
      - name (str): Name of new bundle (original name + " (copy)")
    
    Possible errors:
    - 401: Non authentifié
    - 404: Source bundle not found
    - 400: Invalid JSON format in source bundle
    - 500: Error saving new bundle
    
    Duplication process:
    1. Load complete source bundle
    2. Generate new UUID for copy
    3. Update timestamps (created_at and updated_at)
    4. Modify name by adding " (copy)"
    5. Save new bundle
    6. Return created bundle information
    
    Usage: Allows creating variants of existing bundles or
    making backups before important modifications.
    """
    original_bundle = load_bundle(bundle_id)
    
    # Créer une copie avec un nouvel ID
    new_bundle = dict(original_bundle)
    new_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    new_bundle.update({
        "id": new_id,
        "name": f"{original_bundle['name']} (copy)",
        "created_at": timestamp,
        "updated_at": timestamp
    })
    
    # Sauvegarder le nouveau bundle
    save_bundle(new_bundle)
    
    return {
        "ok": True,
        "message": f"Bundle successfully duplicated",
        "id": new_id,
        "name": new_bundle["name"]
    }
