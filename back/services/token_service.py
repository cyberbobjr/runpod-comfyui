import os
from typing import Dict, Optional, Tuple
from .model_manager import ModelManager
from .config_service import ConfigService
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Constants
ENV_FILE = ".env"


class TokenService:
    """
    API token management service following Single Responsibility Principle.
    
    **Purpose:** Handles external API authentication tokens including:
    - HuggingFace token management
    - CivitAI token management
    - Environment file operations (.env)
    - Token validation and persistence
    - Secure token storage and retrieval
    
    **SRP Responsibility:** External API token management.
    This service should NOT handle user authentication (use AuthService) or
    model operations (use ModelManager).
    """
    
    @staticmethod
    def get_env_file_path() -> str:
        """
        Returns the full path of the .env file according to COMFYUI_MODEL_DIR or current directory.
        
        **Description:** Constructs the path to the environment file.
        **Parameters:** None
        **Returns:** str containing the path to the .env file
        """
        return ConfigService.get_env_file_path()

    @staticmethod
    def write_env_file(hf_token: Optional[str], civitai_token: Optional[str]) -> None:
        """
        Writes tokens to the .env file.
        
        **Description:** Saves authentication tokens to the environment file.
        **Parameters:**
        - `hf_token` (Optional[str]): HuggingFace token to save
        - `civitai_token` (Optional[str]): CivitAI token to save
        **Returns:** None
        """
        lines = []
        if hf_token is not None:
            lines.append(f"HF_TOKEN={hf_token}")
        if civitai_token is not None:
            lines.append(f"CIVITAI_TOKEN={civitai_token}")
        env_path = ConfigService.get_env_file_path()
        os.makedirs(os.path.dirname(env_path), exist_ok=True)
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    @staticmethod
    def read_env_file() -> Tuple[Optional[str], Optional[str]]:
        """
        Reads tokens from the .env file.
        
        **Description:** Loads authentication tokens from the environment file.
        **Parameters:** None
        **Returns:** Tuple of (hf_token, civitai_token) strings or None values
        """
        hf_token = None
        civitai_token = None
        env_path = ConfigService.get_env_file_path()
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("HF_TOKEN="):
                        hf_token = line.strip().split("=", 1)[1]
                    elif line.startswith("CIVITAI_TOKEN="):
                        civitai_token = line.strip().split("=", 1)[1]
        return hf_token, civitai_token

    @staticmethod
    def set_tokens(hf_token: Optional[str], civitai_token: Optional[str]) -> bool:
        """
        Sets API tokens in the .env file.
        
        **Description:** Stores HuggingFace and CivitAI tokens for authenticated downloads.
        **Parameters:**
        - `hf_token` (Optional[str]): HuggingFace token to store
        - `civitai_token` (Optional[str]): CivitAI token to store
        **Returns:** bool indicating success
        """
        TokenService.write_env_file(hf_token, civitai_token)
        return True

    @staticmethod
    def get_tokens() -> Dict[str, Optional[str]]:
        """
        Returns API tokens stored in the .env file.
        
        **Description:** Retrieves stored authentication tokens for external services.
        **Parameters:** None
        **Returns:** Dict containing HF and CivitAI tokens
        """
        hf_token, civitai_token = TokenService.read_env_file()
        return {"hf_token": hf_token, "civitai_token": civitai_token}
