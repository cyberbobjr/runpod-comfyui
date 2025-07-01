from fastapi import APIRouter, HTTPException, Depends
from back.services.auth_middleware import protected
from back.services.model_management_service import ModelManagementService
from back.models.model_models import ModelEntryRequest, DeleteModelRequest

# Router for model entry operations
model_entries_router = APIRouter(prefix="/api/models/entries")


@model_entries_router.post("/")
def add_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """
    Adds a new model entry to a specific group.
    
    **Description:** Adds a new model with validation and conflict checking.
    **Parameters:**
    - `entry_request` (ModelEntryRequest): Model entry creation request
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict with success status and message
    """
    try:
        ModelManagementService.add_model_entry(
            entry_request.group, 
            entry_request.entry.dict(exclude_none=True)
        )
        return {"ok": True, "message": "Model entry added successfully"}
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))


@model_entries_router.put("/")
def update_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """
    Updates an existing model entry or adds it if it doesn't exist.
    
    **Description:** Updates a model's properties or creates it if not found.
    **Parameters:**
    - `entry_request` (ModelEntryRequest): Model entry update request
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict with success status and message
    """
    try:
        was_updated = ModelManagementService.update_model_entry(
            entry_request.group, 
            entry_request.entry.dict(exclude_none=True)
        )
        message = "Model entry updated" if was_updated else "Model entry added"
        return {"ok": True, "message": message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@model_entries_router.delete("/")
def delete_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """
    Removes a model entry from a group.
    
    **Description:** Deletes a model entry from the configuration.
    **Parameters:**
    - `entry_request` (ModelEntryRequest): Model entry deletion request
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict with success status and message
    """
    try:
        ModelManagementService.delete_model_entry(
            entry_request.group, 
            entry_request.entry.dict(exclude_none=True)
        )
        return {"ok": True, "message": "Model entry deleted successfully"}
    except ValueError as e:
        if "does not exist" in str(e) or "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))


@model_entries_router.delete("/file")
def delete_model_file(delete_request: DeleteModelRequest, user=Depends(protected)):
    """
    Deletes a model file from disk.
    
    **Description:** Removes the actual model file from the filesystem.
    **Parameters:**
    - `delete_request` (DeleteModelRequest): Model file deletion request
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict with success status and message
    """
    try:
        ModelManagementService.delete_model_file(delete_request.entry.dict(exclude_none=True))
        return {"ok": True, "message": "Model file deleted successfully"}
    except ValueError as e:
        if "does not exist" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
