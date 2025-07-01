"""
File Manager Service - Handle all file management operations

This module contains all business logic for file management including:
- Directory listing and navigation
- File operations (copy, move, delete, rename)
- File upload and download
- Model file registration tracking
"""

import os
import shutil
import json
from typing import List, Dict, Any, Optional

from .config_service import ConfigService
from datetime import datetime
from .model_manager import ModelManager
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)


class FileManagerService:
    """
    File system management service following Single Responsibility Principle.
    
    **Purpose:** Handles secure file system operations including:
    - Directory listing and navigation with security checks
    - File operations (copy, move, delete, rename)
    - File upload and download handling
    - Model file registration and tracking
    - File system integrity and security validation
    
    **SRP Responsibility:** Secure file system operations and file management.
    This service should NOT handle model configuration (use ModelManager) or
    authentication (use AuthService).
    """
    
    def __init__(self):
        """Initialize the file manager service."""
        self.base_dir = ConfigService.get_base_dir()
    
    def safe_join(self, base: str, *paths: str) -> str:
        """
        Safely join paths to prevent directory traversal attacks.
        
        **Description:** Validates that the resulting path is within the base directory.
        **Parameters:**
        - `base` (str): Base directory path
        - `paths` (str): Path components to join
        **Returns:** Safe absolute path
        **Raises:** HTTPException if path is outside base directory
        """
        base = os.path.abspath(base)
        path = os.path.abspath(os.path.join(base, *paths))
        if not path.startswith(base):
            raise ValueError("Access denied: path outside allowed directory")
        return path
    
    def get_registered_models(self) -> Dict[str, Any]:
        """
        Get all registered models from models.json.
        
        **Description:** Retrieves model information from models.json with file paths.
        **Parameters:** None
        **Returns:** Dictionary of registered model files with metadata
        """
        registered_files = {}
        
        models_path = ModelManager.get_models_json_path()
        if not models_path or not os.path.isfile(models_path):
            logger.warning("No models.json file found")
            return registered_files
        
        try:
            with open(models_path, 'r', encoding='utf-8') as f:
                models_data = json.load(f)
            
            # Process each group
            for group_name, models in models_data.get('groups', {}).items():
                for model in models:
                    dest = model.get('dest')
                    if dest:
                        # Normalize path
                        full_path = os.path.join(self.base_dir, dest)
                        normalized_path = os.path.normpath(full_path)
                        
                        # Get file size if it exists
                        file_size = 0
                        if os.path.isfile(normalized_path):
                            try:
                                file_size = os.path.getsize(normalized_path)
                            except OSError:
                                pass
                        
                        registered_files[normalized_path] = {
                            'group': group_name,
                            'model_info': model,
                            'size': file_size,
                            'exists': os.path.isfile(normalized_path)
                        }
        
        except Exception as e:
            logger.error(f"Error reading models.json: {e}")
        
        return registered_files
    
    def list_directories(self, path: str = "") -> List[Dict[str, Any]]:
        """
        List directories in the specified path.
        
        **Description:** Returns list of directories with metadata.
        **Parameters:**
        - `path` (str): Relative path from base directory
        **Returns:** List of directory information dictionaries
        """
        try:
            full_path = self.safe_join(self.base_dir, path) if path else self.base_dir
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"Directory not found: {path}")
            
            directories = []
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                if os.path.isdir(item_path):
                    try:
                        stat = os.stat(item_path)
                        directories.append({
                            'name': item,
                            'path': os.path.relpath(item_path, self.base_dir),
                            'type': 'directory',
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                    except OSError as e:
                        logger.warning(f"Could not stat directory {item}: {e}")
            
            return sorted(directories, key=lambda x: x['name'].lower())
        
        except Exception as e:
            logger.error(f"Error listing directories: {e}")
            raise
    
    def list_all_directories(self) -> List[Dict[str, Any]]:
        """
        Recursively list all directories in a tree structure.
        
        **Description:** Returns a hierarchical tree structure of all directories with children nested.
        **Parameters:** None
        **Returns:** List of root directories with nested children structure
        """
        def _build_directory_tree(path: str) -> List[Dict[str, Any]]:
            """Recursively build directory tree structure."""
            directories = []
            
            try:
                if not os.path.exists(path):
                    return directories
                
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        try:
                            stat = os.stat(item_path)
                            directory_info = {
                                'name': item,
                                'path': os.path.relpath(item_path, self.base_dir),
                                'type': 'directory',
                                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                'children': _build_directory_tree(item_path)
                            }
                            directories.append(directory_info)
                        except OSError as e:
                            logger.warning(f"Could not stat directory {item}: {e}")
                
                return sorted(directories, key=lambda x: x['name'].lower())
            
            except Exception as e:
                logger.warning(f"Error reading directory {path}: {e}")
                return directories
        
        try:
            return _build_directory_tree(self.base_dir)
        
        except Exception as e:
            logger.error(f"Error listing all directories: {e}")
            raise
    
    def list_files(self, path: str = "", extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        List files in the specified directory.
        
        **Description:** Returns files with metadata and registration status.
        **Parameters:**
        - `path` (str): Relative path from base directory
        - `extensions` (List[str], optional): Filter by file extensions
        **Returns:** Dictionary with files, directories, and metadata
        """
        try:
            full_path = self.safe_join(self.base_dir, path) if path else self.base_dir
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"Directory not found: {path}")
            
            registered_models = self.get_registered_models()
            files = []
            directories = []
            total_size = 0
            
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                
                try:
                    stat = os.stat(item_path)
                    item_info = {
                        'name': item,
                        'path': os.path.relpath(item_path, self.base_dir),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'permissions': oct(stat.st_mode)[-3:]
                    }
                    
                    if os.path.isdir(item_path):
                        item_info['type'] = 'directory'
                        directories.append(item_info)
                    else:
                        # Filter by extensions if specified
                        if extensions:
                            _, ext = os.path.splitext(item.lower())
                            if ext not in [e.lower() for e in extensions]:
                                continue
                        
                        item_info.update({
                            'type': 'file',
                            'size': stat.st_size,
                            'is_registered': os.path.abspath(item_path) in registered_models
                        })
                        total_size += stat.st_size
                        files.append(item_info)
                
                except OSError as e:
                    logger.warning(f"Could not stat item {item}: {e}")
            
            return {
                'path': path,
                'files': sorted(files, key=lambda x: x['name'].lower()),
                'directories': sorted(directories, key=lambda x: x['name'].lower()),
                'total_files': len(files),
                'total_size': total_size
            }
        
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            raise
    
    def copy_file(self, source_path: str, target_path: str) -> None:
        """
        Copy a file or directory.
        
        **Description:** Copies files or directories with safety checks.
        **Parameters:**
        - `source_path` (str): Source file path
        - `target_path` (str): Target file path
        **Returns:** None
        **Raises:** FileNotFoundError, PermissionError, or other OS errors
        """
        try:
            source = self.safe_join(self.base_dir, source_path)
            target = self.safe_join(self.base_dir, target_path)
            
            if not os.path.exists(source):
                raise FileNotFoundError(f"Source not found: {source_path}")
            
            if os.path.exists(target):
                raise FileExistsError(f"Target already exists: {target_path}")
            
            # Create target directory if needed
            target_dir = os.path.dirname(target)
            os.makedirs(target_dir, exist_ok=True)
            
            if os.path.isdir(source):
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
            
            logger.info(f"Successfully copied {source_path} to {target_path}")
        
        except Exception as e:
            logger.error(f"Error copying {source_path} to {target_path}: {e}")
            raise
    
    def delete_file(self, file_path: str) -> None:
        """
        Delete a file or directory.
        
        **Description:** Safely deletes files or directories with validation.
        **Parameters:**
        - `file_path` (str): Path to file or directory to delete
        **Returns:** None
        **Raises:** FileNotFoundError, PermissionError, or other OS errors
        """
        try:
            full_path = self.safe_join(self.base_dir, file_path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            
            logger.info(f"Successfully deleted {file_path}")
        
        except Exception as e:
            logger.error(f"Error deleting {file_path}: {e}")
            raise
    
    def rename_file(self, old_path: str, new_name: str) -> str:
        """
        Rename a file or directory.
        
        **Description:** Renames a file or directory with validation.
        **Parameters:**
        - `old_path` (str): Current file path
        - `new_name` (str): New file name
        **Returns:** New file path
        **Raises:** FileNotFoundError, FileExistsError, or other OS errors
        """
        try:
            old_full_path = self.safe_join(self.base_dir, old_path)
            
            if not os.path.exists(old_full_path):
                raise FileNotFoundError(f"File not found: {old_path}")
            
            # Build new path
            directory = os.path.dirname(old_full_path)
            new_full_path = os.path.join(directory, new_name)
            
            if os.path.exists(new_full_path):
                raise FileExistsError(f"File already exists: {new_name}")
            
            os.rename(old_full_path, new_full_path)
            new_relative_path = os.path.relpath(new_full_path, self.base_dir)
            
            logger.info(f"Successfully renamed {old_path} to {new_relative_path}")
            return new_relative_path
        
        except Exception as e:
            logger.error(f"Error renaming {old_path} to {new_name}: {e}")
            raise
    
    def get_file_properties(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed file properties.
        
        **Description:** Returns comprehensive file metadata and registration status.
        **Parameters:**
        - `file_path` (str): File path to inspect
        **Returns:** Dictionary with file properties
        **Raises:** FileNotFoundError if file doesn't exist
        """
        try:
            full_path = self.safe_join(self.base_dir, file_path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            stat = os.stat(full_path)
            registered_models = self.get_registered_models()
            
            properties = {
                'name': os.path.basename(full_path),
                'path': file_path,
                'size': stat.st_size,
                'type': 'directory' if os.path.isdir(full_path) else 'file',
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'permissions': oct(stat.st_mode)[-3:],
                'is_registered': os.path.abspath(full_path) in registered_models
            }
            
            return properties
        
        except Exception as e:
            logger.error(f"Error getting properties for {file_path}: {e}")
            raise
    
    def create_directory(self, dir_path: str, recursive: bool = True) -> None:
        """
        Create a new directory.
        
        **Description:** Creates a directory with optional recursive creation.
        **Parameters:**
        - `dir_path` (str): Directory path to create
        - `recursive` (bool): Create parent directories if needed
        **Returns:** None
        **Raises:** FileExistsError if directory exists, OSError for other issues
        """
        try:
            full_path = self.safe_join(self.base_dir, dir_path)
            
            if os.path.exists(full_path):
                raise FileExistsError(f"Directory already exists: {dir_path}")
            
            os.makedirs(full_path, exist_ok=False)
            logger.info(f"Successfully created directory {dir_path}")
        
        except Exception as e:
            logger.error(f"Error creating directory {dir_path}: {e}")
            raise
    
    def save_uploaded_file(self, upload_file, target_path: str) -> Dict[str, Any]:
        """
        Save an uploaded file to the specified path.
        
        **Description:** Handles file upload with validation and metadata.
        **Parameters:**
        - `upload_file` (UploadFile): FastAPI upload file object
        - `target_path` (str): Target file path
        **Returns:** Dictionary with upload results
        **Raises:** Various file system errors
        """
        try:
            full_path = self.safe_join(self.base_dir, target_path, upload_file.filename)
            
            # Create target directory if needed
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Save file
            with open(full_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
            
            # Get file stats
            stat = os.stat(full_path)
            relative_path = os.path.relpath(full_path, self.base_dir)
            
            logger.info(f"Successfully uploaded file {upload_file.filename} to {relative_path}")
            
            return {
                'filename': upload_file.filename,
                'path': relative_path,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error uploading file {upload_file.filename}: {e}")
            raise
    
    def get_models_info(self) -> Dict[str, Any]:
        """
        Get comprehensive model file information.
        
        **Description:** Returns registered models and unregistered files analysis.
        **Parameters:** None
        **Returns:** Dictionary with model files analysis
        """
        try:
            registered_models = self.get_registered_models()
            
            # Find all model files (common extensions)
            model_extensions = ['.ckpt', '.safetensors', '.pt', '.pth', '.bin']
            all_model_files = []
            total_size = 0
            
            for root, dirs, files in os.walk(self.base_dir):
                for file in files:
                    _, ext = os.path.splitext(file.lower())
                    if ext in model_extensions:
                        file_path = os.path.join(root, file)
                        try:
                            stat = os.stat(file_path)
                            relative_path = os.path.relpath(file_path, self.base_dir)
                            
                            file_info = {
                                'name': file,
                                'path': relative_path,
                                'size': stat.st_size,
                                'type': 'file',
                                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                'is_registered': os.path.abspath(file_path) in registered_models
                            }
                            
                            all_model_files.append(file_info)
                            total_size += stat.st_size
                        
                        except OSError as e:
                            logger.warning(f"Could not stat model file {file}: {e}")
            
            # Separate registered and unregistered
            unregistered_files = [f for f in all_model_files if not f['is_registered']]
            
            return {
                'registered_models': registered_models,
                'unregistered_files': unregistered_files,
                'total_files': len(all_model_files),
                'total_size': total_size
            }
        
        except Exception as e:
            logger.error(f"Error getting models info: {e}")
            raise
