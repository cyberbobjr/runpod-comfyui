from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime


class ModelDefinition(BaseModel):
    """Model definition within a bundle."""
    url: str = Field(..., description="Download URL for the model")
    dest: str = Field(..., description="Destination path for the model")
    git: str = Field("", description="Git repository URL")
    type: str = Field(..., description="Type of model")
    tags: List[str] = Field(default_factory=list, description="Model tags")
    src: str = Field("", description="Source page URL")
    hash: str = Field("", description="File hash for verification")
    size: Optional[int] = Field(None, description="File size in bytes")


class HardwareProfile(BaseModel):
    """Hardware profile definition for bundles."""
    description: str = Field(..., description="Profile description")
    models: List[ModelDefinition] = Field(default_factory=list, description="Models in this profile")


class Bundle(BaseModel):
    """Complete bundle definition."""
    id: str = Field(..., description="Unique bundle identifier")
    name: str = Field(..., description="Bundle name")
    description: Optional[str] = Field("", description="Bundle description")
    version: str = Field("1.0.0", description="Bundle version")
    author: Optional[str] = Field(None, description="Bundle author")
    website: Optional[str] = Field(None, description="Author website")
    workflows: List[str] = Field(default_factory=list, description="Workflow files included")
    hardware_profiles: Dict[str, HardwareProfile] = Field(default_factory=dict, description="Hardware profiles")
    workflow_params: Optional[Dict[str, Any]] = Field(None, description="Workflow parameters")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class BundleCreate(BaseModel):
    """Request to create a new bundle."""
    name: str = Field(..., description="Bundle name")
    description: Optional[str] = Field("", description="Bundle description")
    version: str = Field("1.0.0", description="Bundle version")
    author: Optional[str] = Field(None, description="Bundle author")
    website: Optional[str] = Field(None, description="Author website")
    workflows: List[str] = Field(default_factory=list, description="Workflow files")
    hardware_profiles: Dict[str, HardwareProfile] = Field(default_factory=dict, description="Hardware profiles")
    workflow_params: Optional[Dict[str, Any]] = Field(None, description="Workflow parameters")


class BundleUpdate(BaseModel):
    """Request to update an existing bundle."""
    name: Optional[str] = Field(None, description="Bundle name")
    description: Optional[str] = Field(None, description="Bundle description")
    version: Optional[str] = Field(None, description="Bundle version")
    author: Optional[str] = Field(None, description="Bundle author")
    website: Optional[str] = Field(None, description="Author website")
    workflows: Optional[List[str]] = Field(None, description="Workflow files")
    hardware_profiles: Optional[Dict[str, HardwareProfile]] = Field(None, description="Hardware profiles")
    workflow_params: Optional[Dict[str, Any]] = Field(None, description="Workflow parameters")


class BundleInstallRequest(BaseModel):
    """Request to install a bundle."""
    bundle_id: str = Field(..., description="Bundle ID to install")
    profile: str = Field(..., description="Hardware profile to use")
    workflow_params: Optional[Dict[str, Any]] = Field(None, description="Override workflow parameters")


class BundleInstallStatus(BaseModel):
    """Installation status response."""
    bundle_id: str = Field(..., description="Bundle identifier")
    status: str = Field(..., description="Installation status")
    progress: int = Field(0, description="Installation progress percentage")
    message: Optional[str] = Field(None, description="Status message")
    installed_models: List[str] = Field(default_factory=list, description="Successfully installed models")
    failed_models: List[str] = Field(default_factory=list, description="Failed model installations")


class BundleExportRequest(BaseModel):
    """Request to export a bundle."""
    bundle_id: str = Field(..., description="Bundle ID to export")
    include_models: bool = Field(False, description="Include model files in export")


class BundleImportRequest(BaseModel):
    """Request to import a bundle."""
    overwrite: bool = Field(False, description="Overwrite existing bundle if it exists")


class BundleInstallResponse(BaseModel):
    """Response from bundle installation."""
    ok: bool = Field(..., description="Installation success status")
    message: str = Field(..., description="Installation message")
    results: Optional[Dict[str, List[str]]] = Field(None, description="Installation results")


class BundleDuplicateRequest(BaseModel):
    """Request to duplicate a bundle."""
    new_name: str = Field(..., description="Name for the new bundle")
    description: Optional[str] = Field(None, description="Description for the new bundle")
