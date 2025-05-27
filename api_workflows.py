import os
import json
import logging
import shutil
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from typing import List
from auth import protected
from model_utils import ModelManager

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router for workflow API routes
workflows_router = APIRouter(prefix="/api/workflows")

def get_workflows_dir():
    """Return the workflows directory."""
    return ModelManager.get_workflows_dir()

@workflows_router.get("/", response_model=List[str])
def list_workflows(user=Depends(protected)):
    """
    GET /api/workflows/
    
    Lists all available workflow files in the workflows directory.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Array of workflow filenames (strings ending in .json)
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading workflows directory
    
    Usage: Get list of available workflows for bundle configuration.
    """
    workflows_dir = get_workflows_dir()
    if not os.path.exists(workflows_dir):
        return []
    
    try:
        files = os.listdir(workflows_dir)
        return [f for f in files if f.endswith('.json')]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing workflows: {str(e)}")

@workflows_router.post("/")
async def upload_workflow(
    workflow_file: UploadFile = File(...),
    user=Depends(protected)
):
    """
    POST /api/workflows/
    
    Uploads a workflow JSON file to the workflows directory.
    
    Arguments:
    - workflow_file (UploadFile): JSON file uploaded via multipart/form-data
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Workflow 'filename' uploaded successfully"}
    
    Possible errors:
    - 401: Not authenticated
    - 400: Invalid file or missing filename
    - 500: Error saving file to disk
    
    Usage: Upload ComfyUI workflow files for use with bundles.
    """
    workflows_dir = get_workflows_dir()
    os.makedirs(workflows_dir, exist_ok=True)
    file_path = os.path.join(workflows_dir, workflow_file.filename)
    
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(workflow_file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")
    
    return {"ok": True, "message": f"Workflow '{workflow_file.filename}' uploaded successfully"}

@workflows_router.get("/{filename}")
def get_workflow(filename: str, download: bool = False, user=Depends(protected)):
    """
    GET /api/workflows/{filename}
    
    Retrieves a workflow file content or downloads it.
    
    Arguments:
    - filename (str): Name of the workflow file (in URL path)
    - download (bool): Query parameter, if true returns file for download
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - If download=false: JSON content of the workflow
    - If download=true: File download response
    
    Possible errors:
    - 401: Not authenticated
    - 404: Workflow file not found
    - 500: Error reading workflow file
    
    Usage: View workflow content or download workflow files.
    """
    workflows_dir = get_workflows_dir()
    file_path = os.path.join(workflows_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Workflow '{filename}' not found")
    
    if download:
        return FileResponse(
            file_path,
            media_type="application/json",
            filename=filename
        )
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return JSONResponse(content=json.loads(content))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading workflow: {str(e)}")

@workflows_router.delete("/{filename}")
def delete_workflow(filename: str, user=Depends(protected)):
    """
    DELETE /api/workflows/{filename}
    
    Deletes a workflow file from the workflows directory.
    
    Arguments:
    - filename (str): Name of the workflow file to delete (in URL path)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Workflow 'filename' deleted successfully"}
    
    Possible errors:
    - 401: Not authenticated
    - 404: Workflow file not found
    - 500: Error deleting file
    
    Usage: Remove unwanted workflow files from the system.
    """
    workflows_dir = get_workflows_dir()
    file_path = os.path.join(workflows_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Workflow '{filename}' not found")
    
    try:
        os.remove(file_path)
        return {"ok": True, "message": f"Workflow '{filename}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting: {str(e)}")
