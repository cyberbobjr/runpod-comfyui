import os
import json
import threading
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from typing import Dict, Optional
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

MODELS_JSON = "models.json"
ENV_FILE = ".env"
PROGRESS: Dict[str, Dict] = {}
USERS_JSON = "users.json"
JWT_SECRET = "change_this_secret"
JWT_ALGO = "HS256"
JWT_EXP_MINUTES = 60

security = HTTPBearer()
api_router = APIRouter(prefix="/api")

DOWNLOAD_EVENTS = {}  # model_id -> threading.Event

def get_users_file_path():
    """Retourne le chemin complet du fichier users.json selon COMFYUI_MODEL_DIR ou le répertoire courant."""
    base_dir = os.environ.get("COMFYUI_MODEL_DIR", ".")
    return os.path.join(base_dir, USERS_JSON)

def load_users():
    users_path = get_users_file_path()
    if not os.path.exists(users_path):
        # Création d'un utilisateur par défaut si le fichier n'existe pas
        os.makedirs(os.path.dirname(users_path), exist_ok=True)
        with open(users_path, "w", encoding="utf-8") as f:
            json.dump({"admin": "admin"}, f)
    with open(users_path, "r", encoding="utf-8") as f:
        return json.load(f)

def verify_user(username, password):
    users = load_users()
    return users.get(username) == password

def create_jwt(username):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

def decode_jwt(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload["sub"]
    except Exception:
        return None

def protected(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user = decode_jwt(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    return user

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

@api_router.post("/login")
def login(req: LoginRequest):
    if verify_user(req.username, req.password):
        token = create_jwt(req.username)
        return {"token": token}
    raise HTTPException(status_code=401, detail="Identifiants invalides")

@api_router.post("/change_user")
def change_user(req: ChangeUserRequest, user=Depends(protected)):
    users = load_users()
    # Vérifie l'ancien login/mot de passe
    if users.get(req.old_username) != req.old_password:
        raise HTTPException(status_code=401, detail="Invalid current username or password")
    # Empêche de remplacer par un login déjà existant (autre que soi-même)
    if req.new_username != req.old_username and req.new_username in users:
        raise HTTPException(status_code=409, detail="Username already exists")
    # Met à jour le fichier users.json
    del users[req.old_username]
    users[req.new_username] = req.new_password
    users_path = get_users_file_path()
    with open(users_path, "w", encoding="utf-8") as f:
        json.dump(users, f)
    return {"ok": True}

def get_models_base_dir():
    """Retourne le dossier racine des modèles selon la règle COMFYUI_MODEL_DIR/models ou config.BASE_DIR."""
    if os.environ.get("COMFYUI_MODEL_DIR"):
        return os.path.join(os.environ["COMFYUI_MODEL_DIR"], "models")
    else:
        return load_base_dir()

@api_router.get("/models")
def list_models(user=Depends(protected)):
    """Liste tous les modèles du JSON et leur état sur le disque."""
    groups = load_models()
    base_dir = get_models_base_dir()
    result = []
    for group, entries in groups.items():
        for entry in entries:
            dest = entry.get("dest")
            # Remplace ${BASE_DIR} par le chemin déterminé ci-dessus
            path = dest.replace("${BASE_DIR}", base_dir) if dest else None
            exists = os.path.exists(path) if path else False
            model_id = get_model_id(entry)
            progress = PROGRESS.get(model_id, {})
            # Ajout explicite des tags dans la réponse (copie de entry pour ne pas modifier l'original)
            entry_with_tags = dict(entry)
            if "tags" not in entry_with_tags:
                entry_with_tags["tags"] = []
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
    """Lance le téléchargement d'un modèle (url ou git), fusionne les requêtes identiques."""
    model_id = get_model_id(entry)
    url = entry.get("url", "")
    hf_token, civitai_token = read_env_file()
    if "huggingface.co" in url and not hf_token:
        raise HTTPException(status_code=400, detail="Le token HuggingFace est requis pour ce téléchargement.")
    if "civitai.com" in url and not civitai_token:
        raise HTTPException(status_code=400, detail="Le token CivitAI est requis pour ce téléchargement.")

    # Synchronisation des téléchargements concurrents pour le même modèle
    event = DOWNLOAD_EVENTS.get(model_id)
    if event:
        # Un téléchargement est déjà en cours, attendre la fin
        event.wait()
        progress = PROGRESS.get(model_id, {})
        if progress.get("status") == "done":
            return {"ok": True}
        elif progress.get("status") == "error":
            raise HTTPException(status_code=500, detail=progress.get("error", "Erreur lors du téléchargement"))
        else:
            # Statut inattendu, relancer le téléchargement
            pass
    else:
        # Pas de téléchargement en cours, on crée un nouvel event
        event = threading.Event()
        DOWNLOAD_EVENTS[model_id] = event
        PROGRESS[model_id] = {"progress": 0, "status": "downloading"}
        background_tasks.add_task(download_worker, entry, model_id, event)
        return {"ok": True}

def download_worker(entry, model_id, event):
    try:
        hf_token, civitai_token = read_env_file()
        if "git" in entry:
            download_git_entry(entry, model_id)
        else:
            download_url_entry(entry, model_id, hf_token, civitai_token)
        PROGRESS[model_id]["progress"] = 100
        PROGRESS[model_id]["status"] = "done"
    except Exception as e:
        PROGRESS[model_id]["status"] = "error"
        PROGRESS[model_id]["error"] = str(e)
    finally:
        # Signale à tous les threads en attente que le téléchargement est terminé
        event.set()
        # Nettoyage de l'event pour éviter les fuites mémoire
        DOWNLOAD_EVENTS.pop(model_id, None)

def download_git_entry(entry, model_id):
    import subprocess
    base_dir = get_models_base_dir()
    dest_dir = entry["dest"].replace("${BASE_DIR}", base_dir)
    if os.path.exists(dest_dir):
        PROGRESS[model_id]["progress"] = 100
        PROGRESS[model_id]["status"] = "done"
        return
    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
    proc = subprocess.Popen(["git", "clone", entry["git"], dest_dir])
    proc.wait()

def download_url_entry(entry, model_id, hf_token=None, civitai_token=None):
    import requests
    base_dir = get_models_base_dir()
    url = entry["url"]
    dest = entry["dest"].replace("${BASE_DIR}", base_dir)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    headers = entry.get("headers", {})
    # Ajout des tokens si besoin
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
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                PROGRESS[model_id]["progress"] = int(downloaded * 100 / total) if total else 0
    PROGRESS[model_id]["progress"] = 100

@api_router.post("/delete")
def delete_model(entry: dict, user=Depends(protected)):
    """Supprime un modèle du disque."""
    base_dir = get_models_base_dir()
    dest = entry.get("dest")
    if not dest:
        raise HTTPException(status_code=400, detail="Pas de chemin de destination")
    path = dest.replace("${BASE_DIR}", base_dir)
    if os.path.exists(path):
        os.remove(path)
        return {"ok": True}
    return {"ok": False, "msg": "Fichier non trouvé"}

@api_router.post("/progress")
def get_progress(entry: dict = Body(...), user=Depends(protected)):
    """Retourne la progression d'un téléchargement (POST avec entry dans le body)."""
    model_id = get_model_id(entry)
    return PROGRESS.get(model_id, {"progress": 0, "status": "idle"})

@api_router.post("/tokens")
def set_tokens(cfg: TokenConfig, user=Depends(protected)):
    """Définit les jetons d'API dans le fichier .env."""
    write_env_file(cfg.hf_token, cfg.civitai_token)
    return {"ok": True}

@api_router.get("/tokens")
def get_tokens(user=Depends(protected)):
    """Retourne les jetons d'API stockés dans le fichier .env."""
    hf_token, civitai_token = read_env_file()
    return {"hf_token": hf_token, "civitai_token": civitai_token}

def get_env_file_path():
    """Retourne le chemin complet du fichier .env selon COMFYUI_MODEL_DIR ou le répertoire courant."""
    base_dir = os.environ.get("COMFYUI_MODEL_DIR", ".")
    return os.path.join(base_dir, ENV_FILE)

def write_env_file(hf_token: Optional[str], civitai_token: Optional[str]):
    """Écrit les jetons dans le fichier .env."""
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
    """Lit les jetons depuis le fichier .env."""
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
    with open(MODELS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    groups = data.get("groups", {})
    return groups

def get_model_id(entry):
    # Utilise dest comme identifiant unique
    return entry.get("dest") or entry.get("git")

def load_base_dir():
    with open(MODELS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("config", {}).get("BASE_DIR", "")