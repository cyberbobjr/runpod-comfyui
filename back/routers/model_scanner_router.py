"""
Model Scanner Router - Handle model discovery and analysis API routes

This module contains all API routes for scanning and analyzing model files including:
- Full model directory scanning
- Model categorization and classification
- Model search and filtering
- Model summary statistics
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from ..services.auth_middleware import protected
from ..services.model_scanner_service import ModelScannerService
from ..models.model_scanner_models import (
    ModelScanResponse, ModelSummaryResponse, ModelSearchResponse
)
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/models/scanner", tags=["Model Scanner"])

@router.get("/scan", response_model=ModelScanResponse)
def scan_models_directory(user=Depends(protected)):
    """
    GET /api/models/scanner/scan
    
    Scans the models directory for all available model files and categorizes them.
    
    **Description:** 
    Performs a complete scan of the models directory to discover all safetensors, 
    sft, ckpt, and other supported model files. Categorizes models by type 
    (checkpoints, VAE, CLIP, etc.) based on directory structure and file analysis.
    
    **Arguments:**
    - `user`: Authentication token (automatic via Depends)
    
    **Returns:**
    - Status: 200 OK
    - Body: ModelScanResponse with categorized model information
    
    **Possible errors:**
    - 401: Not authenticated
    - 500: Error scanning models directory
    
    **Usage:** 
    Get a complete inventory of all available model files organized by category.
    """
    try:
        logger.info("Starting model directory scan")
        results = ModelScannerService.scan_models_directory()
        
        if "error" in results:
            logger.error(f"Model scan failed: {results['error']}")
            raise HTTPException(status_code=500, detail=results["error"])
        
        logger.info(f"Model scan completed successfully. Found {results.get('total_models', 0)} models")
        
        return ModelScanResponse(
            models_directory=results["models_directory"],
            total_models=results["total_models"],
            models=results["models"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during model scan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error scanning models directory: {str(e)}")

@router.get("/summary", response_model=ModelSummaryResponse)
def get_model_summary(user=Depends(protected)):
    """
    GET /api/models/scanner/summary
    
    Gets a summary of discovered models with statistics by category.
    
    **Description:** 
    Provides a high-level overview of model discovery results including 
    total counts and size statistics for each model category.
    
    **Arguments:**
    - `user`: Authentication token (automatic via Depends)
    
    **Returns:**
    - Status: 200 OK
    - Body: ModelSummaryResponse with summary statistics
    
    **Possible errors:**
    - 401: Not authenticated
    - 500: Error getting model summary
    
    **Usage:** 
    Get overview statistics of available models without detailed file information.
    """
    try:
        logger.info("Getting model summary")
        summary = ModelScannerService.get_model_summary()
        
        if "error" in summary:
            logger.error(f"Model summary failed: {summary['error']}")
            raise HTTPException(status_code=500, detail=summary["error"])
        
        logger.info(f"Model summary completed. Total models: {summary.get('total_models', 0)}")
        
        return ModelSummaryResponse(
            total_models=summary["total_models"],
            models_directory=summary["models_directory"],
            categories=summary["categories"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting model summary: {str(e)}")

@router.get("/search", response_model=ModelSearchResponse)
def search_models(
    query: str = Query(..., description="Search query string"),
    category: Optional[str] = Query(None, description="Category to search in (optional)"),
    user=Depends(protected)
):
    """
    GET /api/models/scanner/search
    
    Searches for models matching a query string, optionally filtered by category.
    
    **Description:** 
    Searches through discovered models by name or path using the provided query.
    Can be filtered to search only within a specific category.
    
    **Arguments:**
    - `query` (str): Search query string to match against model names/paths
    - `category` (str, optional): Category to search in (checkpoints, vae, clip, etc.)
    - `user`: Authentication token (automatic via Depends)
    
    **Returns:**
    - Status: 200 OK
    - Body: ModelSearchResponse with matching models
    
    **Possible errors:**
    - 401: Not authenticated
    - 400: Invalid search parameters
    - 500: Error during search
    
    **Usage:** 
    Find specific models by name or search within a particular category.
    """
    try:
        if not query or len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters long")
        
        logger.info(f"Searching models with query: '{query}', category: {category}")
        results = ModelScannerService.search_models(query, category)
        
        if "error" in results:
            logger.error(f"Model search failed: {results['error']}")
            raise HTTPException(status_code=500, detail=results["error"])
        
        logger.info(f"Model search completed. Found {results.get('total_matches', 0)} matches")
        
        return ModelSearchResponse(
            query=results["query"],
            category=results["category"],
            matches=results["matches"],
            total_matches=results["total_matches"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during model search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching models: {str(e)}")

@router.get("/categories")
def get_model_categories(user=Depends(protected)):
    """
    GET /api/models/scanner/categories
    
    Gets the list of available model categories.
    
    **Description:** 
    Returns the list of model categories used for classification.
    
    **Arguments:**
    - `user`: Authentication token (automatic via Depends)
    
    **Returns:**
    - Status: 200 OK
    - Body: List of category names
    
    **Possible errors:**
    - 401: Not authenticated
    
    **Usage:** 
    Get the available categories for filtering model searches.
    """
    try:
        categories = list(ModelScannerService.MODEL_TYPES.keys()) + ["other"]
        logger.info(f"Returning {len(categories)} model categories")
        
        return {
            "categories": categories,
            "category_descriptions": {
                "checkpoints": "Full model checkpoints and diffusion models",
                "vae": "Variational Autoencoders",
                "clip": "CLIP text encoders",
                "controlnet": "ControlNet models",
                "embeddings": "Text embeddings and textual inversions",
                "loras": "LoRA (Low-Rank Adaptation) models",
                "hypernetworks": "Hypernetwork models",
                "upscale_models": "Upscaling models",
                "style_models": "Style transfer models",
                "diffusion_models": "Diffusion models and UNet architectures",
                "unet": "UNet architectures",
                "text_encoders": "Text encoding models",
                "other": "Uncategorized models"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting model categories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting model categories: {str(e)}")

@router.get("/types")
def get_model_types(user=Depends(protected)):
    """
    GET /api/models/scanner/types
    
    Gets information about model types and their classifications.
    
    **Description:** 
    Returns detailed information about how models are classified and categorized.
    
    **Arguments:**
    - `user`: Authentication token (automatic via Depends)
    
    **Returns:**
    - Status: 200 OK
    - Body: Model type classification information
    
    **Possible errors:**
    - 401: Not authenticated
    
    **Usage:** 
    Understand how models are categorized and what types are supported.
    """
    try:
        logger.info("Returning model type information")
        
        return {
            "supported_extensions": ModelScannerService.SUPPORTED_EXTENSIONS,
            "model_classifications": {
                "checkpoint": "Full model checkpoints that can be loaded directly",
                "diffusion_loader": "Models compatible with diffusion loaders",
                "vae": "Variational Autoencoders for image encoding/decoding",
                "clip": "CLIP models for text encoding",
                "controlnet": "ControlNet models for guided generation",
                "lora": "LoRA models for fine-tuning",
                "embeddings": "Text embeddings and textual inversions",
                "upscale": "Models for image upscaling",
                "hypernetworks": "Hypernetwork models",
                "style": "Style transfer models",
                "unknown": "Models with unknown or unclassified types"
            },
            "directory_mapping": ModelScannerService.MODEL_TYPES
        }
        
    except Exception as e:
        logger.error(f"Error getting model types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting model types: {str(e)}")
