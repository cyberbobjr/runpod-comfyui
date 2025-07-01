from fastapi import APIRouter, HTTPException, Depends
from back.services.auth_service import AuthService
from back.models.auth_models import LoginRequest, ChangeUserRequest, TokenConfig
from back.services.auth_middleware import protected
from back.services.token_service import TokenService
from back.version import get_version_info

# Router
auth_router = APIRouter(prefix="/api/auth")


@auth_router.post("/login")
def login(req: LoginRequest):
    """
    User login endpoint.
    
    **Description:** Authenticates user credentials and returns a JWT token.
    **Parameters:**
    - `req` (LoginRequest): Login request containing username and password
    **Returns:** Dict containing the JWT token
    """
    if AuthService.verify_user(req.username, req.password):
        token = AuthService.create_jwt(req.username)
        return {"token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@auth_router.post("/change_user")
def change_user(req: ChangeUserRequest, user=Depends(protected)):
    """
    Change user credentials endpoint.
    
    **Description:** Allows users to change their username and password.
    **Parameters:**
    - `req` (ChangeUserRequest): Request containing old and new credentials
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict with success status
    """
    AuthService.change_user_credentials(
        req.old_username, req.old_password, 
        req.new_username, req.new_password
    )
    return {"ok": True}


@auth_router.post("/tokens")
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


@auth_router.get("/tokens")
def get_tokens(user=Depends(protected)):
    """
    Retrieves currently configured API tokens from the .env file.
    
    **Description:** Gets stored authentication tokens for external services.
    **Parameters:**
    - `user` (str): Authenticated user from JWT token
    **Returns:** Dict containing HF and CivitAI tokens
    """
    return TokenService.get_tokens()


@auth_router.get("/version")
async def get_version_endpoint():
    """
    Get application version information.
    This endpoint is publicly accessible and doesn't require authentication.
    
    **Description:** Returns version information for the application.
    **Parameters:** None
    **Returns:** Dict containing version information
    """
    return get_version_info()
