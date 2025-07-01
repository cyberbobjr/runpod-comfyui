import os
import json
import shutil
import subprocess
import time
import copy
from typing import Dict, List, Any, Optional, Tuple
from fastapi import HTTPException

from .config_service import ConfigService
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

MODELS_JSON = "models.json"

class ModelManager:
    """
    Core model management service following Single Responsibility Principle.
    
    **Purpose:** Handles low-level model operations including:
    - Loading and caching models.json configuration
    - Path resolution and file system operations
    - Model existence validation
    - Git repository cloning
    - Basic model installation workflows
    
    **SRP Responsibility:** Model configuration management and basic file operations.
    This class should NOT handle HTTP downloads (use DownloadService) or 
    complex bundle operations (use BundleService).
    """
    
    # Cache to avoid repeated reloads
    _cache = {
        "models_json_data": None,
        "models_json_path": None,
        "base_dir": None,
        "last_load_time": 0,
        "cache_ttl": 30  # Cache valid for 30 seconds
    }
    
    @staticmethod
    def _is_cache_valid() -> bool:
        """
        Checks if the cache is still valid.
        
        **Description:** Verifies whether the current cache is within the TTL period.
        **Parameters:** None
        **Returns:** bool indicating if cache is valid
        """
        return (time.time() - ModelManager._cache["last_load_time"]) < ModelManager._cache["cache_ttl"]    
    
    @staticmethod
    def _clear_cache():
        """
        Clears the cache.
        
        **Description:** Resets all cached data to force fresh loading.
        **Parameters:** None
        **Returns:** None
        """
        ModelManager._cache["models_json_data"] = None
        ModelManager._cache["models_json_path"] = None
        ModelManager._cache["base_dir"] = None
        ModelManager._cache["last_load_time"] = 0
    

    
    @staticmethod
    def _find_models_json_path() -> str:
        """
        Internal method to find the models.json path without using cache.
        
        **Description:** Locates the models.json file path using the base directory.
        **Parameters:** None
        **Returns:** str containing the full path to models.json
        """
        base_dir = ConfigService.get_base_dir()
        return os.path.join(base_dir, MODELS_JSON)
    
    @staticmethod
    def get_installed_bundles_file() -> str:
        """
        Retourne le chemin du fichier installed_bundles.json
        
        **Description:** Constructs the path to the installed bundles tracking file.
        **Parameters:** None
        **Returns:** str containing the path to installed_bundles.json
        """
        bundles_dir = ConfigService.get_bundles_dir()
        return os.path.join(bundles_dir, "installed_bundles.json")

    @staticmethod
    def get_models_json_path() -> str:
        """
        Retourne le chemin complet du fichier models.json
        
        **Description:** Returns the complete path to the models.json file with caching.
        **Parameters:** None
        **Returns:** str containing the full path to models.json
        """
        # Vérifier le cache d'abord
        if ModelManager._is_cache_valid() and ModelManager._cache["models_json_path"]:
            return ModelManager._cache["models_json_path"]
        
        models_path = ModelManager._find_models_json_path()
        
        # Mettre en cache
        ModelManager._cache["models_json_path"] = models_path
        
        logger.debug(f"Chemin models.json déterminé: {models_path}")
        return models_path
    
    @staticmethod
    def load_models_json() -> Dict:
        """
        Charge le fichier models.json complet avec cache
        
        **Description:** Loads the complete models.json file with caching support.
        **Parameters:** None
        **Returns:** Dict containing the models.json data structure
        """
        # Vérifier le cache d'abord
        if ModelManager._is_cache_valid() and ModelManager._cache["models_json_data"]:
            logger.debug("Utilisation du cache pour models.json")
            return ModelManager._cache["models_json_data"]
        
        models_path = ModelManager.get_models_json_path()
        logger.debug(f"Chargement du fichier: {models_path}")
        
        if not os.path.exists(models_path):
            # Si le fichier n'existe pas, créer un fichier vide avec une structure de base
            try:
                logger.info(f"Création d'un fichier models.json vide à {models_path}")
                os.makedirs(os.path.dirname(models_path) or ".", exist_ok=True)
                empty_data = {"config": {"BASE_DIR": ConfigService.get_base_dir()}, "groups": {}}
                with open(models_path, "w", encoding="utf-8") as f:
                    json.dump(empty_data, f, indent=2)
                
                # Mettre en cache
                ModelManager._cache["models_json_data"] = empty_data
                ModelManager._cache["last_load_time"] = time.time()
                return empty_data
            except Exception as e:
                logger.error(f"Impossible de créer un fichier models.json vide: {str(e)}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Impossible de trouver ou créer le fichier models.json: {str(e)}"
                )
        
        try:
            with open(models_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Mettre en cache
            ModelManager._cache["models_json_data"] = data
            ModelManager._cache["last_load_time"] = time.time()
            
            logger.debug(f"Fichier models.json chargé avec succès depuis {models_path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Erreur de décodage JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture du fichier: {str(e)}")
    
    @staticmethod
    def _clean_exists_keys(data: Dict) -> Dict:
        """
        Remove 'exists' keys from model entries as they should be computed dynamically.
        
        **Description:** Recursively removes 'exists' keys from model data structure.
        **Parameters:**
        - `data` (Dict): The model data dictionary to clean
        **Returns:** Dict with 'exists' keys removed
        """
        cleaned_data = copy.deepcopy(data)
        
        # Remove exists keys from groups
        if "groups" in cleaned_data:
            for group_name, models in cleaned_data["groups"].items():
                if isinstance(models, list):
                    for model in models:
                        if isinstance(model, dict) and "exists" in model:
                            del model["exists"]
        
        return cleaned_data
    
    @staticmethod
    def save_models_json(data: Dict) -> None:
        """
        Sauvegarde le fichier models.json et invalide le cache
        
        **Description:** Saves the models.json file and invalidates the cache.
        **Parameters:**
        - `data` (Dict): The model data structure to save
        **Returns:** None
        """
        models_path = ModelManager.get_models_json_path()
        logger.debug(f"Sauvegarde du fichier: {models_path}")
        
        try:
            # Assurer que le répertoire existe
            os.makedirs(os.path.dirname(models_path) or ".", exist_ok=True)
            
            # Nettoyer les clés 'exists' avant sauvegarde
            cleaned_data = ModelManager._clean_exists_keys(data)
            
            with open(models_path, "w", encoding="utf-8") as f:
                json.dump(cleaned_data, f, indent=2)
            
            # Invalider le cache après sauvegarde
            ModelManager._clear_cache()
            
            logger.debug(f"Fichier models.json sauvegardé avec succès à {models_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde du fichier: {str(e)}")
    
    @staticmethod
    def resolve_path(path: str, base_dir: str) -> str:
        """
        Résout un chemin de fichier en tenant compte des variables comme ${BASE_DIR}
        et retourne le chemin absolu réel.
        
        **Description:** Resolves file paths by substituting variables like ${BASE_DIR}.
        **Parameters:**
        - `path` (str): The path to resolve
        - `base_dir` (str): The base directory for substitution
        **Returns:** str containing the resolved absolute path
        """
        if not path:
            return None
            
        if "${BASE_DIR}" in path:
            return path.replace("${BASE_DIR}", base_dir)
        
        return path
    
    @staticmethod
    def model_exists_on_disk(entry: Dict, base_dir: str = None) -> bool:
        """
        Vérifie si un modèle existe sur le disque.
        
        **Description:** Checks if a model file exists on the filesystem.
        **Parameters:**
        - `entry` (Dict): Model entry containing destination path
        - `base_dir` (str): Base directory for path resolution
        **Returns:** bool indicating if the model exists on disk
        """
        dest = entry.get("dest")
        if not dest:
            return False
            
        # Résoudre le chemin réel
        file_path = ModelManager.resolve_path(dest, base_dir)
        
        return os.path.exists(file_path)
    
    @staticmethod
    def clone_git_repo(entry: Dict, base_dir: str = None) -> Tuple[bool, str]:
        """
        Clone un dépôt git pour récupérer un modèle ou un plugin.
        Retourne (succès, message).
        
        **Description:** Clones a git repository to download a model or plugin.
        **Parameters:**
        - `entry` (Dict): Model entry containing git URL and destination
        - `base_dir` (str): Base directory for path resolution
        **Returns:** Tuple of (success bool, message string)
        """
        git_url = entry.get("git")
        dest = entry.get("dest")
        
        if not git_url:
            return False, "URL git manquante dans l'entrée"
        
        # Si dest est fourni, utiliser comme répertoire cible, sinon extraire du URL git
        if dest:
            target_dir = ModelManager.resolve_path(dest, base_dir)
        else:
            # Extraire le nom du repo de l'URL git
            repo_name = git_url.split("/")[-1].replace(".git", "")
            target_dir = os.path.join(base_dir or ".", repo_name)
        
        # Si le répertoire existe déjà, faire un pull au lieu d'un clone
        if os.path.exists(target_dir) and os.path.isdir(target_dir):
            try:
                logger.info(f"Mise à jour du dépôt git: {target_dir}")
                # Se déplacer dans le répertoire et faire un pull
                original_dir = os.getcwd()
                os.chdir(target_dir)
                result = subprocess.run(["git", "pull"], capture_output=True, text=True)
                os.chdir(original_dir)
                
                if result.returncode == 0:
                    logger.info(f"Dépôt git mis à jour avec succès: {target_dir}")
                    return True, f"Dépôt git mis à jour avec succès: {os.path.basename(target_dir)}"
                else:
                    logger.warning(f"Erreur lors de la mise à jour du dépôt: {result.stderr}")
                    return False, f"Erreur lors de la mise à jour du dépôt: {result.stderr}"
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour du dépôt git: {str(e)}")
                return False, f"Erreur lors de la mise à jour du dépôt git: {str(e)}"
        else:
            # Créer le répertoire parent si nécessaire
            os.makedirs(os.path.dirname(target_dir), exist_ok=True)
            
            try:
                logger.info(f"Clonage du dépôt git: {git_url} -> {target_dir}")
                result = subprocess.run(["git", "clone", git_url, target_dir], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"Dépôt git cloné avec succès: {target_dir}")
                    return True, f"Dépôt git cloné avec succès: {os.path.basename(target_dir)}"
                else:
                    logger.warning(f"Erreur lors du clonage du dépôt: {result.stderr}")
                    return False, f"Erreur lors du clonage du dépôt: {result.stderr}"
            except Exception as e:
                logger.error(f"Erreur lors du clonage du dépôt git: {str(e)}")
                return False, f"Erreur lors du clonage du dépôt git: {str(e)}"
    
    @staticmethod
    def filter_models_by_tags(models: List[Dict], include_tags: List[str], exclude_tags: List[str]) -> List[Dict]:
        """
        Filtre une liste de modèles en fonction des tags à inclure et à exclure.
        
        **Description:** Filters a list of models based on include and exclude tag criteria.
        **Parameters:**
        - `models` (List[Dict]): List of model dictionaries to filter
        - `include_tags` (List[str]): Tags that must be present
        - `exclude_tags` (List[str]): Tags that must not be present
        **Returns:** List[Dict] containing filtered models
        """
        result = []
        
        for model in models:
            model_tags = set(model.get("tags", []))
            
            # Si aucun tag n'est spécifié, accepter le modèle par défaut
            if not include_tags and not exclude_tags:
                result.append(model)
                continue
            
            # Si des tags d'inclusion sont spécifiés, vérifier si au moins un tag correspond
            include_match = not include_tags or any(tag in model_tags for tag in include_tags)
            
            # Si des tags d'exclusion sont spécifiés, vérifier qu'aucun ne correspond
            exclude_match = exclude_tags and any(tag in model_tags for tag in exclude_tags)
            
            # Inclure le modèle s'il correspond aux critères
            if include_match and not exclude_match:
                result.append(model)
        
        return result
    
    @staticmethod
    def copy_workflow_to_comfyui(workflow_name: str) -> Tuple[bool, str]:
        """
        Copie un fichier de workflow depuis le répertoire de workflows vers le répertoire de workflows ComfyUI.
        Retourne (succès, message).
        
        **Description:** Copies a workflow file from the workflows directory to the ComfyUI workflows directory.
        **Parameters:**
        - `workflow_name` (str): Name of the workflow file to copy
        **Returns:** Tuple of (success bool, message string)
        """
        workflows_dir = ConfigService.get_workflows_dir()
        source_path = os.path.join(workflows_dir, workflow_name)
        
        # Le répertoire ComfyUI est dans BASE_DIR/ComfyUI/workflows
        base_dir = ConfigService.get_base_dir()
        comfy_workflows_dir = os.path.join(base_dir, "ComfyUI", "workflows")
        dest_path = os.path.join(comfy_workflows_dir, workflow_name)
        
        # Vérifier que le fichier source existe
        if not os.path.exists(source_path):
            return False, f"Le fichier workflow '{workflow_name}' n'existe pas"
        
        try:
            # Créer le répertoire de destination s'il n'existe pas
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Copier le fichier
            shutil.copy2(source_path, dest_path)
            logger.info(f"Workflow copié avec succès: {source_path} -> {dest_path}")
            return True, f"Workflow '{workflow_name}' copié avec succès vers ComfyUI"
        except Exception as e:
            logger.error(f"Erreur lors de la copie du workflow: {str(e)}")
            return False, f"Erreur lors de la copie du workflow: {str(e)}"
    
    @staticmethod
    def install_models_for_bundle(bundle_data: Dict, profile: str) -> Dict[str, List[str]]:
        """
        Installe tous les modèles nécessaires pour un bundle en fonction du profil matériel.
        Retourne un rapport d'installation avec les modèles installés et les erreurs.
        
        **Description:** Installs all necessary models for a bundle based on hardware profile.
        **Parameters:**
        - `bundle_data` (Dict): Bundle configuration data
        - `profile` (str): Hardware profile name
        **Returns:** Dict containing installation report with installed models and errors
        """
        # Charger les données du fichier models.json
        models_json_data = ModelManager.load_models_json()
        base_dir = ConfigService.get_base_dir()
        
        # Obtenir les filtres de modèles pour le profil
        if profile not in bundle_data.get("hardware_profiles", {}):
            raise HTTPException(status_code=404, detail=f"Profil matériel '{profile}' non trouvé dans le bundle")
        
        profile_data = bundle_data["hardware_profiles"][profile]
        include_tags = profile_data.get("model_filters", {}).get("include_tags", [])
        exclude_tags = profile_data.get("model_filters", {}).get("exclude_tags", [])
        
        # Rapport d'installation
        report = {
            "installed": [],
            "already_exists": [],
            "errors": [],
            "skipped": []
        }
        
        # Pour chaque groupe de modèles dans le bundle
        for group_name in bundle_data.get("models", []):
            if group_name not in models_json_data.get("groups", {}):
                report["errors"].append(f"Groupe de modèles '{group_name}' non trouvé")
                continue
            
            # Récupérer les modèles du groupe
            group_models = models_json_data["groups"][group_name]
            
            # Filtrer les modèles selon les tags
            filtered_models = ModelManager.filter_models_by_tags(group_models, include_tags, exclude_tags)
            
            if not filtered_models:
                logger.info(f"Aucun modèle correspondant aux filtres dans le groupe '{group_name}'")
                report["skipped"].append(f"Groupe '{group_name}': aucun modèle correspondant aux filtres")
                continue
            
            # Installer chaque modèle filtré
            for model in filtered_models:
                model_id = model.get("dest") or model.get("git", "inconnu")
                
                # Vérifier si le modèle existe déjà
                if ModelManager.model_exists_on_disk(model, base_dir):
                    logger.info(f"Le modèle existe déjà: {model_id}")
                    report["already_exists"].append(model_id)
                    continue
                success, message = False, ""
                
                # Télécharger ou cloner le modèle
                if model.get("url"):
                    # Installer le modèle selon son type
                    if model.get("type") == "url":
                        success, message = ModelManager.download_model(model, base_dir)
                    else:
                        success, message = ModelManager.clone_git_repo(model, base_dir)
                elif model.get("git"):
                    success, message = ModelManager.download_model(model, base_dir)
                
                if success:
                    logger.info(f"Modèle installé avec succès: {model_id}")
                    report["installed"].append(model_id)
                else:
                    logger.error(f"Erreur lors de l'installation de {model_id}: {message}")
                    report["errors"].append(f"Erreur lors de l'installation de {model_id}: {message}")
        
        # Installer les workflows
        for workflow_name in bundle_data.get("workflows", []):
            success, message = ModelManager.copy_workflow_to_comfyui(workflow_name)
            if success:
                report["installed"].append(f"workflow:{workflow_name}")
            else:
                report["errors"].append(f"workflow:{workflow_name} - {message}")
        
        return report

    @staticmethod
    def download_model(model: Dict, base_dir: str = None) -> Tuple[bool, str]:
        """
        Télécharge un modèle depuis une URL HTTP.
        Retourne (succès, message).
        
        **Description:** Downloads a model from an HTTP URL.
        **Parameters:**
        - `model` (Dict): Model information containing URL and destination
        - `base_dir` (str): Base directory for path resolution
        **Returns:** Tuple of (success bool, message string)
        """
        # Import here to avoid circular imports
        from .download_manager import DownloadManager
        import requests
        
        url = model.get("url")
        dest = model.get("dest")
        
        if not url or not dest:
            return False, "URL ou destination manquante"
        
        if base_dir is None:
            base_dir = ConfigService.get_base_dir()
        
        file_path = ModelManager.resolve_path(dest, base_dir)
        
        # Vérifier si le fichier existe déjà
        if os.path.exists(file_path):
            logger.info(f"Le fichier existe déjà: {file_path}")
            return True, f"Fichier déjà existant: {os.path.basename(file_path)}"
        
        try:
            # Créer le répertoire parent si nécessaire
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Préparer les headers
            headers = model.get("headers", {})
            
            # Télécharger le fichier
            logger.info(f"Téléchargement de {url} vers {file_path}")
            response = requests.get(url, stream=True, headers=headers)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Téléchargement terminé: {file_path}")
            return True, f"Modèle téléchargé avec succès: {os.path.basename(file_path)}"
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement: {str(e)}")
            return False, f"Erreur lors du téléchargement: {str(e)}"
    
    @staticmethod
    def install_models_from_definitions(model_definitions: List[Dict]) -> Dict[str, List[str]]:
        """
        Install models from a list of model definitions (used by bundles).
        Returns a report with installed models, existing models, and errors.
        
        **Description:** Installs models from a list of model definitions using the DownloadManager.
        **Parameters:**
        - `model_definitions` (List[Dict]): List of model definitions to install
        **Returns:** Dict containing installation report with status lists
        """
        # Import here to avoid circular imports
        from .download_manager import DownloadManager
        
        base_dir = ConfigService.get_base_dir()
        
        # Read tokens for authenticated downloads
        try:
            # Import locally to avoid circular imports
            from .token_service import TokenService
            hf_token, civitai_token = TokenService.read_env_file()
        except ImportError:
            logger.warning("Could not import TokenService, proceeding without tokens")
            hf_token, civitai_token = None, None
        
        install_results = {
            "installed": [],
            "already_exists": [],
            "errors": []
        }
        
        for model in model_definitions:
            model_id = model.get("dest") or model.get("git", "unknown")
            
            # Check if model already exists
            if ModelManager.model_exists_on_disk(model, base_dir):
                logger.info(f"Model already exists: {model_id}")
                install_results["already_exists"].append(model_id)
                continue
            
            try:
                # Start download using DownloadManager
                DownloadManager.download_model(
                    model, 
                    base_dir, 
                    hf_token, 
                    civitai_token, 
                    background=False  # Wait for completion during installation
                )
                install_results["installed"].append(model_id)
                logger.info(f"Model installed successfully: {model_id}")
            except Exception as e:
                error_msg = f"Error installing model {model_id}: {str(e)}"
                install_results["errors"].append(error_msg)
                logger.error(error_msg)        
        return install_results
    
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
        return os.path.join(current_dir, "config.json")
    
    @staticmethod
    # Removed load_user_config and save_user_config. Use ConfigService methods instead.
    
    @staticmethod
    def update_user_base_dir(base_dir: str) -> None:
        """
        Updates the BASE_DIR in user configuration.
        
        **Description:** Updates the BASE_DIR setting in user configuration.
        **Parameters:**
        - `base_dir` (str): New base directory path
        **Returns:** None
        """
        config = ConfigService.load_user_config()
        config["BASE_DIR"] = base_dir
        ConfigService.save_user_config(config)
        logger.info(f"User BASE_DIR updated: {base_dir}")
