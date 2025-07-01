from fastapi import APIRouter, Depends
from back.services.model_service import ModelService
from back.services.model_management_service import ModelManagementService
from back.services.token_service import TokenService
from back.services.auth_middleware import protected
from back.version import get_version_info
from back.models.auth_models import TokenConfig

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


@model_router.get("/version")
async def get_version_endpoint():
    """
    Get application version information.
    This endpoint is publicly accessible and doesn't require authentication.
    
    **Description:** Returns version information for the application.
    **Parameters:** None
    **Returns:** Dict containing version information
    """
    return get_version_info()


@model_router.get("/total_size")
def total_size(user=Depends(protected)):
    """
    Returns the total size (in bytes) of the base_dir directory.
    
    **Description:** Calculates and returns the total disk space used by the ComfyUI installation.
    **Parameters:**
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict containing base directory path and total size
    """
    return ModelService.get_total_size()


@model_router.post("/tokens")
def set_tokens(cfg: TokenConfig, user=Depends(protected)):
    """
    Sets API tokens in the .env file for authenticated downloads.
    
    **Description:** Stores HuggingFace and CivitAI tokens for downloading from private repositories.
    **Parameters:**
    - `cfg` (TokenConfig): Token configuration
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict with success status
    """
    TokenService.set_tokens(cfg.hf_token, cfg.civitai_token)
    return {"ok": True}


@model_router.get("/tokens")
def get_tokens(user=Depends(protected)):
    """
    Retrieves currently configured API tokens from the .env file.
    
    **Description:** Gets stored authentication tokens for external services.
    **Parameters:**
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict containing HF and CivitAI tokens
    """
    return TokenService.get_tokens()
