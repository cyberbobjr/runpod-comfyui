import os
import json
import jwt
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import HTTPException
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Constants for JWT authentication
JWT_SECRET = "change_this_secret"
JWT_ALGO = "HS256"
JWT_EXP_MINUTES = 60*8*8
USERS_JSON = "users.json"


class AuthService:
    """
    Authentication and authorization service following Single Responsibility Principle.
    
    **Purpose:** Handles all authentication-related operations including:
    - User credential management (create, verify, update)
    - Password hashing and validation
    - JWT token generation and validation
    - User session management
    - Authentication state persistence
    
    **SRP Responsibility:** User authentication and authorization.
    This service should NOT handle configuration (use ConfigService) or
    model operations (use appropriate model services).
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using PBKDF2 with JWT_SECRET as salt.
        
        **Description:** Securely hashes a password using PBKDF2 with SHA256.
        **Parameters:**
        - `password` (str): The plain text password to hash
        **Returns:** str containing the base64-encoded hash
        """
        salt = JWT_SECRET.encode('utf-8')
        # Use PBKDF2 with SHA256, 100000 iterations
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return base64.b64encode(key).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.
        
        **Description:** Verifies a plain text password against its stored hash.
        **Parameters:**
        - `password` (str): The plain text password to verify
        - `hashed` (str): The stored hash to compare against
        **Returns:** bool indicating if the password is correct
        """
        return AuthService.hash_password(password) == hashed

    @staticmethod
    def is_password_hashed(password: str) -> bool:
        """
        Check if a password is already hashed (base64 encoded, length suggests PBKDF2 output).
        
        **Description:** Determines if a password string is already hashed or is plain text.
        **Parameters:**
        - `password` (str): The password string to check
        **Returns:** bool indicating if the password is already hashed
        """
        try:
            # PBKDF2-SHA256 produces 32 bytes, base64 encoded is 44 chars (with padding)
            decoded = base64.b64decode(password)
            return len(decoded) == 32 and len(password) == 44
        except:
            return False

    @staticmethod
    def get_users_file_path() -> str:
        """
        Returns the full path of the users.json file according to COMFYUI_MODEL_DIR or current directory.
        
        **Description:** Constructs the path to the users.json file.
        **Parameters:** None
        **Returns:** str containing the path to users.json
        """
        base_dir = os.environ.get("COMFYUI_MODEL_DIR", ".")
        return os.path.join(base_dir, USERS_JSON)

    @staticmethod
    def load_users() -> Dict[str, str]:
        """
        Load users from the users.json file with automatic migration from plain text passwords.
        
        **Description:** Loads user data and migrates plain text passwords to hashed passwords.
        **Parameters:** None
        **Returns:** Dict containing username to password hash mappings
        """
        users_path = AuthService.get_users_file_path()
        if not os.path.exists(users_path):
            # Create a default user if the file doesn't exist
            os.makedirs(os.path.dirname(users_path), exist_ok=True)
            with open(users_path, "w", encoding="utf-8") as f:
                # Store hashed password for default user
                hashed_password = AuthService.hash_password("admin")
                json.dump({"admin": hashed_password}, f)
        
        with open(users_path, "r", encoding="utf-8") as f:
            users = json.load(f)
        
        # Migrate plain text passwords to hashed passwords
        updated = False
        for username, password in users.items():
            if not AuthService.is_password_hashed(password):
                users[username] = AuthService.hash_password(password)
                updated = True
        
        # Save updated users if migration occurred
        if updated:
            with open(users_path, "w", encoding="utf-8") as f:
                json.dump(users, f)
        
        return users

    @staticmethod
    def verify_user(username: str, password: str) -> bool:
        """
        Verify user credentials.
        
        **Description:** Verifies username and password against stored user data.
        **Parameters:**
        - `username` (str): The username to verify
        - `password` (str): The password to verify
        **Returns:** bool indicating if credentials are valid
        """
        users = AuthService.load_users()
        stored_password = users.get(username)
        if not stored_password:
            return False
        
        # Handle both hashed and plain passwords for backward compatibility
        if AuthService.is_password_hashed(stored_password):
            return AuthService.verify_password(password, stored_password)
        else:
            # Fallback for plain text (shouldn't happen after migration)
            return stored_password == password

    @staticmethod
    def create_jwt(username: str) -> str:
        """
        Create a JWT token for a user.
        
        **Description:** Creates a signed JWT token with expiration for user authentication.
        **Parameters:**
        - `username` (str): The username to encode in the token
        **Returns:** str containing the JWT token
        """
        payload = {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

    @staticmethod
    def decode_jwt(token: str) -> Optional[str]:
        """
        Decode and verify a JWT token.
        
        **Description:** Decodes a JWT token and returns the username if valid.
        **Parameters:**
        - `token` (str): The JWT token to decode
        **Returns:** str containing the username, or None if invalid
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
            return payload["sub"]
        except Exception:
            return None

    @staticmethod
    def change_user_credentials(old_username: str, old_password: str, 
                              new_username: str, new_password: str) -> bool:
        """
        Change user credentials.
        
        **Description:** Updates user credentials in the system.
        **Parameters:**
        - `old_username` (str): Current username
        - `old_password` (str): Current password
        - `new_username` (str): New username
        - `new_password` (str): New password
        **Returns:** bool indicating success
        """
        users = AuthService.load_users()
        
        # Check old login/password using verify_user for proper hash verification
        if not AuthService.verify_user(old_username, old_password):
            raise HTTPException(status_code=401, detail="Invalid current username or password")
        
        # Prevent replacing with an already existing login (other than oneself)
        if new_username != old_username and new_username in users:
            raise HTTPException(status_code=409, detail="Username already exists")
        
        # Update the users.json file with hashed password
        del users[old_username]
        users[new_username] = AuthService.hash_password(new_password)
        users_path = AuthService.get_users_file_path()
        with open(users_path, "w", encoding="utf-8") as f:
            json.dump(users, f)
        
        return True
