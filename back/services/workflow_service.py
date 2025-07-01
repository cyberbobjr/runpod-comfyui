"""
Workflow Service - Handle workflow management operations

This module contains all business logic for workflow management including:
- Workflow file listing and metadata
- Upload and download operations
- Workflow validation
- File management
"""

import os
import json
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime

from .config_service import ConfigService
from .model_manager import ModelManager
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)


class WorkflowService:
    """
    Workflow management service following Single Responsibility Principle.
    
    **Purpose:** Handles workflow-related operations including:
    - Workflow file listing and metadata extraction
    - Workflow upload and download operations
    - Workflow validation and JSON parsing
    - Workflow file management (create, delete, copy)
    - ComfyUI workflow integration
    
    **SRP Responsibility:** Workflow file operations and validation.
    This service should NOT handle model operations (use ModelManager) or
    authentication (use AuthService).
    """
    
    def __init__(self):
        """Initialize the workflow service."""
        self.workflows_dir = ConfigService.get_workflows_dir()
    
    def ensure_workflows_directory(self) -> None:
        """
        Ensure workflows directory exists.
        
        **Description:** Creates the workflows directory if it doesn't exist.
        **Parameters:** None
        **Returns:** None
        """
        os.makedirs(self.workflows_dir, exist_ok=True)
    
    def list_workflows(self) -> List[str]:
        """
        List all workflow filenames.
        
        **Description:** Returns a list of all .json files in the workflows directory.
        **Parameters:** None
        **Returns:** List of workflow filenames
        """
        if not os.path.exists(self.workflows_dir):
            return []
        
        try:
            files = os.listdir(self.workflows_dir)
            return [f for f in files if f.endswith('.json')]
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            raise
    
    def get_workflow_info(self, filename: str) -> Dict[str, Any]:
        """
        Get detailed information about a workflow file.
        
        **Description:** Returns metadata about a specific workflow file.
        **Parameters:**
        - `filename` (str): Workflow filename
        **Returns:** Dictionary with workflow information
        **Raises:** FileNotFoundError if workflow doesn't exist
        """
        file_path = os.path.join(self.workflows_dir, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Workflow '{filename}' not found")
        
        try:
            stat = os.stat(file_path)
            
            # Validate JSON
            is_valid = True
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError:
                is_valid = False
            
            return {
                'filename': filename,
                'path': file_path,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'is_valid': is_valid
            }
        except Exception as e:
            logger.error(f"Error getting workflow info for {filename}: {e}")
            raise
    
    def list_workflows_with_info(self) -> List[Dict[str, Any]]:
        """
        List all workflows with detailed information.
        
        **Description:** Returns workflow list with metadata for each file.
        **Parameters:** None
        **Returns:** List of workflow information dictionaries
        """
        workflows = []
        filenames = self.list_workflows()
        
        for filename in filenames:
            try:
                info = self.get_workflow_info(filename)
                workflows.append(info)
            except Exception as e:
                logger.warning(f"Could not get info for workflow {filename}: {e}")
                # Add basic info even if full info fails
                workflows.append({
                    'filename': filename,
                    'path': os.path.join(self.workflows_dir, filename),
                    'size': None,
                    'modified': None,
                    'is_valid': False
                })
        
        return sorted(workflows, key=lambda x: x['filename'].lower())
    
    def upload_workflow(self, upload_file) -> Dict[str, Any]:
        """
        Upload a workflow file.
        
        **Description:** Saves an uploaded workflow file to the workflows directory.
        **Parameters:**
        - `upload_file` (UploadFile): FastAPI upload file object
        **Returns:** Dictionary with upload results
        **Raises:** Various file system errors
        """
        if not upload_file.filename:
            raise ValueError("No filename provided")
        
        if not upload_file.filename.endswith('.json'):
            raise ValueError("File must be a JSON file")
        
        self.ensure_workflows_directory()
        file_path = os.path.join(self.workflows_dir, upload_file.filename)
        
        try:
            # Save the file
            with open(file_path, "wb") as f:
                shutil.copyfileobj(upload_file.file, f)
            
            # Validate JSON content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                # Remove invalid file
                os.remove(file_path)
                raise ValueError(f"Invalid JSON content: {str(e)}")
            
            # Get file stats
            stat = os.stat(file_path)
            
            logger.info(f"Workflow '{upload_file.filename}' uploaded successfully")
            
            return {
                'filename': upload_file.filename,
                'size': stat.st_size,
                'path': file_path
            }
        
        except Exception as e:
            logger.error(f"Error uploading workflow {upload_file.filename}: {e}")
            # Clean up partial file if it exists
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            raise
    
    def get_workflow_content(self, filename: str) -> Dict[str, Any]:
        """
        Get workflow JSON content.
        
        **Description:** Loads and returns the JSON content of a workflow file.
        **Parameters:**
        - `filename` (str): Workflow filename
        **Returns:** Dictionary with workflow JSON content
        **Raises:** FileNotFoundError if workflow doesn't exist, ValueError for invalid JSON
        """
        file_path = os.path.join(self.workflows_dir, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Workflow '{filename}' not found")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            return {
                'filename': filename,
                'content': content,
                'metadata': {
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
            }
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in workflow '{filename}': {str(e)}")
        except Exception as e:
            logger.error(f"Error reading workflow {filename}: {e}")
            raise
    
    def get_workflow_file_path(self, filename: str) -> str:
        """
        Get the full path to a workflow file.
        
        **Description:** Returns the absolute path to a workflow file with validation.
        **Parameters:**
        - `filename` (str): Workflow filename
        **Returns:** Absolute file path
        **Raises:** FileNotFoundError if workflow doesn't exist
        """
        file_path = os.path.join(self.workflows_dir, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Workflow '{filename}' not found")
        
        return file_path
    
    def delete_workflow(self, filename: str) -> None:
        """
        Delete a workflow file.
        
        **Description:** Removes a workflow file from the workflows directory.
        **Parameters:**
        - `filename` (str): Workflow filename to delete
        **Returns:** None
        **Raises:** FileNotFoundError if workflow doesn't exist
        """
        file_path = os.path.join(self.workflows_dir, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Workflow '{filename}' not found")
        
        try:
            os.remove(file_path)
            logger.info(f"Workflow '{filename}' deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting workflow {filename}: {e}")
            raise
    
    def validate_workflow(self, filename: str) -> Dict[str, Any]:
        """
        Validate a workflow file.
        
        **Description:** Validates workflow JSON structure and content.
        **Parameters:**
        - `filename` (str): Workflow filename to validate
        **Returns:** Dictionary with validation results
        **Raises:** FileNotFoundError if workflow doesn't exist
        """
        file_path = os.path.join(self.workflows_dir, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Workflow '{filename}' not found")
        
        errors = []
        warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            # Basic validation checks
            if not isinstance(content, dict):
                errors.append("Workflow must be a JSON object")
            else:
                # Check for common ComfyUI workflow structure
                if 'nodes' not in content and 'workflow' not in content:
                    warnings.append("Workflow doesn't appear to have standard ComfyUI structure")
                
                # Check for empty content
                if not content:
                    warnings.append("Workflow appears to be empty")
            
            return {
                'is_valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
        
        except json.JSONDecodeError as e:
            return {
                'is_valid': False,
                'errors': [f"Invalid JSON: {str(e)}"],
                'warnings': []
            }
        except Exception as e:
            logger.error(f"Error validating workflow {filename}: {e}")
            return {
                'is_valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': []
            }
    
    def workflow_exists(self, filename: str) -> bool:
        """
        Check if a workflow file exists.
        
        **Description:** Checks if a workflow file exists in the workflows directory.
        **Parameters:**
        - `filename` (str): Workflow filename to check
        **Returns:** True if workflow exists, False otherwise
        """
        file_path = os.path.join(self.workflows_dir, filename)
        return os.path.exists(file_path)
