from pydantic import BaseModel, Field
from typing import Optional


class TokenConfig(BaseModel):
    """
    Configuration model for external API tokens.
    
    **Description:** Defines the structure for API authentication tokens
    used to access external services like HuggingFace and CivitAI.
    """
    hf_token: Optional[str] = Field(None, description="HuggingFace API token for model downloads")
    civitai_token: Optional[str] = Field(None, description="CivitAI API token for model downloads")


class LoginRequest(BaseModel):
    """
    User login request model.
    
    **Description:** Defines the structure for user authentication requests.
    """
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")


class ChangeUserRequest(BaseModel):
    """
    Change user credentials request model.
    
    **Description:** Defines the structure for changing user credentials.
    """
    old_username: str = Field(..., description="Current username")
    old_password: str = Field(..., description="Current password")
    new_username: str = Field(..., description="New username")
    new_password: str = Field(..., description="New password")
