import os
import json
import threading
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Body
from typing import Dict, Optional
from pydantic import BaseModel
# Import authentication from auth.py instead
from auth import protected, create_jwt, verify_user, load_users, hash_password, get_users_file_path
from model_utils import ModelManager

MODELS_JSON = "models.json"
ENV_FILE = ".env"
PROGRESS: Dict[str, Dict] = {}
USERS_JSON = "users.json"

DOWNLOAD_EVENTS = {}  # model_id -> threading.Event
STOP_EVENTS = {}      # model_id -> threading.Event

api_router = APIRouter(prefix="/api/models")
auth_router = APIRouter(prefix="/api/auth")

class TokenConfig(BaseModel):
    hf_token: Optional[str]
    civitai_token: Optional[str]

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangeUserRequest(BaseModel):
    old_username: str
    old_password: str
    new_username: str
    new_password: str

@auth_router.post("/login")
def login(req: LoginRequest):
    if verify_user(req.username, req.password):
        token = create_jwt(req.username)
        return {"token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@api_router.post("/change_user")
def change_user(req: ChangeUserRequest, user=Depends(protected)):
    users = load_users()
    # Check old login/password using verify_user for proper hash verification
    if not verify_user(req.old_username, req.old_password):
        raise HTTPException(status_code=401, detail="Invalid current username or password")
    # Prevent replacing with an already existing login (other than oneself)
    if req.new_username != req.old_username and req.new_username in users:
        raise HTTPException(status_code=409, detail="Username already exists")
    # Update the users.json file with hashed password
    del users[req.old_username]
    users[req.new_username] = hash_password(req.new_password)
    users_path = get_users_file_path()
    with open(users_path, "w", encoding="utf-8") as f:
        json.dump(users, f)
    return {"ok": True}

def get_models_base_dir():
    """Returns the models root directory according to COMFYUI_MODEL_DIR/models or config.BASE_DIR rule."""
    return ModelManager.get_models_dir()

@api_router.get("/")
def list_models(user=Depends(protected)):
    """Lists all models from JSON and their status on disk."""
    groups = load_models()
    base_dir = get_models_base_dir()
    result = []
    for group, entries in groups.items():
        for entry in entries:
            dest = entry.get("dest")
            # Replace ${BASE_DIR} with the path determined above
            path = dest.replace("${BASE_DIR}", base_dir) if dest else None
            exists = os.path.exists(path) if path else False
            model_id = get_model_id(entry)
            progress = PROGRESS.get(model_id, {})
            # Explicit addition of tags in response (copy of entry to not modify original)
            entry_with_tags = dict(entry)
            if "tags" not in entry_with_tags:
                entry_with_tags["tags"] = []
            # Check disk size if model exists and expected size is defined
            if exists and entry.get("size") is not None:
                try:
                    actual_size = os.path.getsize(path)
                    expected_size = entry.get("size")
                    if actual_size != expected_size:
                        # Add "incorrect size" if not already present
                        tags = entry_with_tags["tags"]
                        if "incorrect size" not in tags:
                            tags.append("incorrect size")
                    else:
                        # Remove "incorrect size" if size is correct and tag is present
                        tags = entry_with_tags["tags"]
                        if "incorrect size" in tags:
                            tags.remove("incorrect size")
                except Exception:
                    # If error reading size, add the tag
                    tags = entry_with_tags["tags"]
                    if "incorrect size" not in tags:
                        tags.append("incorrect size")
            result.append({
                "group": group,
                "entry": entry_with_tags,
                "exists": exists,
                "progress": progress.get("progress", 0),
                "status": progress.get("status", "idle"),
            })
    return result

@api_router.post("/download")
def download_model(entry: dict, background_tasks: BackgroundTasks, user=Depends(protected)):
    """Starts downloading a model (url or git), merges identical requests."""
    model_id = get_model_id(entry)
    url = entry.get("url", "")
    hf_token, civitai_token = read_env_file()
    if "huggingface.co" in url and not hf_token:
        raise HTTPException(status_code=400, detail="HuggingFace token is required for this download.")
    if "civitai.com" in url and not civitai_token:
        raise HTTPException(status_code=400, detail="CivitAI token is required for this download.")

    # Synchronization of concurrent downloads for the same model
    event = DOWNLOAD_EVENTS.get(model_id)
    if event:
        # A download is already in progress, wait for completion
        event.wait()
        progress = PROGRESS.get(model_id, {})
        if progress.get("status") == "done":
            return {"ok": True}
        elif progress.get("status") == "error":
            raise HTTPException(status_code=500, detail=progress.get("error", "Error during download"))
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
        background_tasks.add_task(download_worker, entry, model_id, event, stop_event)
        return {"ok": True}

@api_router.post("/stop_download")
def stop_download(entry: dict, user=Depends(protected)):
    """Stops an ongoing download for a given model."""
    model_id = get_model_id(entry)
    stop_event = STOP_EVENTS.get(model_id)
    if stop_event:
        stop_event.set()
        return {"ok": True, "msg": "Stop requested"}
    else:
        return {"ok": False, "msg": "No active download for this model"}

def download_worker(entry, model_id, event, stop_event):
    try:
        hf_token, civitai_token = read_env_file()
        if "git" in entry:
            download_git_entry(entry, model_id, stop_event)
        else:
            download_url_entry(entry, model_id, hf_token, civitai_token, stop_event)
        if not stop_event.is_set():
            PROGRESS[model_id]["progress"] = 100
            PROGRESS[model_id]["status"] = "done"
        else:
            PROGRESS[model_id]["status"] = "stopped"
    except Exception as e:
        PROGRESS[model_id]["status"] = "error"
        PROGRESS[model_id]["error"] = str(e)
    finally:
        event.set()
        DOWNLOAD_EVENTS.pop(model_id, None)
        STOP_EVENTS.pop(model_id, None)

def download_git_entry(entry, model_id, stop_event=None):
    import subprocess
    base_dir = get_models_base_dir()
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
        # Sleep a bit to not loop too fast
        import time
        time.sleep(0.5)

def download_url_entry(entry, model_id, hf_token=None, civitai_token=None, stop_event=None):
    import requests
    base_dir = get_models_base_dir()
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

@api_router.post("/progress")
def get_progress(entry: dict = Body(...), user=Depends(protected)):
    """Returns download progress (POST with entry in body)."""
    model_id = get_model_id(entry)
    return PROGRESS.get(model_id, {"progress": 0, "status": "idle"})

@api_router.post("/tokens")
def set_tokens(cfg: TokenConfig, user=Depends(protected)):
    """Sets API tokens in the .env file."""
    write_env_file(cfg.hf_token, cfg.civitai_token)
    return {"ok": True}

@api_router.get("/tokens")
def get_tokens(user=Depends(protected)):
    """Returns API tokens stored in the .env file."""
    hf_token, civitai_token = read_env_file()
    return {"hf_token": hf_token, "civitai_token": civitai_token}

def get_env_file_path():
    """Returns the full path of the .env file according to COMFYUI_MODEL_DIR or current directory."""
    return ModelManager.get_env_file_path()

def write_env_file(hf_token: Optional[str], civitai_token: Optional[str]):
    """Writes tokens to the .env file."""
    lines = []
    if hf_token is not None:
        lines.append(f"HF_TOKEN={hf_token}")
    if civitai_token is not None:
        lines.append(f"CIVITAI_TOKEN={civitai_token}")
    env_path = get_env_file_path()
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def read_env_file():
    """Reads tokens from the .env file."""
    hf_token = None
    civitai_token = None
    env_path = get_env_file_path()
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("HF_TOKEN="):
                    hf_token = line.strip().split("=", 1)[1]
                elif line.startswith("CIVITAI_TOKEN="):
                    civitai_token = line.strip().split("=", 1)[1]
    return hf_token, civitai_token

def load_models():
    data = ModelManager.load_models_json()
    groups = data.get("groups", {})
    return groups

def get_model_id(entry):
    # Use dest as unique identifier
    return entry.get("dest") or entry.get("git")

def load_base_dir():
    return ModelManager.get_base_dir()

def get_total_dir_size(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except Exception:
                pass
    return total

@api_router.get("/total_size")
def total_size(user=Depends(protected)):
    """Returns the total size (in bytes) of the base_dir directory."""
    base_dir = os.environ.get("COMFYUI_MODEL_DIR", ".")
    size = get_total_dir_size(base_dir)
    return {"base_dir": base_dir, "total_size": size}