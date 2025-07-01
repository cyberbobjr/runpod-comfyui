"""
File Manager Models - Pydantic models for file management operations

This module contains all Pydantic models related to file management including:
- File and directory operations
- Upload/download requests
- File properties and metadata
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class FileInfo(BaseModel):
    """Information about a file or directory."""
    name: str = Field(..., description="File or directory name")
    path: str = Field(..., description="Full path")
    type: str = Field(..., description="Type: file or directory")
    size: Optional[int] = Field(None, description="File size in bytes")
    modified: Optional[str] = Field(None, description="Last modified timestamp")
    permissions: Optional[str] = Field(None, description="File permissions")
    is_registered: bool = Field(False, description="Whether file is registered in models.json")


class DirectoryListing(BaseModel):
    """Directory contents listing."""
    path: str = Field(..., description="Directory path")
    files: List[FileInfo] = Field(default_factory=list, description="Files in directory")
    directories: List[FileInfo] = Field(default_factory=list, description="Subdirectories")


class FileOperationRequest(BaseModel):
    """Request for file operations like copy, move, delete."""
    source_path: str = Field(..., description="Source file or directory path")
    target_path: Optional[str] = Field(None, description="Target path for copy/move operations")


class RenameRequest(BaseModel):
    """Request to rename a file or directory."""
    old_path: str = Field(..., description="Current file path")
    new_name: str = Field(..., description="New file name")


class CreateDirectoryRequest(BaseModel):
    """Request to create a new directory."""
    path: str = Field(..., description="Directory path to create")
    recursive: bool = Field(True, description="Create parent directories if needed")


class FilePropertiesResponse(BaseModel):
    """File properties response."""
    name: str = Field(..., description="File name")
    path: str = Field(..., description="Full path")
    size: int = Field(..., description="File size in bytes")
    type: str = Field(..., description="File type")
    created: Optional[str] = Field(None, description="Creation timestamp")
    modified: str = Field(..., description="Last modified timestamp")
    permissions: str = Field(..., description="File permissions")
    is_registered: bool = Field(False, description="Whether file is registered")


class UploadResponse(BaseModel):
    """Response from file upload."""
    ok: bool = Field(..., description="Upload success status")
    message: str = Field(..., description="Upload message")
    filename: str = Field(..., description="Uploaded filename")
    path: str = Field(..., description="Full file path")
    size: int = Field(..., description="File size in bytes")


class ModelsInfoResponse(BaseModel):
    """Response with model files information."""
    registered_models: Dict[str, Any] = Field(default_factory=dict, description="Registered models from models.json")
    unregistered_files: List[FileInfo] = Field(default_factory=list, description="Files not in models.json")
    total_files: int = Field(0, description="Total number of files")
    total_size: int = Field(0, description="Total size in bytes")


class FileOperationResponse(BaseModel):
    """Response from file operations."""
    ok: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Operation message")
    operation: str = Field(..., description="Type of operation performed")
    source_path: Optional[str] = Field(None, description="Source file path")
    target_path: Optional[str] = Field(None, description="Target file path")
