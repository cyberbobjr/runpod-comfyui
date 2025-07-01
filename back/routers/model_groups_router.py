from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any
from back.services.auth_middleware import protected
from back.services.model_management_service import ModelManagementService
from back.models.model_models import (
    ModelGroupRequest, 
    UpdateModelGroupRequest, 
    ModelEntryRequest,
    ModelEntry
)

# Router for model group operations
model_groups_router = APIRouter(prefix="/api/models/groups")


@model_groups_router.get("/", response_model=List[str])
def get_groups(user=Depends(protected)):
    """
    Retrieves the list of all existing model groups.
    
    **Description:** Gets all model group names for organization and management.
    **Parameters:**
    - `user` (str): Authenticated user from JWT token
    **Returns:** List of group names
    """
    return ModelManagementService.get_groups()


@model_groups_router.post("/")
def create_group(group_request: ModelGroupRequest, user=Depends(protected)):
    """
    Creates a new empty model group.
    
    **Description:** Creates a new group to organize models by category.
    **Parameters:**
    - `group_request` (ModelGroupRequest): Group creation request
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict with success status and message
    """
    try:
        ModelManagementService.create_group(group_request.group)
        return {"ok": True, "message": f"Group '{group_request.group}' created"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@model_groups_router.put("/")
def update_group_name(update_request: UpdateModelGroupRequest, user=Depends(protected)):
    """
    Renames an existing model group and updates all bundle references.
    
    **Description:** Renames a group while preserving all models and bundle references.
    **Parameters:**
    - `update_request` (UpdateModelGroupRequest): Group rename request
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict with success status and message
    """
    try:
        ModelManagementService.rename_group(update_request.old_group, update_request.new_group)
        return {"ok": True, "message": f"Group renamed from '{update_request.old_group}' to '{update_request.new_group}'"}
    except ValueError as e:
        if "does not exist" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))


@model_groups_router.delete("/")
def delete_group(group_request: ModelGroupRequest, user=Depends(protected)):
    """
    Deletes a model group if it's not referenced by any bundles.
    
    **Description:** Removes an unused model group from the configuration.
    **Parameters:**
    - `group_request` (ModelGroupRequest): Group deletion request
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict with success status and message
    """
    try:
        ModelManagementService.delete_group(group_request.group)
        return {"ok": True, "message": f"Group '{group_request.group}' deleted"}
    except ValueError as e:
        if "does not exist" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))


@model_groups_router.get("/{group_name}", response_model=List[ModelEntry])
def get_group_models(group_name: str, user=Depends(protected)):
    """
    Retrieves all model entries for a specific group.
    
    **Description:** Gets all models in a specific group for display or processing.
    **Parameters:**
    - `group_name` (str): Name of the group
    - `user` (str): Authenticated user from JWT token
    **Returns:** List of model entries
    """
    try:
        return ModelManagementService.get_group_models(group_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
