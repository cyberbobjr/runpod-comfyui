"""
Workflow Router - Handle workflow management API routes

This module contains all API routes for workflow management including:
- Workflow listing and metadata
- Upload and download operations
- Workflow validation
- File management
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import List

from ..services.auth_middleware import protected
from ..services.workflow_service import WorkflowService
from ..models.workflow_models import (
    WorkflowInfo, WorkflowListResponse, WorkflowUploadResponse,
    WorkflowDeleteResponse, WorkflowValidationResponse, WorkflowContent
)
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/workflows", tags=["workflows"])

# Initialize service
workflow_service = WorkflowService()


@router.get("/", response_model=List[str])
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
    try:
        workflows = workflow_service.list_workflows()
        return workflows
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing workflows: {str(e)}")


@router.get("/detailed", response_model=WorkflowListResponse)
def list_workflows_detailed(user=Depends(protected)):
    """
    GET /api/workflows/detailed
    
    Lists all workflows with detailed information including metadata.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: WorkflowListResponse with detailed workflow information
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading workflows directory
    
    Usage: Get detailed workflow information for management interface.
    """
    try:
        workflows_info = workflow_service.list_workflows_with_info()
        return WorkflowListResponse(
            workflows=[WorkflowInfo(**info) for info in workflows_info],
            total_count=len(workflows_info)
        )
    except Exception as e:
        logger.error(f"Error listing detailed workflows: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing workflows: {str(e)}")


@router.post("/upload", response_model=WorkflowUploadResponse)
def upload_workflow(
    workflow_file: UploadFile = File(...),
    user=Depends(protected)
):
    """
    POST /api/workflows/upload
    
    Uploads a workflow JSON file to the workflows directory.
    
    Arguments:
    - workflow_file (UploadFile): JSON file uploaded via multipart/form-data
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: WorkflowUploadResponse with upload details
    
    Possible errors:
    - 401: Not authenticated
    - 400: Invalid file or missing filename, invalid JSON
    - 500: Error saving file to disk
    
    Usage: Upload ComfyUI workflow files for use with bundles.
    """
    try:
        result = workflow_service.upload_workflow(workflow_file)
        return WorkflowUploadResponse(
            ok=True,
            message=f"Workflow '{workflow_file.filename}' uploaded successfully",
            filename=result['filename'],
            size=result['size']
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@router.post("/", response_model=WorkflowUploadResponse)
def upload_workflow_alt(
    workflow_file: UploadFile = File(...),
    user=Depends(protected)
):
    """
    POST /api/workflows/
    
    Alternative endpoint for workflow upload at root path.
    
    Arguments:
    - workflow_file (UploadFile): JSON file uploaded via multipart/form-data
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: WorkflowUploadResponse with upload details
    
    Possible errors:
    - 401: Not authenticated
    - 400: Invalid file or missing filename, invalid JSON
    - 500: Error saving file to disk
    
    Usage: Alternative upload endpoint for workflows.
    """
    return upload_workflow(workflow_file, user)


@router.get("/{filename}")
def get_workflow(
    filename: str, 
    download: bool = Query(False, description="Download file instead of returning JSON"),
    user=Depends(protected)
):
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
    - 400: Invalid JSON in workflow file
    - 500: Error reading workflow file
    
    Usage: View workflow content or download workflow files.
    """
    try:
        if download:
            file_path = workflow_service.get_workflow_file_path(filename)
            return FileResponse(
                file_path,
                media_type="application/json",
                filename=filename
            )
        else:
            content = workflow_service.get_workflow_content(filename)
            return JSONResponse(content=content['content'])
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Workflow '{filename}' not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting workflow {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading workflow: {str(e)}")


@router.get("/{filename}/info", response_model=WorkflowInfo)
def get_workflow_info(filename: str, user=Depends(protected)):
    """
    GET /api/workflows/{filename}/info
    
    Gets detailed information about a workflow file.
    
    Arguments:
    - filename (str): Name of the workflow file (in URL path)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: WorkflowInfo with file metadata
    
    Possible errors:
    - 401: Not authenticated
    - 404: Workflow file not found
    - 500: Error reading workflow file
    
    Usage: Get metadata about a specific workflow file.
    """
    try:
        info = workflow_service.get_workflow_info(filename)
        return WorkflowInfo(**info)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Workflow '{filename}' not found")
    except Exception as e:
        logger.error(f"Error getting workflow info for {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting workflow info: {str(e)}")


@router.get("/{filename}/validate", response_model=WorkflowValidationResponse)
def validate_workflow(filename: str, user=Depends(protected)):
    """
    GET /api/workflows/{filename}/validate
    
    Validates a workflow file structure and content.
    
    Arguments:
    - filename (str): Name of the workflow file (in URL path)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: WorkflowValidationResponse with validation results
    
    Possible errors:
    - 401: Not authenticated
    - 404: Workflow file not found
    - 500: Error during validation
    
    Usage: Validate workflow file structure and ComfyUI compatibility.
    """
    try:
        validation = workflow_service.validate_workflow(filename)
        return WorkflowValidationResponse(**validation)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Workflow '{filename}' not found")
    except Exception as e:
        logger.error(f"Error validating workflow {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error validating workflow: {str(e)}")


@router.delete("/{filename}", response_model=WorkflowDeleteResponse)
def delete_workflow(filename: str, user=Depends(protected)):
    """
    DELETE /api/workflows/{filename}
    
    Deletes a workflow file from the workflows directory.
    
    Arguments:
    - filename (str): Name of the workflow file to delete (in URL path)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: WorkflowDeleteResponse with deletion confirmation
    
    Possible errors:
    - 401: Not authenticated
    - 404: Workflow file not found
    - 500: Error deleting file
    
    Usage: Remove unwanted workflow files from the system.
    """
    try:
        workflow_service.delete_workflow(filename)
        return WorkflowDeleteResponse(
            ok=True,
            message=f"Workflow '{filename}' deleted successfully",
            filename=filename
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Workflow '{filename}' not found")
    except Exception as e:
        logger.error(f"Error deleting workflow {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting workflow: {str(e)}")


@router.head("/{filename}")
def check_workflow_exists(filename: str, user=Depends(protected)):
    """
    HEAD /api/workflows/{filename}
    
    Checks if a workflow file exists without returning content.
    
    Arguments:
    - filename (str): Name of the workflow file (in URL path)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK if file exists
    - Status: 404 if file doesn't exist
    
    Possible errors:
    - 401: Not authenticated
    - 404: Workflow file not found
    
    Usage: Check workflow existence without downloading content.
    """
    if not workflow_service.workflow_exists(filename):
        raise HTTPException(status_code=404, detail=f"Workflow '{filename}' not found")
    
    return {"exists": True}
