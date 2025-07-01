from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Body, Request
from back.services.download_service import DownloadService
from back.services.token_service import TokenService
from back.services.auth_middleware import protected
from back.models.model_models import (
    DownloadRequest, 
    ProgressRequest, 
    StopDownloadRequest,
    DeleteModelRequest,
    ModelEntry
)

# Router
download_router = APIRouter(prefix="/api/downloads")


@download_router.get("/")
@download_router.get("")
def get_all_downloads(user=Depends(protected)):
    """
    Returns the status of all ongoing model downloads.
    
    **Description:** Gets progress information for all active downloads with cleanup.
    **Parameters:**
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict with model_id as keys and progress info as values
    """
    return DownloadService.get_all_downloads()


@download_router.post("/start")
async def download_models(
    request: Request,
    background_tasks: BackgroundTasks,
    user=Depends(protected)
):
    """
    Starts downloading one or more models in the background.
    
    **Description:** Initiates model downloads with validation and token checking.
    **Parameters:**
    - `request` (Request): HTTP request with model entry or list of entries
    - `background_tasks` (BackgroundTasks): FastAPI background task queue
    - `user` (str): Authenticated user from JWT token
    **Returns:** Single result or list of results with download status
    """
    data = await request.json()
    hf_token, civitai_token = TokenService.read_env_file()
    
    # Handle both single entry and list of entries
    is_single = isinstance(data, dict)
    entries = [data] if is_single else data
    
    if not isinstance(entries, list):
        raise HTTPException(status_code=400, detail="Invalid input format")
    
    try:
        results = DownloadService.download_models(entries, hf_token, civitai_token)
        return results[0] if is_single else results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@download_router.post("/stop")
def stop_download(entry: dict, user=Depends(protected)):
    """
    Stops an ongoing download for a given model.
    
    **Description:** Cancels an active download and cleans up partial files.
    **Parameters:**
    - `entry` (dict): Model information to identify the download
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict with operation status and message
    """
    return DownloadService.stop_download(entry)


@download_router.post("/progress")
def get_progress(entry: dict = Body(...), user=Depends(protected)):
    """
    Returns download progress (POST with entry in body).
    
    **Description:** Retrieves the current download progress for a specific model.
    **Parameters:**
    - `entry` (dict): Model information to identify the download
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict containing progress percentage and status
    """
    model_id = DownloadService.get_model_id(entry)
    return DownloadService.get_progress(model_id)


@download_router.delete("/")
async def delete_models(
    request: Request,
    user=Depends(protected)
):
    """
    Deletes one or more model files from disk.
    
    **Description:** Removes model files with deduplication and validation.
    **Parameters:**
    - `request` (Request): HTTP request with model entry or list of entries
    - `user` (str): Authenticated user from JWT token
    **Returns:** Single result or list of results with deletion status
    """
    data = await request.json()
    
    # Handle both single entry and list of entries
    is_single = isinstance(data, dict)
    entries = [data] if is_single else data
    
    if not isinstance(entries, list):
        raise HTTPException(status_code=400, detail="Invalid input format")
    
    try:
        results = DownloadService.delete_models(entries)
        return results[0] if is_single else results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
