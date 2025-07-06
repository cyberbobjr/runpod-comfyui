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
import traceback

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
router = APIRouter(prefix="/api/bundles", tags=["Bundles"])

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
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error retrieving bundles: {str(e)}")


@router.post("/install", response_model=BundleInstallResponse)
def install_bundle(install_request: BundleInstallRequest, user=Depends(protected)):
    """
    POST /api/bundles/install

    Installs a bundle's models and workflows for a specific hardware profile.

    Arguments:
    - install_request (BundleInstallRequest):
        - bundle_id (str): The unique identifier of the bundle to install.
        - profile (str): The hardware profile to use for installation (e.g., 'default', 'cuda', etc.).
    - user: Authentication token (automatic via Depends)

    Returns:
    - Status: 200 OK
    - Body: BundleInstallResponse object with:
        - ok (bool): True if installation succeeded.
        - message (str): Human-readable status message.
        - results (dict):
            - installed (list of str): List of successfully installed model filenames.
            - failed (list of str): List of model filenames that failed to install.

    Example response:
    ```
    {
        "ok": true,
        "message": "Bundle installed successfully",
        "results": {
            "installed": ["modelA.safetensors", "modelB.safetensors"],
            "failed": []
        }
    }
    ```

    Possible errors:
    - 401: Not authenticated
    - 404: Bundle or profile not found
    - 400: Invalid installation request
    - 500: Error during installation

    Usage: Use this endpoint to install all models and workflows for a bundle under a specific hardware profile. The response details which models were installed or failed.
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
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error installing bundle: {str(e)}")


from pydantic import BaseModel

class BundleUninstallRequest(BaseModel):
    bundle_id: str
    profile: str

@router.post("/uninstall")
def uninstall_bundle(uninstall_request: BundleUninstallRequest, user=Depends(protected)):
    """
    POST /api/bundles/uninstall

    Uninstalls a specific hardware profile from an installed bundle. If all profiles are uninstalled, the bundle is considered fully uninstalled.

    Arguments:
    - uninstall_request (BundleUninstallRequest):
        - bundle_id (str): The unique identifier of the bundle to uninstall.
        - profile (str): The hardware profile to uninstall from the bundle.
    - user: Authentication token (automatic via Depends)

    Returns:
    - Status: 200 OK
    - Body: {"ok": true, "message": "Profile '<profile>' uninstalled from bundle '<bundle_id>'"}

    Example response:
    ```
    {
        "ok": true,
        "message": "Profile 'cuda' uninstalled from bundle 'example-bundle-id'"
    }
    ```

    Possible errors:
    - 401: Not authenticated
    - 404: Bundle or profile not found or not installed
    - 500: Error during uninstallation

    Usage: Use this endpoint to uninstall a specific hardware profile from a bundle. If all profiles are uninstalled, the bundle will be fully removed from the installed list.
    """
    try:
        bundle_service.uninstall_bundle(uninstall_request.bundle_id, uninstall_request.profile)
        return {"ok": True, "message": f"Profile '{uninstall_request.profile}' uninstalled from bundle '{uninstall_request.bundle_id}'"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Bundle {uninstall_request.bundle_id} or profile {uninstall_request.profile} not found or not installed")
    except Exception as e:
        logger.error(f"Error uninstalling profile {uninstall_request.profile} from bundle {uninstall_request.bundle_id}: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error uninstalling bundle profile: {str(e)}")


@router.get("/installed", response_model=List[Dict[str, Any]])
def get_installed_bundles(user=Depends(protected)):
    """
    GET /api/bundles/installed

    Retrieves the list of all installed bundles with their installation details.

    Arguments:
    - user: Authentication token (automatic via Depends)

    Returns:
    - Status: 200 OK
    - Body: Array of objects, each containing:
        - "bundle": Bundle object (full bundle metadata)
        - "installation": Installation information, including:
            - profile (str): Hardware profile used for installation
            - installed_at (str): ISO timestamp of installation
            - status (str): Installation status (e.g., "completed", "partial")
            - installed_models (list of str): List of successfully installed models
            - failed_models (list of str): List of models that failed to install

    Example response:
    
    ```
    [
            
        {
            "profile": "default",
            "installed_at": "2024-07-01T12:34:56.789Z",
            "status": "completed",
            "installed_models": ["modelA.safetensors", "modelB.safetensors"],
            "failed_models": []
        },
        ...
    ]
    ```
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading installation records

    Usage: Get list of bundles that are currently installed, including their installation status and details.
    """
    try:
        return bundle_service.get_installed_bundles()
    except Exception as e:
        logger.error(f"Error getting installed bundles: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error retrieving installed bundles: {str(e)}")



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
        bundle = bundle_service.get_bundle(bundle_id)
        return bundle
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Bundle with id {bundle_id} not found")
    except Exception as e:
        logger.error(f"Error getting bundle {bundle_id}: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error retrieving bundle: {str(e)}")


@router.post("/", response_model=Bundle)
def create_bundle(bundle_data: BundleCreate, user=Depends(protected)):
    """
    POST /api/bundles/

    Creates a new bundle.

    **Arguments:**
    - `bundle_data` (BundleCreate): Bundle creation data (see BundleCreate schema)
    - `user`: Authentication token (automatic via Depends)

    **Returns:**
    - Status: 200 OK
    - Body: Created Bundle object (see Bundle schema)

    **Example response:**
    ```
    {
        "id": "example-bundle-id",
        "name": "Example Bundle",
        "description": "A test bundle.",
        "version": "1.0.0",
        "author": "Author Name",
        "website": "https://example.com",
        "hardware_profiles": { ... },
        "workflows": [ ... ],
        "workflow_params": { ... },
        "created_at": "2024-07-01T12:34:56.789Z",
        "updated_at": "2024-07-01T12:34:56.789Z"
    }
    ```

    **Possible errors:**
    - 401: Not authenticated
    - 400: Invalid bundle data
    - 409: Bundle with same name already exists
    - 500: Error creating bundle

    **Usage:**
    Create a new bundle from provided data for later installation or sharing.
    """
    try:
        new_bundle = bundle_service.create_bundle(bundle_data)
        return new_bundle
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating bundle: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error creating bundle: {str(e)}")


@router.put("/{bundle_id}", response_model=Bundle)
def update_bundle(bundle_id: str, bundle_data: BundleUpdate, user=Depends(protected)):
    """
    PUT /api/bundles/{bundle_id}

    Updates an existing bundle.

    **Arguments:**
    - `bundle_id` (str): Bundle identifier (in URL path)
    - `bundle_data` (BundleUpdate): Bundle update data (see BundleUpdate schema)
    - `user`: Authentication token (automatic via Depends)

    **Returns:**
    - Status: 200 OK
    - Body: Updated Bundle object (see Bundle schema)

    **Example response:**
    ```
    {
        "id": "example-bundle-id",
        "name": "Updated Bundle Name",
        ...
    }
    ```

    **Possible errors:**
    - 401: Not authenticated
    - 404: Bundle not found
    - 400: Invalid update data
    - 500: Error updating bundle

    **Usage:**
    Update an existing bundle's properties, such as name, description, or hardware profiles.
    """
    try:
        updated_bundle = bundle_service.update_bundle(bundle_id, bundle_data)
        return updated_bundle
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Bundle with id {bundle_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating bundle {bundle_id}: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error updating bundle: {str(e)}")


@router.delete("/{bundle_id}")
def delete_bundle(bundle_id: str, user=Depends(protected)):
    """
    DELETE /api/bundles/{bundle_id}

    Deletes a bundle.

    **Arguments:**
    - `bundle_id` (str): Bundle identifier (in URL path)
    - `user`: Authentication token (automatic via Depends)

    **Returns:**
    - Status: 200 OK
    - Body: `{ "ok": true, "message": "Bundle deleted successfully" }`

    **Example response:**
    ```
    {
        "ok": true,
        "message": "Bundle deleted successfully"
    }
    ```

    **Possible errors:**
    - 401: Not authenticated
    - 404: Bundle not found
    - 500: Error deleting bundle

    **Usage:**
    Remove a bundle from the system and delete its ZIP file.
    """
    try:
        bundle_service.delete_bundle(bundle_id)
        return {"ok": True, "message": f"Bundle with id {bundle_id} deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Bundle with id {bundle_id} not found")
    except Exception as e:
        logger.error(f"Error deleting bundle {bundle_id}: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error deleting bundle: {str(e)}")


@router.post("/upload")
def upload_bundle(file: UploadFile = File(...), user=Depends(protected)):
    """
    POST /api/bundles/upload

    Uploads and imports a bundle from a ZIP file.

    **Arguments:**
    - `file` (UploadFile): ZIP file containing bundle data
    - `user`: Authentication token (automatic via Depends)

    **Returns:**
    - Status: 200 OK
    - Body: `{ "ok": true, "message": "Bundle imported successfully", "bundle_id": "id" }`

    **Example response:**
    ```
    {
        "ok": true,
        "message": "Bundle imported successfully",
        "bundle_id": "example-bundle-id"
    }
    ```

    **Possible errors:**
    - 401: Not authenticated
    - 400: Invalid file format or corrupted bundle
    - 409: Bundle already exists
    - 500: Error processing upload

    **Usage:**
    Import a bundle from an uploaded ZIP file for installation or sharing.
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
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error uploading bundle: {str(e)}")


@router.get("/download/{bundle_id}")
def download_bundle(bundle_id: str, user=Depends(protected)):
    """
    GET /api/bundles/download/{bundle_id}

    Downloads a bundle as a ZIP file.

    **Arguments:**
    - `bundle_id` (str): Bundle identifier (in URL path)
    - `user`: Authentication token (automatic via Depends)

    **Returns:**
    - Status: 200 OK
    - Body: ZIP file download
    - Headers: Content-Disposition with filename

    **Usage:**
    Download a bundle as a ZIP file for backup, migration, or sharing with others.

    **Possible errors:**
    - 401: Not authenticated
    - 404: Bundle not found
    - 500: Error creating download
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
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error downloading bundle: {str(e)}")


@router.post("/duplicate", response_model=Bundle)
def duplicate_bundle(bundle_id: str, duplicate_data: BundleDuplicateRequest, user=Depends(protected)):
    """
    POST /api/bundles/duplicate/{bundle_id}

    Creates a duplicate of an existing bundle with a new name.

    **Arguments:**
    - `bundle_id` (str): Source bundle identifier (in URL path)
    - `duplicate_data` (BundleDuplicateRequest): New bundle name and optional modifications
    - `user`: Authentication token (automatic via Depends)

    **Returns:**
    - Status: 200 OK
    - Body: `{ "ok": true, "message": "Bundle duplicated successfully", "new_bundle_id": "id" }`

    **Example response:**
    ```
    {
        "ok": true,
        "message": "Bundle duplicated successfully",
        "new_bundle_id": "new-bundle-id"
    }
    ```

    **Possible errors:**
    - 401: Not authenticated
    - 404: Source bundle not found
    - 409: Target bundle name already exists
    - 500: Error during duplication

    **Usage:**
    Create a copy of a bundle with a different name for modification, testing, or versioning.
    """
    try:
        new_bundle = bundle_service.duplicate_bundle(duplicate_data.original_bundle_id, duplicate_data.new_name)
        return new_bundle
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error duplicating bundle: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error duplicating bundle: {str(e)}")


@router.post("/export/{bundle_id}", response_class=FileResponse)
def export_bundle(bundle_id: str, user=Depends(protected)):
    """
    POST /api/bundles/export/{bundle_id}

    Exports a bundle as a ZIP file.

    **Arguments:**
    - `bundle_id` (str): Bundle identifier (in URL path)
    - `user`: Authentication token (automatic via Depends)

    **Returns:**
    - Status: 200 OK
    - Body: ZIP file download
    - Headers: Content-Disposition with filename

    **Usage:**
    Export a bundle as a ZIP file for backup, migration, or sharing with others.

    **Possible errors:**
    - 401: Not authenticated
    - 404: Bundle not found
    - 500: Error creating export
    """
    try:
        zip_path = bundle_service.export_bundle(bundle_id)
        return FileResponse(zip_path, media_type='application/zip', filename=f"{bundle_id}.zip")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Bundle with id {bundle_id} not found")
    except Exception as e:
        logger.error(f"Error exporting bundle {bundle_id}: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error exporting bundle: {str(e)}")


@router.post("/import", response_model=Bundle)
async def import_bundle(file: UploadFile = File(...), user=Depends(protected)):
    """
    POST /api/bundles/import

    Imports a bundle from a ZIP file.

    **Arguments:**
    - `file` (UploadFile): ZIP file containing the bundle
    - `user`: Authentication token (automatic via Depends)

    **Returns:**
    - Status: 200 OK
    - Body: Imported Bundle object

    **Possible errors:**
    - 401: Not authenticated
    - 400: Invalid file format or corrupted bundle
    - 409: Bundle with the same name already exists
    - 500: Error processing import

    **Usage:**
    Import a bundle from an uploaded ZIP file for installation or sharing.
    """
    try:
        imported_bundle = await bundle_service.import_bundle(file)
        return imported_bundle
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error importing bundle: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error importing bundle: {str(e)}")
