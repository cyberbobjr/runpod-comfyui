from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth_service import AuthService

# Security
security = HTTPBearer()


def protected(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Protected route dependency.
    
    **Description:** FastAPI dependency that validates JWT tokens for protected routes.
    **Parameters:**
    - `credentials` (HTTPAuthorizationCredentials): The authorization header credentials
    **Returns:** str containing the authenticated username
    """
    token = credentials.credentials
    user = AuthService.decode_jwt(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user
