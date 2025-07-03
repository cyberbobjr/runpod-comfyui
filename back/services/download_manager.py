import os
import shutil
import traceback
import requests
import subprocess
import threading
import time
from typing import Dict, List, Any, Optional
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

from typing import Any, Dict, List, Optional
import threading
import time
import os
import shutil
import subprocess
import requests
import logging

logger = logging.getLogger(__name__)

class DownloadProgress:
    """
    Represents the progress and status of a download operation.
    
    **Attributes:**
    - `progress` (int): Download progress percentage (0-100)
    - `status` (str): Status string (e.g., 'downloading', 'done', 'stopped', 'error', 'idle')
    - `dest_path` (Optional[str]): Destination file or directory path
    - `start_time` (Optional[float]): Timestamp when download started
    - `finished_time` (Optional[float]): Timestamp when download finished
    - `error` (Optional[str]): Error message if any
    """
    def __init__(self, progress: int = 0, status: str = "idle", dest_path: Optional[str] = None, start_time: Optional[float] = None, finished_time: Optional[float] = None, error: Optional[str] = None):
        self.progress = progress
        self.status = status
        self.dest_path = dest_path
        self.start_time = start_time
        self.finished_time = finished_time
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "progress": self.progress,
            "status": self.status,
            "dest_path": self.dest_path,
            "start_time": self.start_time,
            "finished_time": self.finished_time,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DownloadProgress":
        return cls(
            progress=data.get("progress", 0),
            status=data.get("status", "idle"),
            dest_path=data.get("dest_path"),
            start_time=data.get("start_time"),
            finished_time=data.get("finished_time"),
            error=data.get("error"),
        )

class DownloadManager:
    @staticmethod
    def is_file_fully_downloaded(local_path: str, expected_size: int) -> bool:
        """
        Check if a file exists and matches the expected size.
        
        **Description:** Returns True if the file at local_path exists and its size matches expected_size.
        **Parameters:**
        - `local_path` (str): Path to the local file
        - `expected_size` (int): Expected file size in bytes
        **Returns:** True if file exists and size matches, False otherwise
        """
        if os.path.exists(local_path):
            local_size = os.path.getsize(local_path)
            return expected_size > 0 and local_size == expected_size
        return False
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
    PROGRESS: Dict[str, DownloadProgress] = {}
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
        progress = cls.PROGRESS.get(model_id)
        if progress:
            return progress.to_dict()
        return {"progress": 0, "status": "idle"}
    
    @classmethod
    def get_all_progress(cls) -> List[Dict[str, Any]]:
        """
        Returns the progress and status of all ongoing downloads.

        **Description:**
        Retrieves progress information for all currently active downloads (status in ["downloading", "stopped", "error"]).

        **Parameters:**
        None

        **Returns:**
        List[Dict[str, Any]]: A list of dictionaries, each containing:
            - 'model_id' (str): The unique identifier for the model being downloaded
            - 'progress' (int): Download progress percentage (0-100)
            - 'status' (str): Download status ("downloading", "stopped", "error")
            - 'dest_path' (Optional[str]): Destination file or directory path
            - 'start_time' (Optional[float]): Timestamp when download started
            - 'finished_time' (Optional[float]): Timestamp when download finished (if any)
            - 'error' (Optional[str]): Error message if any

        **Example:**
        [
            {
                'model_id': 'models/checkpoints/flux1-dev.safetensors',
                'progress': 80,
                'status': 'downloading',
                'dest_path': '/abs/path/to/flux1-dev.safetensors',
                'start_time': 1720000000.0,
                'finished_time': None,
                'error': None
            },
            {
                'model_id': 'models/checkpoints/other-model.safetensors',
                'progress': 100,
                'status': 'stopped',
                'dest_path': '/abs/path/to/other-model.safetensors',
                'start_time': 1720000100.0,
                'finished_time': 1720000200.0,
                'error': 'User cancelled download'
            }
        ]
        """
        return [
            {"model_id": k, **v.to_dict()}
            for k, v in cls.PROGRESS.items()
            if v.status in ["downloading", "stopped", "error"]
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
            progress_info = cls.PROGRESS.get(model_id)
            file_path = progress_info.dest_path if progress_info else None
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
                cls.PROGRESS[model_id].status = "stopped"

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
            status = progress_info.status
            finished_time = progress_info.finished_time
            # Mark finish time if not already marked
            if status in ["done", "stopped", "error"] and progress_info.finished_time is None:
                progress_info.finished_time = current_time
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
        Start a download for a model (HTTP/HTTPS URL or git repository).
        If background=True, runs in a thread and returns immediately.
        Otherwise, blocks until download is done.

        **Description:** Initiates a download process for a model, supporting both HTTP/HTTPS and git sources.

        **Parameters:**
        - `entry` (dict): Model information. Must contain:
            - For HTTP/HTTPS download:
                - `url` (str): The URL of the file to download (required)
                - `dest` (str): The destination path (relative, may contain ${BASE_DIR}) (required)
                - `headers` (dict, optional): Additional HTTP headers
            - For git download:
                - `git` (str): The git repository URL to clone (required)
                - `dest` (str): The destination directory (relative, may contain ${BASE_DIR}) (required)
        - `base_dir` (str): Base directory for resolving destination paths
        - `hf_token` (Optional[str]): HuggingFace authentication token (used for huggingface.co URLs)
        - `civitai_token` (Optional[str]): CivitAI authentication token (used for civitai.com URLs)
        - `background` (bool): Whether to run download in background thread (default: True)

        **Returns:**
        Dict containing initial progress status (e.g., {"progress": 0, "status": "downloading"})
        """
        # Import here to avoid circular imports
        from .model_manager import ModelManager

        logger.info("[download_model] Called with entry=%s, base_dir=%s, hf_token=%s, civitai_token=%s, background=%s", entry, base_dir, bool(hf_token), bool(civitai_token), background)

        model_id = entry.get("dest") or entry.get("git")
        if not model_id:
            logger.error("[download_model] Model entry must have 'dest' or 'git'. Entry: %s", entry)
            raise ValueError("Model entry must have 'dest' or 'git'.")


        # For HTTP/HTTPS downloads, check if file already exists and matches remote size before proceeding
        if entry.get("url") and entry.get("dest"):
            # Try to get remote file size
            resolved_dest = ModelManager.resolve_path(entry["dest"], base_dir)
            try:
                logger.info(f"Making HTTP HEAD request to: {entry["url"]}")
                head_resp = requests.head(entry["url"], headers=entry.get("headers", {}), timeout=30, allow_redirects=True)
                head_resp.raise_for_status()
                total = int(head_resp.headers.get('content-length', 0))
                logger.info(f"Remote content length: {total} bytes")
            except Exception as e:
                logger.warning(f"[download_model] Could not get remote file size for {entry['url']}: {e}")
                total = 0
                
            if cls.is_file_fully_downloaded(resolved_dest, total):
                logger.info(f"[download_model] File {resolved_dest} already exists and matches remote size. Skipping download.")
                return {"progress": 100, "status": "done"}
            elif os.path.exists(resolved_dest):
                local_size = os.path.getsize(resolved_dest)
                logger.info(f"File {resolved_dest} exists but size does not match remote (local: {local_size}, remote: {total}). Re-downloading.")
                
        # Prevent duplicate downloads
        if model_id in cls.DOWNLOAD_EVENTS:
            logger.info("[download_model] Model %s is already being downloaded. Waiting for completion...", model_id)
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

        logger.info("[download_model] model_id=%s, dest_path=%s", model_id, dest_path)

        import time
        cls.PROGRESS[model_id] = DownloadProgress(progress=0, status="downloading", dest_path=dest_path, start_time=time.time())

        def worker():
            logger.info("[download_model.worker] Starting download for model_id=%s", model_id)
            try:
                if entry.get("git"):
                    logger.info("[download_model.worker] Detected git download: git=%s dest=%s", entry.get("git"), entry.get("dest"))
                    cls._download_git(entry, base_dir, model_id, stop_event)
                else:
                    logger.info("[download_model.worker] Detected HTTP/HTTPS download: url=%s dest=%s", entry.get("url"), entry.get("dest"))
                    # Resolve the path before passing to _download_url
                    resolved_entry = entry.copy()
                    if resolved_entry.get("dest"):
                        resolved_entry["dest"] = ModelManager.resolve_path(resolved_entry["dest"], base_dir)
                        logger.info(f"Worker: resolved dest path to {resolved_entry['dest']}")
                    cls._download_url(resolved_entry, model_id, hf_token, civitai_token, stop_event)

                if not stop_event.is_set():
                    cls.PROGRESS[model_id].progress = 100
                    cls.PROGRESS[model_id].status = "done"
                    logger.info(f"Download worker completed successfully for {model_id}")
                else:
                    cls.PROGRESS[model_id].status = "stopped"
                    logger.info(f"Download worker stopped for {model_id}")
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(f"Download worker error for {model_id}: {e}")
                cls.PROGRESS[model_id].status = "error"
                cls.PROGRESS[model_id].error = str(e)
            finally:
                event.set()
                cls.DOWNLOAD_EVENTS.pop(model_id, None)
                cls.STOP_EVENTS.pop(model_id, None)
                logger.info(f"Download worker cleanup completed for {model_id}")

        if background:
            logger.info("[download_model] Launching download in background thread for model_id=%s", model_id)
            threading.Thread(target=worker, daemon=True).start()
            return {"progress": 0, "status": "downloading"}
        else:
            logger.info("[download_model] Running download synchronously for model_id=%s", model_id)
            worker()
            progress = cls.PROGRESS.get(model_id)
            if progress:
                return progress.to_dict()
            return {"progress": 0, "status": "idle"}

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
            cls.PROGRESS[model_id].progress = 100
            cls.PROGRESS[model_id].status = "done"
            return
        os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
        proc = subprocess.Popen(["git", "clone", entry["git"], dest_dir])
        while proc.poll() is None:
            if stop_event and stop_event.is_set():
                proc.terminate()
                cls.PROGRESS[model_id].status = "stopped"
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
            logger.info(f"Making HTTP GET request to: {url}")
            with requests.get(url, stream=True, headers=headers, timeout=30) as r:
                logger.info(f"HTTP response status: {r.status_code}")
                logger.info(f"HTTP response headers: {dict(r.headers)}")

                # Check for HTTP errors
                r.raise_for_status()
                
                total = int(r.headers.get('content-length', 0))
                logger.info(f"Content length: {total} bytes")
                # Use the total from GET if not available from HEAD
                if total == 0:
                    total = int(r.headers.get('content-length', 0))
                    logger.info(f"Content length from GET: {total} bytes")

                downloaded = 0
                logger.info(f"Opening file for writing: {dest}")

                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if stop_event and stop_event.is_set():
                            logger.info(f"Download stopped by user for {model_id}")
                            cls.PROGRESS[model_id].status = "stopped"
                            # Remove partial file
                            if os.path.exists(dest):
                                os.remove(dest)
                                logger.info(f"Removed partial file: {dest}")
                            break
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress = int(downloaded * 100 / total) if total else 0
                            cls.PROGRESS[model_id].progress = progress
                            # Log progress every 10%
                            if progress % 10 == 0 and progress != getattr(cls.PROGRESS[model_id], "last_logged_progress", -1):
                                logger.info(f"Download progress for {model_id}: {progress}% ({downloaded}/{total} bytes)")
                                cls.PROGRESS[model_id].last_logged_progress = progress

                if not stop_event or not stop_event.is_set():
                    file_size = os.path.getsize(dest)
                    logger.info(f"Download completed for {model_id}. Final file size: {file_size} bytes")
                    logger.info(f"File saved at: {dest}")
                else:
                    # Download was stopped after the loop - remove partial file
                    if os.path.exists(dest):
                        os.remove(dest)
                        logger.info(f"Download was stopped - removed partial file: {dest}")
                    cls.PROGRESS[model_id].status = "stopped"

                    # Verify file exists and has content
                    if os.path.exists(dest) and file_size > 0:
                        logger.info(f"File verification successful for {model_id}")
                    else:
                        logger.error(f"File verification failed for {model_id}: exists={os.path.exists(dest)}, size={file_size}")

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request error for {model_id}: {e}")
            cls.PROGRESS[model_id].status = "error"
            cls.PROGRESS[model_id].error = f"HTTP request error: {str(e)}"
            raise
        except IOError as e:
            logger.error(f"File I/O error for {model_id}: {e}")
            cls.PROGRESS[model_id].status = "error"
            cls.PROGRESS[model_id].error = f"File I/O error: {str(e)}"
            raise
        except Exception as e:
            logger.error(f"Unexpected error during download for {model_id}: {e}")
            cls.PROGRESS[model_id].status = "error"
            cls.PROGRESS[model_id].error = f"Unexpected error: {str(e)}"
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
