from fastapi import APIRouter
from .auth_router import auth_router
from .token_router import token_router
from .download_router import download_router
from .model_router import model_router
from .model_groups_router import model_groups_router
from .model_entries_router import model_entries_router
from .bundle_router import router as bundle_router
from .file_manager_router import router as file_manager_router
from .json_models_router import router as json_models_router
from .workflow_router import router as workflow_router

# Main API router that combines all sub-routers
api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, tags=["Authentication"])
api_router.include_router(token_router, tags=["Tokens"])
api_router.include_router(download_router, tags=["Downloads"])
api_router.include_router(model_router, tags=["Models"])
api_router.include_router(model_groups_router, tags=["Model Groups"])
api_router.include_router(model_entries_router, tags=["Model Entries"])
api_router.include_router(bundle_router, tags=["Bundles"])
api_router.include_router(file_manager_router, tags=["File Manager"])
api_router.include_router(json_models_router, tags=["JSON Models"])
api_router.include_router(workflow_router, tags=["Workflows"])
