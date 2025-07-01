
from fastapi import APIRouter, Depends
from back.services.model_management_service import ModelManagementService
from back.services.auth_middleware import protected

# Router
model_router = APIRouter(prefix="/api/models")


@model_router.get("/")
def get_models_data(user=Depends(protected)):
    """
    Retrieves the complete models.json file including configuration, model groups, and bundles.
    
    **Description:** Returns comprehensive model data with existence status and download progress.
    **Parameters:**
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict containing config, groups, bundles with status information
    """
    return ModelManagementService.get_complete_models_data()


