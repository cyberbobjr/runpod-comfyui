"""
File Manager Router - Handle all file management API routes

This module contains all API routes for file management including:
- Directory listing and navigation
- File operations (copy, move, delete, rename)
- File upload and download
- File properties and metadata
"""

import os
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from typing import List, Optional, Dict, Any

from ..services.auth_middleware import protected
from ..services.file_manager_service import FileManagerService
from ..models.file_models import (
    FileInfo, DirectoryListing, FileOperationRequest, RenameRequest,
    CreateDirectoryRequest, FilePropertiesResponse, UploadResponse,
    ModelsInfoResponse, FileOperationResponse
)
from ..utils.logger import get_logger
from back.services.model_service import ModelService

# Initialize logger
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/file", tags=["file-manager"])

# Initialize service
file_service = FileManagerService()


@router.get("/list_dirs")
def list_directories(path: str = Query("", description="Directory path to list"), user=Depends(protected)):
    """
    GET /api/file/list_dirs
    
    Lists directories in the specified path.
    
    Arguments:
    - path (str): Relative directory path (query parameter)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Array of directory information objects
    
    Possible errors:
    - 401: Not authenticated
    - 404: Directory not found
    - 403: Access denied (path outside allowed directory)
    - 500: File system error
    
    Usage: Get list of subdirectories for navigation.
    """
    try:
        directories = file_service.list_directories(path)
        return directories
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Directory not found: {path}")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing directories: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing directories: {str(e)}")


@router.get("/list_all_dirs")
def list_all_directories(user=Depends(protected)):
    """
    GET /api/file/list_all_dirs
    
    Recursively lists all directories in the base directory.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Array of all directory information objects
    
    Possible errors:
    - 401: Not authenticated
    - 500: File system error
    
    Usage: Get complete directory tree for navigation.
    """
    try:
        directories = file_service.list_all_directories()
        return directories
    except Exception as e:
        logger.error(f"Error listing all directories: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing directories: {str(e)}")


@router.get("/list_files")
def list_files(
    path: str = Query("", description="Directory path to list"),
    extensions: Optional[str] = Query(None, description="Comma-separated file extensions to filter"),
    user=Depends(protected)
):
    """
    GET /api/file/list_files
    
    Lists files in the specified directory with optional extension filtering.
    
    Arguments:
    - path (str): Relative directory path (query parameter)
    - extensions (str, optional): Comma-separated file extensions (e.g., ".ckpt,.safetensors")
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Object with files, directories, and metadata
    
    Possible errors:
    - 401: Not authenticated
    - 404: Directory not found
    - 403: Access denied
    - 500: File system error
    
    Usage: Browse files in a directory with registration status.
    """
    try:
        ext_list = None
        if extensions:
            ext_list = [ext.strip() for ext in extensions.split(",")]
        
        result = file_service.list_files(path, ext_list)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Directory not found: {path}")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@router.post("/copy", response_model=FileOperationResponse)
def copy_file(request: FileOperationRequest, user=Depends(protected)):
    """
    POST /api/file/copy
    
    Copies a file or directory to a new location.
    
    Arguments:
    - request (FileOperationRequest): Copy request with source and target paths
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: FileOperationResponse with operation details
    
    Possible errors:
    - 401: Not authenticated
    - 404: Source file not found
    - 409: Target already exists
    - 403: Access denied
    - 500: File system error
    
    Usage: Copy files or directories to new locations.
    """
    try:
        if not request.target_path:
            raise HTTPException(status_code=400, detail="Target path is required for copy operation")
        
        file_service.copy_file(request.source_path, request.target_path)
        return FileOperationResponse(
            ok=True,
            message=f"Successfully copied {request.source_path} to {request.target_path}",
            operation="copy",
            source_path=request.source_path,
            target_path=request.target_path
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Source not found: {request.source_path}")
    except FileExistsError:
        raise HTTPException(status_code=409, detail=f"Target already exists: {request.target_path}")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error copying file: {e}")
        raise HTTPException(status_code=500, detail=f"Error copying file: {str(e)}")


@router.post("/delete", response_model=FileOperationResponse)
def delete_file(request: FileOperationRequest, user=Depends(protected)):
    """
    POST /api/file/delete
    
    Deletes a file or directory.
    
    Arguments:
    - request (FileOperationRequest): Delete request with source path
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: FileOperationResponse with operation details
    
    Possible errors:
    - 401: Not authenticated
    - 404: File not found
    - 403: Access denied
    - 500: File system error
    
    Usage: Delete files or directories from the system.
    """
    try:
        file_service.delete_file(request.source_path)
        return FileOperationResponse(
            ok=True,
            message=f"Successfully deleted {request.source_path}",
            operation="delete",
            source_path=request.source_path
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.source_path}")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")


@router.post("/rename", response_model=FileOperationResponse)
def rename_file(request: RenameRequest, user=Depends(protected)):
    """
    POST /api/file/rename
    
    Renames a file or directory.
    
    Arguments:
    - request (RenameRequest): Rename request with old path and new name
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: FileOperationResponse with operation details and new path
    
    Possible errors:
    - 401: Not authenticated
    - 404: File not found
    - 409: New name already exists
    - 403: Access denied
    - 500: File system error
    
    Usage: Rename files or directories.
    """
    try:
        new_path = file_service.rename_file(request.old_path, request.new_name)
        return FileOperationResponse(
            ok=True,
            message=f"Successfully renamed {request.old_path} to {request.new_name}",
            operation="rename",
            source_path=request.old_path,
            target_path=new_path
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.old_path}")
    except FileExistsError:
        raise HTTPException(status_code=409, detail=f"File already exists: {request.new_name}")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error renaming file: {e}")
        raise HTTPException(status_code=500, detail=f"Error renaming file: {str(e)}")


@router.get("/properties", response_model=FilePropertiesResponse)
def get_file_properties(path: str = Query(..., description="File path"), user=Depends(protected)):
    """
    GET /api/file/properties
    
    Gets detailed properties of a file or directory.
    
    Arguments:
    - path (str): File path (query parameter)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: FilePropertiesResponse with file metadata
    
    Possible errors:
    - 401: Not authenticated
    - 404: File not found
    - 403: Access denied
    - 500: File system error
    
    Usage: Get detailed information about a file including registration status.
    """
    try:
        properties = file_service.get_file_properties(path)
        return FilePropertiesResponse(**properties)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting file properties: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting file properties: {str(e)}")


@router.get("/download")
def download_file(path: str = Query(..., description="File path to download"), user=Depends(protected)):
    """
    GET /api/file/download
    
    Downloads a file from the server.
    
    Arguments:
    - path (str): File path to download (query parameter)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: File download stream
    - Headers: Content-Disposition with filename
    
    Possible errors:
    - 401: Not authenticated
    - 404: File not found
    - 403: Access denied or directory specified
    - 500: File system error
    
    Usage: Download files from the server to client.
    """
    try:
        full_path = file_service.safe_join(file_service.base_dir, path)
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File not found: {path}")
        
        if os.path.isdir(full_path):
            raise HTTPException(status_code=403, detail="Cannot download directories")
        
        return FileResponse(
            full_path,
            media_type="application/octet-stream",
            filename=os.path.basename(full_path)
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")


@router.post("/upload", response_model=UploadResponse)
def upload_file(
    file: UploadFile = File(...),
    path: str = Form("", description="Target directory path"),
    user=Depends(protected)
):
    """
    POST /api/file/upload
    
    Uploads a file to the server.
    
    Arguments:
    - file (UploadFile): File to upload (multipart form data)
    - path (str): Target directory path (form field)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: UploadResponse with upload details
    
    Possible errors:
    - 401: Not authenticated
    - 400: Invalid file or path
    - 403: Access denied
    - 500: File system error
    
    Usage: Upload files to the server file system.
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        result = file_service.save_uploaded_file(file, path)
        return UploadResponse(
            ok=True,
            message=f"File {file.filename} uploaded successfully",
            **result
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("/models_info", response_model=ModelsInfoResponse)
def get_models_info(user=Depends(protected)):
    """
    GET /api/file/models_info
    
    Gets comprehensive information about model files.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: ModelsInfoResponse with registered and unregistered models
    
    Possible errors:
    - 401: Not authenticated
    - 500: File system error
    
    Usage: Analyze model files and their registration status.
    """
    try:
        info = file_service.get_models_info()
        return ModelsInfoResponse(**info)
    except Exception as e:
        logger.error(f"Error getting models info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting models info: {str(e)}")


@router.post("/create_dir", response_model=FileOperationResponse)
def create_directory(request: CreateDirectoryRequest, user=Depends(protected)):
    """
    POST /api/file/create_dir
    
    Creates a new directory.
    
    Arguments:
    - request (CreateDirectoryRequest): Directory creation request
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: FileOperationResponse with creation details
    
    Possible errors:
    - 401: Not authenticated
    - 409: Directory already exists
    - 403: Access denied
    - 500: File system error
    
    Usage: Create new directories in the file system.
    """
    try:
        file_service.create_directory(request.path, request.recursive)
        return FileOperationResponse(
            ok=True,
            message=f"Directory {request.path} created successfully",
            operation="create_directory",
            target_path=request.path
        )
    except FileExistsError:
        raise HTTPException(status_code=409, detail=f"Directory already exists: {request.path}")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating directory: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating directory: {str(e)}")


@router.get("/total_size")
def total_size(user=Depends(protected)):
    """
    GET /api/file/total_size
    
    Returns the total size (in bytes) of the base_dir directory.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Dict containing base directory path and total size
    
    Usage: Calculates and returns the total disk space used by the ComfyUI installation.
    """
    return ModelService.get_total_size()
