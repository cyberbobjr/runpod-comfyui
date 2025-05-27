import os
import json
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Constants for JWT authentication
JWT_SECRET = "change_this_secret"
JWT_ALGO = "HS256"
JWT_EXP_MINUTES = 60
USERS_JSON = "users.json"

security = HTTPBearer()

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
