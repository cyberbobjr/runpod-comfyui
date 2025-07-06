from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class ModelFileInfo(BaseModel):
    """Model file information structure"""
    name: str = Field(..., description="Model file name")
    path: str = Field(..., description="Full path to the model file")
    relative_path: str = Field(..., description="Relative path from models directory")
    subdirectory: str = Field(..., description="Subdirectory within models folder")
    size: int = Field(..., description="File size in bytes")
    size_mb: float = Field(..., description="File size in megabytes")
    extension: str = Field(..., description="File extension")
    type: List[str] = Field(..., description="List of possible model types")
    identified_type: Optional[str] = Field(None, description="Advanced identification result")
    exists: bool = Field(..., description="Whether the file exists")
    error: Optional[str] = Field(None, description="Error message if any")

class ModelCategoryInfo(BaseModel):
    """Model category statistics"""
    count: int = Field(..., description="Number of models in this category")
    total_size_mb: float = Field(..., description="Total size of all models in MB")

class ModelScanResponse(BaseModel):
    """Complete model scan response"""
    models_directory: str = Field(..., description="Path to the models directory")
    total_models: int = Field(..., description="Total number of models found")
    models: Dict[str, List[ModelFileInfo]] = Field(..., description="Models organized by category")
    error: Optional[str] = Field(None, description="Error message if scan failed")

class ModelSummaryResponse(BaseModel):
    """Model summary response"""
    total_models: int = Field(..., description="Total number of models found")
    models_directory: str = Field(..., description="Path to the models directory")
    categories: Dict[str, ModelCategoryInfo] = Field(..., description="Summary by category")
    error: Optional[str] = Field(None, description="Error message if scan failed")

class ModelSearchResponse(BaseModel):
    """Model search response"""
    query: str = Field(..., description="Search query used")
    category: Optional[str] = Field(None, description="Category filter applied")
    matches: Dict[str, List[ModelFileInfo]] = Field(..., description="Matching models by category")
    total_matches: int = Field(..., description="Total number of matching models")
    error: Optional[str] = Field(None, description="Error message if search failed")
