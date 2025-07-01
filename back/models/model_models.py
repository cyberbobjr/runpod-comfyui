from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class ModelEntry(BaseModel):
    """Model entry definition."""
    url: Optional[str] = Field(None, description="Download URL for the model")
    dest: Optional[str] = Field(None, description="Destination path for the model file")
    git: Optional[str] = Field(None, description="Git repository URL")
    type: Optional[str] = Field(None, description="Type of model")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")
    src: Optional[str] = Field(None, description="Source page URL")
    hash: Optional[str] = Field(None, description="File hash for verification")
    size: Optional[int] = Field(None, description="File size in bytes")
    headers: Optional[Dict[str, str]] = Field(None, description="Custom HTTP headers for download")
    system_requirements: Optional[Dict[str, Any]] = Field(None, description="System requirements")


class ModelEntryRequest(BaseModel):
    """Request to manage a model entry."""
    group: str = Field(..., description="Group name")
    entry: ModelEntry = Field(..., description="Model entry data")


class ModelGroupRequest(BaseModel):
    """Request for group operations."""
    group: str = Field(..., description="Group name")


class UpdateModelGroupRequest(BaseModel):
    """Request to rename a model group."""
    old_group: str = Field(..., description="Current group name")
    new_group: str = Field(..., description="New group name")


class ConfigUpdateRequest(BaseModel):
    """Request to update configuration."""
    base_dir: str = Field(..., description="Base directory path")


class ModelFilters(BaseModel):
    """Model filtering criteria."""
    include_tags: List[str] = Field(default_factory=list, description="Tags that must be present")
    exclude_tags: List[str] = Field(default_factory=list, description="Tags that must not be present")


class HardwareProfile(BaseModel):
    """Hardware profile definition."""
    description: str = Field(..., description="Profile description")
    model_filters: ModelFilters = Field(..., description="Model filtering criteria")


class Bundle(BaseModel):
    """Bundle definition."""
    description: str = Field(..., description="Bundle description")
    workflows: List[str] = Field(..., description="Workflow names included in bundle")
    models: List[str] = Field(..., description="Model groups included in bundle")
    hardware_profiles: Dict[str, HardwareProfile] = Field(default_factory=dict, description="Hardware profiles")
    workflow_params: Optional[Dict[str, Any]] = Field(None, description="Workflow parameters")


class BundleRequest(BaseModel):
    """Request to manage a bundle."""
    name: str = Field(..., description="Bundle name")
    bundle: Bundle = Field(..., description="Bundle data")


class BundleInstallRequest(BaseModel):
    """Request to install a bundle."""
    bundle: str = Field(..., description="Bundle name to install")
    profile: str = Field(..., description="Hardware profile to use")


class DownloadRequest(BaseModel):
    """Request to download a model."""
    entry: ModelEntry = Field(..., description="Model entry to download")


class ProgressRequest(BaseModel):
    """Request to check download progress."""
    entry: ModelEntry = Field(..., description="Model entry to check progress for")


class StopDownloadRequest(BaseModel):
    """Request to stop a download."""
    entry: ModelEntry = Field(..., description="Model entry to stop downloading")


class DeleteModelRequest(BaseModel):
    """Request to delete a model file."""
    entry: ModelEntry = Field(..., description="Model entry to delete from disk")
