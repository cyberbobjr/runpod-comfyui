"""
Workflow Models - Pydantic models for workflow management operations

This module contains all Pydantic models related to workflow management including:
- Workflow file operations
- Upload and download responses
- Workflow metadata
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class WorkflowInfo(BaseModel):
    """Information about a workflow file."""
    filename: str = Field(..., description="Workflow filename")
    path: str = Field(..., description="Full file path")
    size: Optional[int] = Field(None, description="File size in bytes")
    modified: Optional[str] = Field(None, description="Last modified timestamp")
    is_valid: bool = Field(True, description="Whether the workflow JSON is valid")


class WorkflowListResponse(BaseModel):
    """Response with list of workflows."""
    workflows: List[WorkflowInfo] = Field(default_factory=list, description="Available workflows")
    total_count: int = Field(0, description="Total number of workflows")


class WorkflowUploadResponse(BaseModel):
    """Response from workflow upload."""
    ok: bool = Field(..., description="Upload success status")
    message: str = Field(..., description="Upload message")
    filename: str = Field(..., description="Uploaded filename")
    size: Optional[int] = Field(None, description="File size in bytes")


class WorkflowDeleteResponse(BaseModel):
    """Response from workflow deletion."""
    ok: bool = Field(..., description="Deletion success status")
    message: str = Field(..., description="Deletion message")
    filename: str = Field(..., description="Deleted filename")


class WorkflowValidationResponse(BaseModel):
    """Response from workflow validation."""
    is_valid: bool = Field(..., description="Whether workflow is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors if any")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings if any")


class WorkflowContent(BaseModel):
    """Workflow content structure."""
    filename: str = Field(..., description="Workflow filename")
    content: Dict[str, Any] = Field(..., description="Workflow JSON content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Workflow metadata")
