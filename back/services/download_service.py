import os
import time
import threading
import subprocess
import requests
from typing import Dict, Optional, List, Any
from .model_manager import ModelManager
from .download_manager import DownloadManager
from back.services.config_service import ConfigService
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Global state for downloads
PROGRESS: Dict[str, Dict] = {}
DOWNLOAD_EVENTS = {}  # model_id -> threading.Event
STOP_EVENTS = {}      # model_id -> threading.Event


class DownloadService:
    """
    High-level download coordination service following Single Responsibility Principle.
    
    **Purpose:** Provides user-friendly download operations including:
    - Download initiation with authentication
    - Download progress monitoring
    - Download cancellation and cleanup
    - User-facing download API
    - Token management integration
    
    **SRP Responsibility:** User-facing download coordination and API.
    This service acts as a facade over DownloadManager, providing a clean
    API for download operations with proper authentication and error handling.
    """
    
    @staticmethod
    def get_model_id(entry: dict) -> str:
        """
        Generate a unique identifier for a model entry.
        
        **Description:** Creates a unique ID for model tracking based on destination or git URL.
        **Parameters:**
        - `entry` (dict): Model entry dictionary
        **Returns:** str containing the unique model ID
        """
        # Use dest as unique identifier
        return entry.get("dest") or entry.get("git")

    @staticmethod
    def get_progress(model_id: str) -> Dict[str, any]:
        """
        Get download progress for a model.
        
        **Description:** Retrieves the current download progress for a specific model.
        **Parameters:**
        - `model_id` (str): Unique identifier for the download
        **Returns:** Dict containing progress percentage and status
        """
        return DownloadManager.get_progress(model_id)

    @staticmethod
    def get_all_downloads() -> List[Dict[str, Any]]:
        """
        Returns the status of all ongoing model downloads.
        
        **Description:** Gets progress information for all active downloads.
        **Parameters:** None
        **Returns:** A list of dicts, each containing progress info and the model ID.
        """
        DownloadManager.cleanup_finished_downloads()
        return DownloadManager.get_all_progress()

    @staticmethod
    def start_download(entry: dict, hf_token: Optional[str] = None, 
                      civitai_token: Optional[str] = None) -> bool:
        """
        Starts downloading a model (url or git), merges identical requests.
        
        **Description:** Initiates a model download with progress tracking and deduplication.
        **Parameters:**
        - `entry` (dict): Model information containing URL/git and destination
        - `hf_token` (Optional[str]): HuggingFace authentication token
        - `civitai_token` (Optional[str]): CivitAI authentication token
        **Returns:** bool indicating if download was started
        """
        model_id = DownloadService.get_model_id(entry)
        
        # Synchronization of concurrent downloads for the same model
        event = DOWNLOAD_EVENTS.get(model_id)
        if event:
            # A download is already in progress, wait for completion
            event.wait()
            progress = PROGRESS.get(model_id, {})
            if progress.get("status") == "done":
                return True
            elif progress.get("status") == "error":
                raise Exception(progress.get("error", "Error during download"))
            else:
                # Unexpected status, restart download
                pass
        else:
            # No download in progress, create a new event
            event = threading.Event()
            DOWNLOAD_EVENTS[model_id] = event
            PROGRESS[model_id] = {"progress": 0, "status": "downloading"}
            # Add a stop_event for this download
            stop_event = threading.Event()
            STOP_EVENTS[model_id] = stop_event
            
            # Start download in background thread
            thread = threading.Thread(
                target=DownloadService._download_worker,
                args=(entry, model_id, event, stop_event, hf_token, civitai_token)
            )
            thread.daemon = True
            thread.start()
            
            return True

    @staticmethod
    def download_models(entries: List[dict], hf_token: Optional[str] = None, 
                       civitai_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Downloads multiple models with validation and deduplication.
        
        **Description:** Handles batch model downloads with proper validation.
        **Parameters:**
        - `entries` (List[dict]): List of model entries to download
        - `hf_token` (Optional[str]): HuggingFace authentication token
        - `civitai_token` (Optional[str]): CivitAI authentication token
        **Returns:** List of download result dictionaries
        """
        base_dir = ConfigService.get_base_dir()
        launched_dests = set()
        results = []
        
        for entry in entries:
            url = entry.get("url", "")
            dest = entry.get("dest")
            git_url = entry.get("git")
            model_id = DownloadService.get_model_id(entry)
            
            # Log the download request
            if url:
                logger.info(f"Download request - URL: {url}")
            elif git_url:
                logger.info(f"Download request - Git: {git_url}")
            
            # Token checks
            if "huggingface.co" in url and not hf_token:
                results.append({"ok": False, "msg": "HuggingFace token required for this download"})
                continue
            if "civitai.com" in url and not civitai_token:
                results.append({"ok": False, "msg": "CivitAI token required for this download"})
                continue

            # Use ModelManager to resolve the path properly
            if dest:
                path = ModelManager.resolve_path(dest, base_dir)
                if not path:
                    results.append({"ok": False, "msg": "Invalid destination path"})
                    continue
                
                # Log the resolved destination path
                logger.info(f"Destination path resolved: {path}")
                logger.info(f"Directory: {os.path.dirname(path)}")
                
                # Check if directory exists, create if not
                dest_dir = os.path.dirname(path)
                if not os.path.exists(dest_dir):
                    logger.info(f"Creating destination directory: {dest_dir}")
                    try:
                        os.makedirs(dest_dir, exist_ok=True)
                    except Exception as e:
                        logger.error(f"Failed to create directory {dest_dir}: {e}")
                        results.append({"ok": False, "msg": f"Failed to create directory: {e}"})
                        continue
                else:
                    logger.info(f"Destination directory exists: {dest_dir}")
            else:
                path = None

            # Only launch each download once per dest
            if path and path in launched_dests:
                logger.info(f"Download already in progress for: {path}")
                results.append({"ok": True, "msg": "Already downloading"})
                continue
            if path:
                launched_dests.add(path)

            try:
                logger.info(f"Starting download - Model ID: {model_id}")
                logger.info(f"Final destination: {path}")
                DownloadManager.download_model(entry, base_dir, hf_token, civitai_token, background=True)
                results.append({"ok": True})
                logger.info(f"Download initiated successfully for: {model_id}")
            except Exception as e:
                logger.error(f"Failed to start download for {model_id}: {e}")
                results.append({"ok": False, "msg": str(e)})
        
        return results

    @staticmethod
    def stop_download(entry: dict) -> Dict[str, any]:
        """
        Stops an ongoing download for a given model.
        
        **Description:** Cancels an active download and cleans up partial files.
        **Parameters:**
        - `entry` (dict): Model information to identify the download
        **Returns:** Dict with operation status and message
        """
        model_id = DownloadService.get_model_id(entry)
        stopped = DownloadManager.stop_download(model_id)
        if stopped:
            return {"ok": True, "msg": "Stop requested"}
        return {"ok": False, "msg": "No active download for this model"}

    @staticmethod
    def delete_models(entries: List[dict]) -> List[Dict[str, Any]]:
        """
        Deletes multiple model files from disk.
        
        **Description:** Handles batch model file deletion with deduplication.
        **Parameters:**
        - `entries` (List[dict]): List of model entries to delete
        **Returns:** List of deletion result dictionaries
        """
        base_dir = ConfigService.get_base_dir()
        deleted_dests = set()
        results = []
        
        for entry in entries:
            dest = entry.get("dest")
            if not dest:
                results.append({"ok": False, "msg": "No destination path provided"})
                continue

            # Use ModelManager to resolve the path properly
            path = ModelManager.resolve_path(dest, base_dir)
            if not path:
                results.append({"ok": False, "msg": "Invalid destination path"})
                continue

            # Only attempt to delete each file once
            if path in deleted_dests:
                results.append({"ok": True, "msg": "Already deleted"})
                continue
            deleted_dests.add(path)

            if os.path.exists(path):
                try:
                    if os.path.isfile(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        import shutil
                        shutil.rmtree(path)
                    results.append({"ok": True})
                except Exception as e:
                    results.append({"ok": False, "msg": f"Error deleting file: {e}"})
            else:
                results.append({"ok": False, "msg": f"File not found: {path}"})
        
        return results

    @staticmethod
    def _download_worker(entry: dict, model_id: str, event: threading.Event, 
                        stop_event: threading.Event, hf_token: Optional[str] = None, 
                        civitai_token: Optional[str] = None) -> None:
        """
        Background worker for model downloads.
        
        **Description:** Handles the actual download process in a background thread.
        **Parameters:**
        - `entry` (dict): Model information
        - `model_id` (str): Unique identifier for the download
        - `event` (threading.Event): Event to signal completion
        - `stop_event` (threading.Event): Event to signal cancellation
        - `hf_token` (Optional[str]): HuggingFace authentication token
        - `civitai_token` (Optional[str]): CivitAI authentication token
        **Returns:** None
        """
        try:
            if "git" in entry:
                DownloadService._download_git_entry(entry, model_id, stop_event)
            else:
                DownloadService._download_url_entry(entry, model_id, hf_token, civitai_token, stop_event)
            
            if not stop_event.is_set():
                PROGRESS[model_id]["progress"] = 100
                PROGRESS[model_id]["status"] = "done"
            else:
                PROGRESS[model_id]["status"] = "stopped"
        except Exception as e:
            PROGRESS[model_id]["status"] = "error"
            PROGRESS[model_id]["error"] = str(e)
            logger.error(f"Download error for {model_id}: {e}")
        finally:
            event.set()
            DOWNLOAD_EVENTS.pop(model_id, None)
            STOP_EVENTS.pop(model_id, None)

    @staticmethod
    def _download_git_entry(entry: dict, model_id: str, stop_event: Optional[threading.Event] = None) -> None:
        """
        Download a model from a git repository.
        
        **Description:** Clones a git repository for model download.
        **Parameters:**
        - `entry` (dict): Model entry containing git URL and destination
        - `model_id` (str): Unique identifier for the download
        - `stop_event` (Optional[threading.Event]): Event to signal cancellation
        **Returns:** None
        """
        base_dir = ConfigService.get_base_dir()
        dest_dir = entry["dest"].replace("${BASE_DIR}", base_dir)
        if os.path.exists(dest_dir):
            PROGRESS[model_id]["progress"] = 100
            PROGRESS[model_id]["status"] = "done"
            return
        
        os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
        proc = subprocess.Popen(["git", "clone", entry["git"], dest_dir])
        
        while proc.poll() is None:
            if stop_event and stop_event.is_set():
                proc.terminate()
                PROGRESS[model_id]["status"] = "stopped"
                return
            time.sleep(0.5)

    @staticmethod
    def _download_url_entry(entry: dict, model_id: str, hf_token: Optional[str] = None, 
                           civitai_token: Optional[str] = None, 
                           stop_event: Optional[threading.Event] = None) -> None:
        """
        Download a model from a URL.
        
        **Description:** Downloads a model file from an HTTP/HTTPS URL with progress tracking.
        **Parameters:**
        - `entry` (dict): Model entry containing URL and destination
        - `model_id` (str): Unique identifier for the download
        - `hf_token` (Optional[str]): HuggingFace authentication token
        - `civitai_token` (Optional[str]): CivitAI authentication token
        - `stop_event` (Optional[threading.Event]): Event to signal cancellation
        **Returns:** None
        """
        base_dir = ConfigService.get_base_dir()
        url = entry["url"]
        dest = entry["dest"].replace("${BASE_DIR}", base_dir)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        
        headers = entry.get("headers", {})
        
        # Add tokens if needed
        if "civitai.com" in url and civitai_token:
            if "token=" not in url:
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}token={civitai_token}"
        
        if "huggingface.co" in url and hf_token:
            if not headers:
                headers = {}
            headers["Authorization"] = f"Bearer {hf_token}"
        
        r = requests.get(url, stream=True, headers=headers)
        r.raise_for_status()
        
        total = int(r.headers.get('content-length', 0))
        downloaded = 0
        
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if stop_event and stop_event.is_set():
                    PROGRESS[model_id]["status"] = "stopped"
                    break
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    PROGRESS[model_id]["progress"] = int(downloaded * 100 / total) if total else 0
