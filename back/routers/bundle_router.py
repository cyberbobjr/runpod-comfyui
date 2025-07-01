"""
Bundle Router - Handle all bundle-related API routes

This module contains all API routes for bundle management including:
- CRUD operations on bundles
- Bundle installation/uninstallation  
- Bundle export/import
- Bundle duplication
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Query
from fastapi.responses import FileResponse
from typing import List, Dict, Any

from ..services.auth_middleware import protected
from ..services.bundle_service import BundleService
from ..models.bundle_models import (
    Bundle, BundleCreate, BundleUpdate, BundleInstallRequest, 
    BundleInstallResponse, BundleDuplicateRequest
)
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/bundles", tags=["bundles"])

# Initialize service
bundle_service = BundleService()


@router.get("/", response_model=List[Bundle])
def get_all_bundles(user=Depends(protected)):
    """
    GET /api/bundles
    
    Retrieves all available bundles.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Array of Bundle objects
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading bundle files
    
    Usage: Get list of all available bundles for display.
    """
    try:
        return bundle_service.get_all_bundles()
    except Exception as e:
        logger.error(f"Error getting bundles: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving bundles: {str(e)}")


@router.get("/{bundle_id}", response_model=Bundle)
def get_bundle(bundle_id: str, user=Depends(protected)):
    """
    GET /api/bundles/{bundle_id}
    
    Retrieves a specific bundle by ID.
    
    Arguments:
    - bundle_id (str): Bundle identifier (in URL path)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Bundle object
    
    Possible errors:
    - 401: Not authenticated
    - 404: Bundle not found
    - 500: Error reading bundle file
    
    Usage: Get details of a specific bundle.
    """
    try:
        return bundle_service.get_bundle(bundle_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Bundle {bundle_id} not found")
    except Exception as e:
        logger.error(f"Error getting bundle {bundle_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving bundle: {str(e)}")


@router.post("/", response_model=Bundle)
def create_bundle(bundle_data: BundleCreate, user=Depends(protected)):
    """
    POST /api/bundles/
    
    Creates a new bundle.
    
    Arguments:
    - bundle_data (BundleCreate): Bundle creation data
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Created Bundle object
    
    Possible errors:
    - 401: Not authenticated
    - 400: Invalid bundle data
    - 409: Bundle with same name already exists
    - 500: Error creating bundle
    
    Usage: Create a new bundle from provided data.
    """
    try:
        return bundle_service.create_bundle(bundle_data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating bundle: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating bundle: {str(e)}")


@router.put("/{bundle_id}", response_model=Bundle)
def update_bundle(bundle_id: str, bundle_data: BundleUpdate, user=Depends(protected)):
    """
    PUT /api/bundles/{bundle_id}
    
    Updates an existing bundle.
    
    Arguments:
    - bundle_id (str): Bundle identifier (in URL path)
    - bundle_data (BundleUpdate): Bundle update data
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Updated Bundle object
    
    Possible errors:
    - 401: Not authenticated
    - 404: Bundle not found
    - 400: Invalid update data
    - 500: Error updating bundle
    
    Usage: Update an existing bundle's properties.
    """
    try:
        return bundle_service.update_bundle(bundle_id, bundle_data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Bundle {bundle_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating bundle {bundle_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating bundle: {str(e)}")


@router.delete("/{bundle_id}")
def delete_bundle(bundle_id: str, user=Depends(protected)):
    """
    DELETE /api/bundles/{bundle_id}
    
    Deletes a bundle.
    
    Arguments:
    - bundle_id (str): Bundle identifier (in URL path)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Bundle deleted"}
    
    Possible errors:
    - 401: Not authenticated
    - 404: Bundle not found
    - 500: Error deleting bundle
    
    Usage: Remove a bundle from the system.
    """
    try:
        bundle_service.delete_bundle(bundle_id)
        return {"ok": True, "message": f"Bundle {bundle_id} deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Bundle {bundle_id} not found")
    except Exception as e:
        logger.error(f"Error deleting bundle {bundle_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting bundle: {str(e)}")


@router.post("/upload")
def upload_bundle(file: UploadFile = File(...), user=Depends(protected)):
    """
    POST /api/bundles/upload
    
    Uploads and imports a bundle from a ZIP file.
    
    Arguments:
    - file (UploadFile): ZIP file containing bundle data
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Bundle imported", "bundle_id": "id"}
    
    Possible errors:
    - 401: Not authenticated
    - 400: Invalid file format or corrupted bundle
    - 409: Bundle already exists
    - 500: Error processing upload
    
    Usage: Import a bundle from an uploaded ZIP file.
    """
    try:
        bundle_id = bundle_service.import_bundle_from_zip(file)
        return {
            "ok": True, 
            "message": "Bundle imported successfully",
            "bundle_id": bundle_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading bundle: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading bundle: {str(e)}")


@router.get("/download/{bundle_id}")
def download_bundle(bundle_id: str, user=Depends(protected)):
    """
    GET /api/bundles/download/{bundle_id}
    
    Downloads a bundle as a ZIP file.
    
    Arguments:
    - bundle_id (str): Bundle identifier (in URL path)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: ZIP file download
    - Headers: Content-Disposition with filename
    
    Possible errors:
    - 401: Not authenticated
    - 404: Bundle not found
    - 500: Error creating download
    
    Usage: Download a bundle as a ZIP file for backup or sharing.
    """
    try:
        zip_path = bundle_service.get_bundle_download_path(bundle_id)
        return FileResponse(
            zip_path, 
            media_type="application/zip",
            filename=f"{bundle_id}.zip"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Bundle {bundle_id} not found")
    except Exception as e:
        logger.error(f"Error downloading bundle {bundle_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading bundle: {str(e)}")


@router.post("/install", response_model=BundleInstallResponse)
def install_bundle(install_request: BundleInstallRequest, user=Depends(protected)):
    """
    POST /api/bundles/install
    
    Installs a bundle with a specific hardware profile.
    
    Arguments:
    - install_request (BundleInstallRequest): Installation request with bundle_id and profile
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: BundleInstallResponse with results
    
    Possible errors:
    - 401: Not authenticated
    - 404: Bundle or profile not found
    - 400: Invalid installation request
    - 500: Error during installation
    
    Usage: Install a bundle's models and workflows for a specific hardware profile.
    """
    try:
        result = bundle_service.install_bundle(install_request.bundle_id, install_request.profile)
        return BundleInstallResponse(
            ok=True,
            message="Bundle installed successfully",
            results=result
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error installing bundle: {e}")
        raise HTTPException(status_code=500, detail=f"Error installing bundle: {str(e)}")


@router.post("/uninstall")
def uninstall_bundle(bundle_id: str, user=Depends(protected)):
    """
    POST /api/bundles/uninstall
    
    Uninstalls a previously installed bundle.
    
    Arguments:
    - bundle_id (str): Bundle identifier in request body
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Bundle uninstalled"}
    
    Possible errors:
    - 401: Not authenticated
    - 404: Bundle not found or not installed
    - 500: Error during uninstallation
    
    Usage: Remove an installed bundle's models and workflows.
    """
    try:
        bundle_service.uninstall_bundle(bundle_id)
        return {"ok": True, "message": f"Bundle {bundle_id} uninstalled successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Bundle {bundle_id} not found or not installed")
    except Exception as e:
        logger.error(f"Error uninstalling bundle {bundle_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error uninstalling bundle: {str(e)}")


@router.get("/installed/", response_model=List[Dict[str, Any]])
def get_installed_bundles(user=Depends(protected)):
    """
    GET /api/bundles/installed/
    
    Retrieves list of all installed bundles.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Array of installed bundle information
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading installation records
    
    Usage: Get list of bundles that are currently installed.
    """
    try:
        return bundle_service.get_installed_bundles()
    except Exception as e:
        logger.error(f"Error getting installed bundles: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving installed bundles: {str(e)}")


@router.post("/duplicate/{bundle_id}")
def duplicate_bundle(bundle_id: str, duplicate_data: BundleDuplicateRequest, user=Depends(protected)):
    """
    POST /api/bundles/duplicate/{bundle_id}
    
    Creates a duplicate of an existing bundle with a new name.
    
    Arguments:
    - bundle_id (str): Source bundle identifier (in URL path)
    - duplicate_data (BundleDuplicateRequest): New bundle name and optional modifications
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Bundle duplicated", "new_bundle_id": "id"}
    
    Possible errors:
    - 401: Not authenticated
    - 404: Source bundle not found
    - 409: Target bundle name already exists
    - 500: Error during duplication
    
    Usage: Create a copy of a bundle with a different name for modification.
    """
    try:
        new_bundle_id = bundle_service.duplicate_bundle(bundle_id, duplicate_data.new_name)
        return {
            "ok": True,
            "message": f"Bundle duplicated successfully",
            "new_bundle_id": new_bundle_id
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Bundle {bundle_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error duplicating bundle {bundle_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error duplicating bundle: {str(e)}")
