from fastapi import APIRouter, Depends
from back.services.token_service import TokenService
from back.models.auth_models import TokenConfig
from back.services.auth_middleware import protected

# Router
token_router = APIRouter(prefix="/api/tokens")


@token_router.post("/")
def set_tokens(cfg: TokenConfig, user=Depends(protected)):
    """
    Sets API tokens in the .env file.
    
    **Description:** Stores HuggingFace and CivitAI tokens for authenticated downloads.
    **Parameters:**
    - `cfg` (TokenConfig): Token configuration containing HF and CivitAI tokens
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict with success status
    """
    TokenService.set_tokens(cfg.hf_token, cfg.civitai_token)
    return {"ok": True}


@token_router.get("/")
def get_tokens(user=Depends(protected)):
    """
    Returns API tokens stored in the .env file.
    
    **Description:** Retrieves stored authentication tokens for external services.
    **Parameters:**
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict containing HF and CivitAI tokens
    """
    return TokenService.get_tokens()
