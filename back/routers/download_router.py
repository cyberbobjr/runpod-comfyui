from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Body, Request
from back.services.download_service import DownloadService
from back.services.token_service import TokenService
from back.services.auth_middleware import protected

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
    
    **Returns:** 
    A list of dictionaries, each containing the model_id and its progress information.
    
    **Example response:**
    ```json
    [
      {
        "model_id": "model_123",
        "progress": 50,
        "status": "downloading"
      },
      {
        "model_id": "model_456",
        "progress": 100,
        "status": "stopped"
      }
    ]
    ```
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
    
    **Description:** 
    Initiates model downloads with validation and token checking. 
    The request body can be a single model entry object or a list of model entry objects.
    
    **Parameters:**
    - `request` (Request): HTTP request with a model entry or a list of entries in the body.
    - `background_tasks` (BackgroundTasks): FastAPI background task queue.
    - `user` (str): Authenticated user from JWT token.
    
    **Returns:** 
    A single result object or a list of result objects with the download status.
    
    **Example response (single):**
    ```json
    {
      "ok": true
    }
    ```
    
    **Example response (list):**
    ```json
    [
      {
        "ok": true
      },
      {
        "ok": false,
        "msg": "HuggingFace token required for this download"
      }
    ]
    ```
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
    
    **Description:** 
    Cancels an active download and cleans up partial files.
    The request body must contain the model information to identify the download to stop.
    
    **Parameters:**
    - `entry` (dict): Model information to identify the download.
    - `user` (str): Authenticated user from JWT token.
    
    **Returns:** 
    A dictionary with the operation status and a message.
    
    **Example response (success):**
    ```json
    {
      "ok": true,
      "msg": "Stop requested"
    }
    ```

    **Example response (failure):**
    ```json
    {
      "ok": false,
      "msg": "No active download for this model"
    }
    ```
    """
    return DownloadService.stop_download(entry)


@download_router.post("/progress")
def get_progress(entry: dict = Body(...), user=Depends(protected)):
    """
    Returns download progress for a specific model.
    
    **Description:** 
    Retrieves the current download progress for a specific model.
    The request body must contain the model information to identify the download.
    
    **Parameters:**
    - `entry` (dict): Model information to identify the download.
    - `user` (str): Authenticated user from JWT token.
    
    **Returns:** 
    A dictionary containing the progress percentage and status.
    
    **Example response:**
    ```json
    {
      "progress": 75,
      "status": "downloading"
    }
    ```
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
    
    **Description:** 
    Removes model files with deduplication and validation.
    The request body can be a single model entry object or a list of model entry objects.
    
    **Parameters:**
    - `request` (Request): HTTP request with a model entry or a list of entries in the body.
    - `user` (str): Authenticated user from JWT token.
    
    **Returns:** 
    A single result object or a list of result objects with the deletion status.
    
    **Example response (single):**
    ```json
    {
      "ok": true
    }
    ```
    
    **Example response (list):**
    ```json
    [
      {
        "ok": true
      },
      {
        "ok": false,
        "msg": "File not found: /path/to/model"
      }
    ]
    ```
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
