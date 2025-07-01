from fastapi import APIRouter, HTTPException, Depends
from back.services.auth_service import AuthService
from back.models.auth_models import LoginRequest, ChangeUserRequest
from back.services.auth_middleware import protected

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
