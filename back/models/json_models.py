"""
JSON Models - Pydantic models for JSON model management operations

This module contains Pydantic models related to JSON model management including:
- Configuration management
- Group ordering
- Path normalization
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class ConfigResponse(BaseModel):
    """Configuration response."""
    BASE_DIR: str = Field(..., description="Current base directory path")
    source: str = Field(..., description="Source of BASE_DIR (user_config, models_json, environment, default)")


class ConfigUpdateRequest(BaseModel):
    """Request to update configuration."""
    base_dir: str = Field(..., description="New base directory path")


class GroupOrderRequest(BaseModel):
    """Request to update group order."""
    order: List[str] = Field(..., description="List of group names in the desired order")


class GroupOrderResponse(BaseModel):
    """Response with current group order."""
    order: List[str] = Field(..., description="Current order of groups")


class PathNormalizationRequest(BaseModel):
    """Request for path normalization."""
    path: str = Field(..., description="Path to normalize")
    base_dir: Optional[str] = Field(None, description="Base directory for relative paths")


class PathNormalizationResponse(BaseModel):
    """Response with normalized path."""
    original_path: str = Field(..., description="Original path")
    normalized_path: str = Field(..., description="Normalized path")
    is_relative: bool = Field(..., description="Whether path is relative to BASE_DIR")


class ModelsDataResponse(BaseModel):
    """Response with complete models data."""
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration settings")
    groups: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict, description="Model groups")