import os
import json
import logging
import shutil
import requests
import subprocess
import threading
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from fastapi import HTTPException

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELS_JSON = "models.json"

class DownloadManager:
    """
    Centralized download manager for models.
    Tracks progress, supports concurrent downloads, and allows stopping downloads.
    """
    PROGRESS: Dict[str, Dict] = {}
    DOWNLOAD_EVENTS: Dict[str, threading.Event] = {}
    STOP_EVENTS: Dict[str, threading.Event] = {}

    @classmethod
    def get_progress(cls, model_id: str) -> Dict[str, Any]:
        return cls.PROGRESS.get(model_id, {"progress": 0, "status": "idle"})

    @classmethod
    def get_all_progress(cls) -> Dict[str, Dict]:
        """
        Returns the progress and status of all ongoing downloads.
        """
        return {k: v for k, v in cls.PROGRESS.items() if v.get("status") == "downloading"}

    @classmethod
    def stop_download(cls, model_id: str) -> bool:
        stop_event = cls.STOP_EVENTS.get(model_id)
        if stop_event:
            stop_event.set()
            return True
        return False

    @classmethod
    def download_model(
        cls,
        entry: dict,
        base_dir: str,
        hf_token: Optional[str] = None,
        civitai_token: Optional[str] = None,
        background: bool = True,
    ):
        """
        Start a download for a model (URL or git).
        If background=True, runs in a thread and returns immediately.
        Otherwise, blocks until download is done.
        """
        model_id = entry.get("dest") or entry.get("git")
        if not model_id:
            raise ValueError("Model entry must have 'dest' or 'git'.")

        # Prevent duplicate downloads
        if model_id in cls.DOWNLOAD_EVENTS:
            event = cls.DOWNLOAD_EVENTS[model_id]
            event.wait()
            return cls.PROGRESS.get(model_id, {"progress": 0, "status": "idle"})

        event = threading.Event()
        stop_event = threading.Event()
        cls.DOWNLOAD_EVENTS[model_id] = event
        cls.STOP_EVENTS[model_id] = stop_event
        cls.PROGRESS[model_id] = {"progress": 0, "status": "downloading"}

        def worker():
            try:
                if entry.get("git"):
                    cls._download_git(entry, base_dir, model_id, stop_event)
                else:
                    # Resolve the path before passing to _download_url
                    resolved_entry = entry.copy()
                    if resolved_entry.get("dest"):
                        resolved_entry["dest"] = ModelManager.resolve_path(resolved_entry["dest"], base_dir)
                        logger.info(f"Worker: resolved dest path to {resolved_entry['dest']}")
                    cls._download_url(resolved_entry, base_dir, model_id, hf_token, civitai_token, stop_event)
                    
                if not stop_event.is_set():
                    cls.PROGRESS[model_id]["progress"] = 100
                    cls.PROGRESS[model_id]["status"] = "done"
                    logger.info(f"Download worker completed successfully for {model_id}")
                else:
                    cls.PROGRESS[model_id]["status"] = "stopped"
                    logger.info(f"Download worker stopped for {model_id}")
            except Exception as e:
                logger.error(f"Download worker error for {model_id}: {e}")
                cls.PROGRESS[model_id]["status"] = "error"
                cls.PROGRESS[model_id]["error"] = str(e)
            finally:
                event.set()
                cls.DOWNLOAD_EVENTS.pop(model_id, None)
                cls.STOP_EVENTS.pop(model_id, None)
                logger.info(f"Download worker cleanup completed for {model_id}")

        if background:
            threading.Thread(target=worker, daemon=True).start()
            return {"progress": 0, "status": "downloading"}
        else:
            worker()
            return cls.PROGRESS.get(model_id, {"progress": 0, "status": "idle"})

    @classmethod
    def _download_git(cls, entry, base_dir, model_id, stop_event):
        dest_dir = ModelManager.resolve_path(entry["dest"], base_dir)
        if os.path.exists(dest_dir):
            cls.PROGRESS[model_id]["progress"] = 100
            cls.PROGRESS[model_id]["status"] = "done"
            return
        os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
        proc = subprocess.Popen(["git", "clone", entry["git"], dest_dir])
        while proc.poll() is None:
            if stop_event and stop_event.is_set():
                proc.terminate()
                cls.PROGRESS[model_id]["status"] = "stopped"
                return
            time.sleep(0.5)

    @classmethod
    def _download_url(cls, entry, base_dir, model_id, hf_token, civitai_token, stop_event):
        url = entry["url"]
        # The dest should already be resolved in the worker function
        dest = entry["dest"]
        
        logger.info(f"Starting _download_url for model {model_id}")
        logger.info(f"Original URL: {url}")
        logger.info(f"Destination path: {dest}")
        
        # Create directory if it doesn't exist
        dest_dir = os.path.dirname(dest)
        logger.info(f"Creating directory if needed: {dest_dir}")
        os.makedirs(dest_dir, exist_ok=True)
        
        headers = entry.get("headers", {})
        logger.info(f"Initial headers: {headers}")
        
        # Handle CivitAI token
        if "civitai.com" in url and civitai_token:
            if "token=" not in url:
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}token={civitai_token}"
                logger.info(f"Added CivitAI token to URL")
        
        # Handle HuggingFace token
        if "huggingface.co" in url and hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"
            logger.info(f"Added HuggingFace authorization header")
        
        logger.info(f"Final headers: {headers}")
        logger.info(f"Final URL: {url}")
        
        try:
            logger.info(f"Making HTTP request to: {url}")
            with requests.get(url, stream=True, headers=headers, timeout=30) as r:
                logger.info(f"HTTP response status: {r.status_code}")
                logger.info(f"HTTP response headers: {dict(r.headers)}")
                
                # Check for HTTP errors
                r.raise_for_status()
                
                total = int(r.headers.get('content-length', 0))
                logger.info(f"Content length: {total} bytes")
                
                downloaded = 0
                logger.info(f"Opening file for writing: {dest}")
                
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if stop_event and stop_event.is_set():
                            logger.info(f"Download stopped by user for {model_id}")
                            cls.PROGRESS[model_id]["status"] = "stopped"
                            # Remove partial file
                            if os.path.exists(dest):
                                os.remove(dest)
                                logger.info(f"Removed partial file: {dest}")
                            break
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress = int(downloaded * 100 / total) if total else 0
                            cls.PROGRESS[model_id]["progress"] = progress
                            
                            # Log progress every 10%
                            if progress % 10 == 0 and progress != cls.PROGRESS[model_id].get("last_logged_progress", -1):
                                logger.info(f"Download progress for {model_id}: {progress}% ({downloaded}/{total} bytes)")
                                cls.PROGRESS[model_id]["last_logged_progress"] = progress
                
                if not stop_event or not stop_event.is_set():
                    file_size = os.path.getsize(dest)
                    logger.info(f"Download completed for {model_id}. Final file size: {file_size} bytes")
                    logger.info(f"File saved at: {dest}")
                    
                    # Verify file exists and has content
                    if os.path.exists(dest) and file_size > 0:
                        logger.info(f"File verification successful for {model_id}")
                    else:
                        logger.error(f"File verification failed for {model_id}: exists={os.path.exists(dest)}, size={file_size}")
                        
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request error for {model_id}: {e}")
            cls.PROGRESS[model_id]["status"] = "error"
            cls.PROGRESS[model_id]["error"] = f"HTTP request error: {str(e)}"
            raise
        except IOError as e:
            logger.error(f"File I/O error for {model_id}: {e}")
            cls.PROGRESS[model_id]["status"] = "error"
            cls.PROGRESS[model_id]["error"] = f"File I/O error: {str(e)}"
            raise
        except Exception as e:
            logger.error(f"Unexpected error during download for {model_id}: {e}")
            cls.PROGRESS[model_id]["status"] = "error"
            cls.PROGRESS[model_id]["error"] = f"Unexpected error: {str(e)}"
            raise

    @classmethod
    def resolve_path(cls, path: str, base_dir: str) -> str:
        """Resolve path with BASE_DIR substitution"""
        if "${BASE_DIR}" in path:
            return path.replace("${BASE_DIR}", base_dir)
        return path

class ModelManager:
    """
    Classe utilitaire pour gérer les modèles et les workflows.
    Contient des méthodes pour charger, installer et vérifier les modèles.
    """
    
    # Cache pour éviter les rechargements répétés
    _cache = {
        "models_json_data": None,
        "models_json_path": None,
        "base_dir": None,
        "last_load_time": 0,
        "cache_ttl": 30  # Cache valide pendant 30 secondes
    }
    
    @staticmethod
    def _is_cache_valid() -> bool:
        """Vérifie si le cache est encore valide."""
        return (time.time() - ModelManager._cache["last_load_time"]) < ModelManager._cache["cache_ttl"]
    
    @staticmethod
    def _clear_cache():
        """Vide le cache."""
        ModelManager._cache["models_json_data"] = None
        ModelManager._cache["models_json_path"] = None
        ModelManager._cache["base_dir"] = None
        ModelManager._cache["last_load_time"] = 0
    
    @staticmethod
    def get_base_dir() -> str:
        """
        Retourne le répertoire de base (BASE_DIR) selon la priorité :
        1. Variable d'environnement BASE_DIR
        2. Valeur dans models.json config.BASE_DIR
        3. Variable d'environnement COMFYUI_MODEL_DIR
        4. Répertoire courant
        """
        # Vérifier le cache d'abord
        if ModelManager._is_cache_valid() and ModelManager._cache["base_dir"]:
            return ModelManager._cache["base_dir"]
        
        base_dir = None
        
        # Priorité 1: Variable d'environnement BASE_DIR
        env_base_dir = os.environ.get("BASE_DIR")
        if env_base_dir:
            logger.debug(f"Utilisation de BASE_DIR depuis variable d'environnement: {env_base_dir}")
            base_dir = env_base_dir
        
        # Priorité 2: Valeur dans models.json (sans utiliser le cache pour éviter la récursion)
        if not base_dir:
            try:
                models_path = ModelManager._find_models_json_path()
                if models_path and os.path.exists(models_path):
                    with open(models_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    config_base_dir = data.get("config", {}).get("BASE_DIR", "")
                    if config_base_dir:
                        logger.debug(f"Utilisation de BASE_DIR depuis models.json: {config_base_dir}")
                        base_dir = config_base_dir
            except Exception:
                logger.debug("Impossible de lire BASE_DIR depuis models.json")
        
        # Priorité 3: Variable d'environnement COMFYUI_MODEL_DIR
        if not base_dir:
            comfy_dir = os.environ.get("COMFYUI_MODEL_DIR")
            if comfy_dir:
                logger.debug(f"Utilisation de COMFYUI_MODEL_DIR: {comfy_dir}")
                base_dir = comfy_dir
        
        # Priorité 4: Répertoire courant
        if not base_dir:
            base_dir = os.getcwd()
            logger.debug(f"Utilisation du répertoire courant: {base_dir}")
        
        # Mettre en cache
        ModelManager._cache["base_dir"] = base_dir
        return base_dir
    
    @staticmethod
    def _find_models_json_path() -> str:
        """Méthode interne pour trouver le chemin de models.json sans utiliser le cache."""
        # Stratégie 1: Variable d'environnement BASE_DIR
        env_base_dir = os.environ.get("BASE_DIR")
        if env_base_dir:
            path = os.path.join(env_base_dir, MODELS_JSON)
            if os.path.exists(path):
                return path
        
        # Stratégie 2: Répertoire courant de l'application
        current_dir = os.path.abspath(os.getcwd())
        path = os.path.join(current_dir, MODELS_JSON)
        if os.path.exists(path):
            return path
        
        # Stratégie 3: Répertoire du script actuel
        script_dir = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(script_dir, MODELS_JSON)
        if os.path.exists(path):
            return path
        
        # Stratégie 4: Variable d'environnement COMFYUI_MODEL_DIR
        comfy_dir = os.environ.get("COMFYUI_MODEL_DIR")
        if comfy_dir:
            path = os.path.join(comfy_dir, MODELS_JSON)
            if os.path.exists(path):
                return path
        
        # Retourner le chemin par défaut
        return os.path.join(current_dir, MODELS_JSON)
    
    @staticmethod
    def get_models_dir() -> str:
        """Retourne le répertoire des modèles : ${BASE_DIR}/models"""
        base_dir = ModelManager.get_base_dir()
        models_dir = os.path.join(base_dir, "models")
        return models_dir
    
    @staticmethod
    def get_workflows_dir() -> str:
        """Retourne le répertoire des workflows : ${BASE_DIR}/user/default/workflows"""
        base_dir = ModelManager.get_base_dir()
        workflows_dir = os.path.join(base_dir, "user", "default", "workflows")
        return workflows_dir
    
    @staticmethod
    def get_env_file_path() -> str:
        """Retourne le chemin du fichier .env : ${BASE_DIR}/.env"""
        base_dir = ModelManager.get_base_dir()
        return os.path.join(base_dir, ".env")
    
    @staticmethod
    def get_bundles_dir() -> str:
        """Return the bundles directory path."""
        base_dir = ModelManager.get_base_dir()
        bundles_dir = os.path.join(base_dir, "bundles")
        # Normalize path to avoid double backslashes
        bundles_dir = os.path.normpath(bundles_dir)
        return bundles_dir
    
    @staticmethod
    def get_installed_bundles_file() -> str:
        """Retourne le chemin du fichier installed_bundles.json"""
        bundles_dir = ModelManager.get_bundles_dir()
        return os.path.join(bundles_dir, "installed_bundles.json")

    @staticmethod
    def get_models_json_path() -> str:
        """Retourne le chemin complet du fichier models.json"""
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
        """Charge le fichier models.json complet avec cache"""
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
                empty_data = {"config": {"BASE_DIR": ModelManager.get_base_dir()}, "groups": {}}
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
    def save_models_json(data: Dict) -> None:
        """Sauvegarde le fichier models.json et invalide le cache"""
        models_path = ModelManager.get_models_json_path()
        logger.debug(f"Sauvegarde du fichier: {models_path}")
        
        try:
            # Assurer que le répertoire existe
            os.makedirs(os.path.dirname(models_path) or ".", exist_ok=True)
            
            with open(models_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            # Invalider le cache après sauvegarde
            ModelManager._clear_cache()
            
            logger.debug(f"Fichier models.json sauvegardé avec succès à {models_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde du fichier: {str(e)}")
    
    @staticmethod
    def resolve_path(path: str, base_dir: str = None) -> str:
        """
        Résout un chemin de fichier en tenant compte des variables comme ${BASE_DIR}
        et retourne le chemin absolu réel.
        """
        if not path:
            return None
            
        if "${BASE_DIR}" in path:
            if base_dir is None:
                base_dir = ModelManager.get_base_dir()
            return path.replace("${BASE_DIR}", base_dir)
        
        return path
    
    @staticmethod
    def model_exists_on_disk(entry: Dict, base_dir: str = None) -> bool:
        """
        Vérifie si un modèle existe sur le disque.
        """
        dest = entry.get("dest")
        if not dest:
            return False
            
        # Résoudre le chemin réel
        if base_dir is None:
            base_dir = ModelManager.get_base_dir()
        file_path = ModelManager.resolve_path(dest, base_dir)
        
        return os.path.exists(file_path)
    
    @staticmethod
    def clone_git_repo(entry: Dict, base_dir: str = None) -> Tuple[bool, str]:
        """
        Clone un dépôt git pour récupérer un modèle ou un plugin.
        Retourne (succès, message).
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
        """
        workflows_dir = ModelManager.get_workflows_dir()
        source_path = os.path.join(workflows_dir, workflow_name)
        
        # Le répertoire ComfyUI est dans BASE_DIR/ComfyUI/workflows
        base_dir = ModelManager.get_base_dir()
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
        """
        # Charger les données du fichier models.json
        models_json_data = ModelManager.load_models_json()
        base_dir = ModelManager.get_base_dir()
        
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
        """
        url = model.get("url")
        dest = model.get("dest")
        
        if not url or not dest:
            return False, "URL ou destination manquante"
        
        if base_dir is None:
            base_dir = ModelManager.get_base_dir()
        
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
        """
        base_dir = ModelManager.get_base_dir()
        
        # Read tokens for authenticated downloads
        try:
            from api_models import read_env_file
            hf_token, civitai_token = read_env_file()
        except ImportError:
            logger.warning("Could not import read_env_file, proceeding without tokens")
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
