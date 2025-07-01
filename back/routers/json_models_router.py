"""
JSON Models Router - Handle JSON model management API routes

This module contains all API routes for JSON model management including:
- Configuration management
- Group operations and ordering  
- Model entry management
- Path normalization
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any

from ..services.auth_middleware import protected
from ..services.json_models_service import JsonModelsService
from ..models.json_models import (
    ConfigResponse, ConfigUpdateRequest, GroupOrderRequest, 
    GroupOrderResponse, ModelsDataResponse
)
from ..models.model_models import (
    ModelEntry, ModelEntryRequest, ModelGroupRequest, 
    UpdateModelGroupRequest
)
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/jsonmodels", tags=["json-models"])

# Initialize service
json_models_service = JsonModelsService()


@router.get("/", response_model=ModelsDataResponse)
def get_models_data(user=Depends(protected)):
    """
    GET /api/jsonmodels/
    
    Retrieves the complete models.json file with existence check for each model.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: ModelsDataResponse containing config, groups with existence flags
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading models.json file
    
    Usage: Main endpoint to get current state of all models with disk existence.
    """
    try:
        data = json_models_service.get_models_data_with_existence()
        return ModelsDataResponse(
            config=data.get("config", {}),
            groups=data.get("groups", {}),
            bundles=data.get("bundles")
        )
    except Exception as e:
        logger.error(f"Error getting models data: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving models data: {str(e)}")


@router.get("/config", response_model=ConfigResponse)
def get_config(user=Depends(protected)):
    """
    GET /api/jsonmodels/config
    
    Retrieves the current configuration including user-specific BASE_DIR.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: ConfigResponse with BASE_DIR and source information
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading configuration
    
    Usage: Get current BASE_DIR configuration and its source.
    """
    try:
        config_info = json_models_service.get_config_info()
        return ConfigResponse(**config_info)
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving config: {str(e)}")


@router.post("/config")
def update_config(config: ConfigUpdateRequest, user=Depends(protected)):
    """
    POST /api/jsonmodels/config
    
    Updates the BASE_DIR in user-specific config.json.
    
    Arguments:
    - config (ConfigUpdateRequest): Configuration update with base_dir
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Success response with confirmation message
    
    Possible errors:
    - 401: Not authenticated
    - 400: Invalid base directory path
    - 500: Error updating configuration
    
    Usage: Update BASE_DIR configuration in user config file.
    """
    try:
        result = json_models_service.update_config(config.base_dir)
        return result
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating config: {str(e)}")


@router.get("/groups", response_model=List[str])
def get_groups(user=Depends(protected)):
    """
    GET /api/jsonmodels/groups
    
    Retrieves the list of all existing model groups in order.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Array of group names in current order
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading models.json file
    
    Usage: Get all available model group names in their display order.
    """
    try:
        groups = json_models_service.get_groups_list()
        return groups
    except Exception as e:
        logger.error(f"Error getting groups: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving groups: {str(e)}")


@router.post("/groups")
def create_group(group_request: ModelGroupRequest, user=Depends(protected)):
    """
    POST /api/jsonmodels/groups
    
    Creates a new empty model group.
    
    Arguments:
    - group_request (ModelGroupRequest): Group creation request with group name
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Success response with confirmation message
    
    Possible errors:
    - 401: Not authenticated
    - 400: Group name already exists or invalid format
    - 500: Error writing to models.json file
    
    Usage: Create a new group to organize models by category.
    """
    try:
        result = json_models_service.create_group(group_request.group)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating group: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating group: {str(e)}")


@router.put("/groups")
def update_group_name(update_request: UpdateModelGroupRequest, user=Depends(protected)):
    """
    PUT /api/jsonmodels/groups
    
    Renames an existing model group and updates all references.
    
    Arguments:
    - update_request (UpdateModelGroupRequest): Group rename request
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Success response with confirmation message
    
    Possible errors:
    - 401: Not authenticated
    - 404: Old group name does not exist
    - 400: New group name already exists
    - 500: Error writing to models.json file
    
    Usage: Rename a model group while preserving all models and references.
    """
    try:
        result = json_models_service.update_group_name(
            update_request.old_group, 
            update_request.new_group
        )
        return result
    except ValueError as e:
        status_code = 404 if "does not exist" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating group name: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating group: {str(e)}")


@router.delete("/groups")
def delete_group(group_request: ModelGroupRequest, user=Depends(protected)):
    """
    DELETE /api/jsonmodels/groups
    
    Deletes a model group if it's not referenced by any bundles.
    
    Arguments:
    - group_request (ModelGroupRequest): Group deletion request
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Success response with confirmation message
    
    Possible errors:
    - 401: Not authenticated
    - 404: Group does not exist
    - 400: Group is used in bundles (cannot delete)
    - 500: Error writing to models.json file
    
    Usage: Remove an empty or unused model group.
    """
    try:
        result = json_models_service.delete_group(group_request.group)
        return result
    except ValueError as e:
        status_code = 404 if "does not exist" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting group: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting group: {str(e)}")


@router.get("/group/{group_name}", response_model=List[ModelEntry])
def get_group_models(group_name: str, user=Depends(protected)):
    """
    GET /api/jsonmodels/group/{group_name}
    
    Retrieves all model entries for a specific group.
    
    Arguments:
    - group_name (str): Name of the group (in URL path)
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Array of ModelEntry objects
    
    Possible errors:
    - 401: Not authenticated
    - 404: Group does not exist
    - 500: Error reading models.json file
    
    Usage: Get all models in a specific group for display or processing.
    """
    try:
        models = json_models_service.get_group_models(group_name)
        return models
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting group models: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving group models: {str(e)}")


@router.post("/entry")
def add_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """
    POST /api/jsonmodels/entry
    
    Adds a new model entry to a specific group with path normalization.
    
    Arguments:
    - entry_request (ModelEntryRequest): Model entry creation request
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Success response with confirmation message
    
    Possible errors:
    - 401: Not authenticated
    - 400: Missing URL/git, invalid destination, or duplicate model
    - 409: Model with same destination already exists
    - 500: Error writing to models.json file
    
    Usage: Add a new model to a group with automatic path normalization.
    """
    try:
        entry_dict = entry_request.entry.dict(exclude_none=True)
        result = json_models_service.add_model_entry(entry_request.group, entry_dict)
        return result
    except ValueError as e:
        status_code = 409 if "already exists" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding model entry: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding model entry: {str(e)}")


@router.put("/entry")
def update_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """
    PUT /api/jsonmodels/entry
    
    Updates an existing model entry or adds it if it doesn't exist.
    
    Arguments:
    - entry_request (ModelEntryRequest): Model entry update request
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Success response indicating whether entry was updated or added
    
    Possible errors:
    - 401: Not authenticated
    - 400: Missing destination/git identifier
    - 500: Error writing to models.json file
    
    Usage: Update an existing model's properties or add a new one if not found.
    """
    try:
        entry_dict = entry_request.entry.dict(exclude_none=True)
        result = json_models_service.update_model_entry(entry_request.group, entry_dict)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating model entry: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating model entry: {str(e)}")


@router.delete("/entry")
def delete_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """
    DELETE /api/jsonmodels/entry
    
    Removes a model entry from a group.
    
    Arguments:
    - entry_request (ModelEntryRequest): Model entry deletion request
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Success response with confirmation message
    
    Possible errors:
    - 401: Not authenticated
    - 404: Group or model not found
    - 400: Cannot identify model to delete
    - 500: Error writing to models.json file
    
    Usage: Remove a model entry from the configuration.
    """
    try:
        entry_dict = entry_request.entry.dict(exclude_none=True)
        result = json_models_service.delete_model_entry(entry_request.group, entry_dict)
        return result
    except ValueError as e:
        status_code = 404 if "not found" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting model entry: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting model entry: {str(e)}")


@router.get("/group-order", response_model=GroupOrderResponse)
def get_group_order(user=Depends(protected)):
    """
    GET /api/jsonmodels/group-order
    
    Retrieves the current order of model groups.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: GroupOrderResponse with ordered group names
    
    Possible errors:
    - 401: Not authenticated
    - 500: Error reading models.json file
    
    Usage: Get the current display order of model groups.
    """
    try:
        order = json_models_service.get_group_order()
        return GroupOrderResponse(order=order)
    except Exception as e:
        logger.error(f"Error getting group order: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving group order: {str(e)}")


@router.put("/group-order")
def set_group_order(order_request: GroupOrderRequest, user=Depends(protected)):
    """
    PUT /api/jsonmodels/group-order
    
    Sets the order of model groups for display.
    
    Arguments:
    - order_request (GroupOrderRequest): New group order
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Success response with confirmation message and new order
    
    Possible errors:
    - 401: Not authenticated
    - 400: Invalid group order (missing or unknown groups)
    - 500: Error writing to models.json file
    
    Usage: Update the display order of model groups.
    """
    try:
        result = json_models_service.set_group_order(order_request.order)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting group order: {e}")
        raise HTTPException(status_code=500, detail=f"Error setting group order: {str(e)}")
