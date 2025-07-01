import json
import os
from typing import Any, Dict
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

class ConfigService:
    """
    Configuration management service following Single Responsibility Principle.
    
    **Purpose:** Handles all configuration-related operations including:
    - Loading and saving user configuration files
    - Managing configuration paths and directories
    - Configuration validation and defaults
    - Environment variable resolution
    
    **SRP Responsibility:** Configuration management and validation.
    This class should NOT handle model operations (use ModelManager) or
    download operations (use DownloadService).
    """

    def __init__(self):
        self.config = {}

    @staticmethod
    def save_user_config(config: Dict[str, Any]) -> None:
        """
        Saves the user configuration to config.json.
        Invalidates cache after saving.
        
        **Description:** Saves user configuration to config.json and invalidates cache.
        **Parameters:**
        - `config` (Dict[str, Any]): Configuration data to save
        **Returns:** None
        """
        config_path = ConfigService.get_user_config_path()
        logger.debug(f"Saving user configuration to: {config_path}")
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"User configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Error saving {config_path}: {e}")
            raise Exception(f"Error saving configuration: {str(e)}")

    @staticmethod
    def get_user_config_path() -> str:
        """
        Returns the path to the user's custom config.json file.
        This file is not in the git repository and won't be overwritten during updates.
        
        **Description:** Constructs the path to the user's configuration file.
        **Parameters:** None
        **Returns:** str containing the path to config.json
        """
        # The config.json file is placed in the current application directory
        current_dir = os.path.abspath(os.getcwd())
        logger.debug(f"Current directory for config.json: {current_dir}")
        return os.path.join(current_dir, "config.json")
        

    @staticmethod
    def load_user_config() -> Dict[str, Any]:
        """
        Loads the user's custom config.json file.
        Returns an empty dictionary if the file doesn't exist.
        
        **Description:** Loads user configuration from config.json file.
        **Parameters:** None
        **Returns:** Dict containing user configuration data
        """
        config_path = ConfigService.get_user_config_path()
        if not os.path.exists(config_path):
            logger.debug("User config.json file not found")
            return {}
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"User configuration loaded from: {config_path}")
            return data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading {config_path}: {e}")
            return {}

    @staticmethod
    def get_env_file_path() -> str:
        """
        Returns the .env file path: ${BASE_DIR}/.env
        
        **Description:** Constructs the path to the environment file.
        **Parameters:** None
        **Returns:** str containing the path to the .env file
        """
        base_dir = ConfigService.get_base_dir()
        return os.path.join(base_dir, ".env")
    
    @staticmethod
    def get_workflows_dir() -> str:
        """
        Returns the workflows directory: ${BASE_DIR}/user/default/workflows
        
        **Description:** Constructs the path to the workflows directory.
        **Parameters:** None
        **Returns:** str containing the path to the workflows directory
        """
        base_dir = ConfigService.get_base_dir()
        workflows_dir = os.path.join(base_dir, "user", "default", "workflows")
        return workflows_dir
    
    @staticmethod
    def get_models_dir() -> str:
        """
        Returns the models directory: ${BASE_DIR}/models
        
        **Description:** Constructs the path to the models directory.
        **Parameters:** None
        **Returns:** str containing the path to the models directory
        """
        base_dir = ConfigService.get_base_dir()
        models_dir = os.path.join(base_dir, "models")
        return models_dir
    
    @staticmethod
    def get_bundles_dir() -> str:
        """
        Return the bundles directory path.
        
        **Description:** Constructs the normalized path to the bundles directory.
        **Parameters:** None
        **Returns:** str containing the path to the bundles directory
        """
        base_dir = ConfigService.get_base_dir()
        bundles_dir = os.path.join(base_dir, "bundles")
        # Normalize path to avoid double backslashes
        bundles_dir = os.path.normpath(bundles_dir)
        return bundles_dir
        
    @staticmethod
    def get_base_dir(default_value : str = None) -> str:
        """
        Returns the base directory (BASE_DIR) according to priority:
        1. config.json file (created by user)
        2. BASE_DIR environment variable
        3. models.json config.BASE_DIR value
        4. COMFYUI_MODEL_DIR environment variable
        5. Current directory
        
        **Description:** Determines the base directory for the ComfyUI installation using multiple fallback sources.
        **Parameters:** None
        **Returns:** str containing the absolute path to the base directory
        """
        base_dir = None
        
        # Priority 1: Custom config.json file (resistant to git pull)
        try:
            user_config = ConfigService.load_user_config()
            config_base_dir = user_config.get("BASE_DIR", "")
            if config_base_dir:
                logger.debug(f"Using BASE_DIR from config.json: {config_base_dir}")
                base_dir = config_base_dir
        except Exception:
            logger.debug("Unable to read BASE_DIR from config.json")

        # Priority 2: BASE_DIR environment variable
        if not base_dir:
            env_base_dir = os.environ.get("BASE_DIR")
            if env_base_dir:
                logger.debug(f"Using BASE_DIR from environment variable: {env_base_dir}")
                base_dir = env_base_dir
        
        # Priority 3: models.json value (without using cache to avoid recursion)
        if not base_dir and default_value:
            try:
                if default_value and os.path.exists(default_value):
                    with open(default_value, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    config_base_dir = data.get("config", {}).get("BASE_DIR", "")
                    if config_base_dir:
                        logger.debug(f"Using BASE_DIR from models.json: {config_base_dir}")
                        base_dir = config_base_dir
            except Exception:
                logger.debug("Unable to read BASE_DIR from models.json")
        
        # Priority 4: COMFYUI_MODEL_DIR environment variable
        if not base_dir:
            comfy_dir = os.environ.get("COMFYUI_MODEL_DIR")
            if comfy_dir:
                logger.debug(f"Using COMFYUI_MODEL_DIR: {comfy_dir}")
                base_dir = comfy_dir
        
        # Priority 5: Current directory
        if not base_dir:
            base_dir = os.getcwd()
            logger.debug(f"Using current directory: {base_dir}")
        return base_dir
    