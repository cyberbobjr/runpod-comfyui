import os
import shutil
import requests
import subprocess
import threading
import time
from typing import Dict, List, Any, Optional
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

class DownloadManager:
    """
    Centralized download manager for models following Single Responsibility Principle.
    
    **Purpose:** Handles the download mechanics including:
    - Progress tracking for concurrent downloads
    - HTTP/HTTPS file downloads with authentication
    - Git repository cloning operations
    - Download cancellation and cleanup
    - Cleanup of finished downloads
    
    **SRP Responsibility:** Download execution and progress management.
    This class should NOT handle model configuration (use ModelManager) or
    high-level download coordination (use DownloadService).
    """
    PROGRESS: Dict[str, Dict] = {}
    DOWNLOAD_EVENTS: Dict[str, threading.Event] = {}
    STOP_EVENTS: Dict[str, threading.Event] = {}

    @classmethod
    def get_progress(cls, model_id: str) -> Dict[str, Any]:
        """
        Get the progress of a specific download.
        
        **Description:** Returns the progress and status information for a given model download.
        **Parameters:**
        - `model_id` (str): The unique identifier for the model being downloaded
        **Returns:** Dict containing progress percentage and status information
        """
        return cls.PROGRESS.get(model_id, {"progress": 0, "status": "idle"})   
    
    @classmethod
    def get_all_progress(cls) -> List[Dict]:
        """
        Returns the progress and status of all ongoing downloads.
        
        **Description:** Retrieves progress information for all currently active downloads.
        **Parameters:** None
        **Returns:** A list of dicts, each containing progress info and the model ID.
        """
        return [
            {"model_id": k, **v}
            for k, v in cls.PROGRESS.items()
            if v.get("status") in ["downloading", "stopped"]
        ]

    @classmethod
    def stop_download(cls, model_id: str) -> bool:
        """
        Stop a download and clean up any partial files.
        
        **Description:** Stops an active download and removes any partially downloaded files.
        **Parameters:**
        - `model_id` (str): The unique identifier for the download to stop
        **Returns:** bool indicating whether the stop operation was successful
        """
        stop_event = cls.STOP_EVENTS.get(model_id)
        if stop_event:
            stop_event.set()
            
            # Try to clean up partial file/directory if we have the path
            progress_info = cls.PROGRESS.get(model_id, {})
            file_path = progress_info.get("dest_path")
            if file_path and os.path.exists(file_path):
                try:
                    if os.path.isdir(file_path):
                        # It's a git repository directory
                        shutil.rmtree(file_path)
                        logger.info(f"Removed partial git directory during stop_download: {file_path}")
                    else:
                        # It's a regular file
                        os.remove(file_path)
                        logger.info(f"Removed partial file during stop_download: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to remove partial file/directory {file_path}: {e}")
            
            # Mark as stopped
            if model_id in cls.PROGRESS:
                cls.PROGRESS[model_id]["status"] = "stopped"
            
            return True
        return False

    @classmethod
    def cleanup_finished_downloads(cls):
        """
        Clean up downloads that are finished (done, stopped, error) after 30 seconds.
        This prevents the PROGRESS dictionary from growing indefinitely.
        
        **Description:** Removes finished download entries from memory after a timeout period.
        **Parameters:** None
        **Returns:** Number of entries that were cleaned up
        """
        current_time = time.time()
        to_remove = []
        
        for model_id, progress_info in cls.PROGRESS.items():
            status = progress_info.get("status")
            finished_time = progress_info.get("finished_time")
            
            # Mark finish time if not already marked
            if status in ["done", "stopped", "error"] and "finished_time" not in progress_info:
                progress_info["finished_time"] = current_time
                logger.info(f"Marked download {model_id} as finished at {current_time}")
            
            # Remove entries that have been finished for more than 30 seconds
            elif status in ["done", "stopped", "error"] and finished_time:
                if current_time - finished_time > 30:  # 30 seconds
                    to_remove.append(model_id)
                    logger.info(f"Cleaning up finished download entry: {model_id} (status: {status})")
        
        # Remove the entries
        for model_id in to_remove:
            cls.PROGRESS.pop(model_id, None)
        
        return len(to_remove)

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
        
        **Description:** Initiates a download process for a model, supporting both URL and git sources.
        **Parameters:**
        - `entry` (dict): Model information containing URL/git and destination details
        - `base_dir` (str): Base directory for resolving paths
        - `hf_token` (Optional[str]): HuggingFace authentication token
        - `civitai_token` (Optional[str]): CivitAI authentication token
        - `background` (bool): Whether to run download in background thread
        **Returns:** Dict containing initial progress status
        """
        # Import here to avoid circular imports
        from .model_manager import ModelManager
        
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
        
        # Store the destination path for cleanup purposes
        dest_path = None
        if entry.get("dest"):
            dest_path = ModelManager.resolve_path(entry["dest"], base_dir)
        elif entry.get("git"):
            dest_path = ModelManager.resolve_path(entry["dest"], base_dir) if entry.get("dest") else None
            
        cls.PROGRESS[model_id] = {
            "progress": 0, 
            "status": "downloading",
            "dest_path": dest_path
        }

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
                    cls._download_url(resolved_entry, model_id, hf_token, civitai_token, stop_event)
                    
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
        """
        Download a model from a git repository.
        
        **Description:** Clones a git repository for model download.
        **Parameters:**
        - `entry` (dict): Model entry containing git URL and destination
        - `base_dir` (str): Base directory for resolving paths
        - `model_id` (str): Unique identifier for the download
        - `stop_event` (threading.Event): Event to signal download cancellation
        **Returns:** None
        """
        # Import here to avoid circular imports
        from .model_manager import ModelManager
        
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
                # Remove partial directory
                if os.path.exists(dest_dir):
                    try:
                        shutil.rmtree(dest_dir)
                        logger.info(f"Removed partial git directory: {dest_dir}")
                    except Exception as e:
                        logger.error(f"Failed to remove partial git directory {dest_dir}: {e}")
                return
            time.sleep(0.5)

    @classmethod
    def _download_url(cls, entry, model_id, hf_token, civitai_token, stop_event):
        """
        Download a model from a URL.
        
        **Description:** Downloads a model file from an HTTP/HTTPS URL with progress tracking.
        **Parameters:**
        - `entry` (dict): Model entry containing URL and destination
        - `model_id` (str): Unique identifier for the download
        - `hf_token` (Optional[str]): HuggingFace authentication token
        - `civitai_token` (Optional[str]): CivitAI authentication token
        - `stop_event` (threading.Event): Event to signal download cancellation
        **Returns:** None
        """
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
                else:
                    # Download was stopped after the loop - remove partial file
                    if os.path.exists(dest):
                        os.remove(dest)
                        logger.info(f"Download was stopped - removed partial file: {dest}")
                    cls.PROGRESS[model_id]["status"] = "stopped"
                    
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
        """
        Resolve path with BASE_DIR substitution.
        
        **Description:** Resolves a path by substituting BASE_DIR variables.
        **Parameters:**
        - `path` (str): The path to resolve
        - `base_dir` (str): The base directory to substitute
        **Returns:** str containing the resolved absolute path
        """
        if "${BASE_DIR}" in path:
            return path.replace("${BASE_DIR}", base_dir)
        return path
