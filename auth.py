import os
import json
import jwt
import hashlib
import base64
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Constants for JWT authentication
JWT_SECRET = "change_this_secret"
JWT_ALGO = "HS256"
JWT_EXP_MINUTES = 60*8
USERS_JSON = "users.json"

security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2 with JWT_SECRET as salt."""
    salt = JWT_SECRET.encode('utf-8')
    # Use PBKDF2 with SHA256, 100000 iterations
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return base64.b64encode(key).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == hashed

def is_password_hashed(password: str) -> bool:
    """Check if a password is already hashed (base64 encoded, length suggests PBKDF2 output)."""
    try:
        # PBKDF2-SHA256 produces 32 bytes, base64 encoded is 44 chars (with padding)
        decoded = base64.b64decode(password)
        return len(decoded) == 32 and len(password) == 44
    except:
        return False

def get_users_file_path():
    """Returns the full path of the users.json file according to COMFYUI_MODEL_DIR or current directory."""
    base_dir = os.environ.get("COMFYUI_MODEL_DIR", ".")
    return os.path.join(base_dir, USERS_JSON)

def load_users():
    users_path = get_users_file_path()
    if not os.path.exists(users_path):
        # Create a default user if the file doesn't exist
        os.makedirs(os.path.dirname(users_path), exist_ok=True)
        with open(users_path, "w", encoding="utf-8") as f:
            # Store hashed password for default user
            hashed_password = hash_password("admin")
            json.dump({"admin": hashed_password}, f)
    
    with open(users_path, "r", encoding="utf-8") as f:
        users = json.load(f)
    
    # Migrate plain text passwords to hashed passwords
    updated = False
    for username, password in users.items():
        if not is_password_hashed(password):
            users[username] = hash_password(password)
            updated = True
    
    # Save updated users if migration occurred
    if updated:
        with open(users_path, "w", encoding="utf-8") as f:
            json.dump(users, f)
    
    return users

def verify_user(username, password):
    users = load_users()
    stored_password = users.get(username)
    if not stored_password:
        return False
    
    # Handle both hashed and plain passwords for backward compatibility
    if is_password_hashed(stored_password):
        return verify_password(password, stored_password)
    else:
        # Fallback for plain text (shouldn't happen after migration)
        return stored_password == password

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
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user
