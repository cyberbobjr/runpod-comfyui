"""
Comfy Router - Handle ComfyUI workflow generation and execution API routes

This module contains all API routes for ComfyUI workflow management including:
- Workflow generation from parameters
- Workflow execution via ComfyUI
- Model registry management
- LoRA and ControlNet integration
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import requests

from ..services.auth_middleware import protected
from ..services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams, MODEL_REGISTRY
from ..services.comfy_client import ComfyClient
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/comfy", tags=["ComfyUI"])

# Initialize services
comfy_client = ComfyClient()


@router.get("/models", response_model=Dict[str, Any])
def get_available_models(user=Depends(protected)):
    """
    GET /api/comfy/models
    
    Lists all available models in the model registry.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Dictionary of available models with their metadata
    
    Possible errors:
    - 401: Not authenticated
    """
    try:
        logger.info("Fetching available models from registry")
        return JSONResponse(
            status_code=200,
            content={"models": MODEL_REGISTRY}
        )
    except Exception as e:
        logger.error(f"Error fetching models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")


@router.post("/workflow/generate")
def generate_workflow(
    params: GenerationParams,
    user=Depends(protected)
):
    """
    POST /api/comfy/workflow/generate
    
    Generates a ComfyUI workflow based on the provided parameters.
    
    Arguments:
    - params: Complete generation parameters including optional features
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Generated ComfyUI workflow JSON
    
    Possible errors:
    - 400: Invalid parameters or missing model
    - 401: Not authenticated
    - 500: Error generating workflow
    """
    try:
        logger.info(f"Generating workflow for model: {params.model_key}")
        
        # Initialize workflow builder
        builder = ComfyWorkflowBuilder()
        
        # Generate workflow (all parameters are now in GenerationParams)
        workflow = builder.build_prompt_workflow(params)
        
        logger.info("Workflow generated successfully")
        return JSONResponse(
            status_code=200,
            content={"workflow": workflow}
        )
        
    except ValueError as e:
        logger.error(f"Invalid parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating workflow: {str(e)}")


@router.post("/workflow/execute")
def execute_workflow(
    workflow: Dict[str, Any],
    user=Depends(protected)
):
    """
    POST /api/comfy/workflow/execute
    
    Executes a ComfyUI workflow and returns the result.
    
    Arguments:
    - workflow: ComfyUI workflow JSON to execute
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Execution result with generated images
    
    Possible errors:
    - 400: Invalid workflow format
    - 401: Not authenticated
    - 500: Error executing workflow or ComfyUI unavailable
    - 504: Workflow execution timeout
    """
    try:
        logger.info("Executing ComfyUI workflow")
        
        # Send prompt to ComfyUI
        prompt_id = comfy_client.send_prompt(workflow)
        logger.info(f"Workflow sent with prompt_id: {prompt_id}")
        
        # Wait for completion
        result = comfy_client.wait_for_completion(prompt_id, timeout=120)
        
        # Get output images
        images = comfy_client.get_output_images(result)
        
        logger.info(f"Workflow completed successfully, generated {len(images)} images")
        return JSONResponse(
            status_code=200,
            content={
                "prompt_id": prompt_id,
                "images": images,
                "result": result
            }
        )
        
    except TimeoutError as e:
        logger.error(f"Workflow execution timeout: {str(e)}")
        raise HTTPException(status_code=504, detail="Workflow execution timeout")
    except requests.exceptions.RequestException as e:
        logger.error(f"ComfyUI connection error: {str(e)}")
        raise HTTPException(status_code=500, detail="ComfyUI server unavailable")
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error executing workflow: {str(e)}")


@router.post("/generate-and-execute")
def generate_and_execute(
    params: GenerationParams,
    user=Depends(protected)
):
    """
    POST /api/comfy/generate-and-execute
    
    Convenience endpoint that generates and executes a workflow in one call.
    
    Arguments:
    - params: Complete generation parameters including execution control
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Execution result with generated images and workflow (if wait=True)
           or immediate response with prompt_id (if wait=False)
    
    Possible errors:
    - 400: Invalid parameters or missing model
    - 401: Not authenticated
    - 500: Error generating or executing workflow
    - 504: Workflow execution timeout
    """
    try:
        logger.info(f"Generating and executing workflow for model: {params.model_key}")
        
        # Initialize workflow builder and generate workflow
        builder = ComfyWorkflowBuilder()
        workflow = builder.build_prompt_workflow(params)
        logger.info("Workflow generated successfully")
        
        # Execute workflow
        prompt_id = comfy_client.send_prompt(workflow)
        logger.info(f"Workflow sent with prompt_id: {prompt_id}")

        if not params.wait:
            # Return immediately for WebSocket preview
            return JSONResponse(
                status_code=200,
                content={
                    "status": "submitted",
                    "prompt_id": prompt_id
                }
            )

        # Wait for completion
        result = comfy_client.wait_for_completion(prompt_id, timeout=120)
        images = comfy_client.get_output_images(result)

        logger.info(f"Workflow completed successfully, generated {len(images)} images")
        return JSONResponse(
            status_code=200,
            content={
                "prompt_id": prompt_id,
                "workflow": workflow,
                "images": images,
                "result": result
            }
        )

    except ValueError as e:
        logger.error(f"Invalid parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        logger.error(f"Workflow execution timeout: {str(e)}")
        raise HTTPException(status_code=504, detail="Workflow execution timeout")
    except requests.exceptions.RequestException as e:
        logger.error(f"ComfyUI connection error: {str(e)}")
        raise HTTPException(status_code=500, detail="ComfyUI server unavailable")
    except Exception as e:
        logger.error(f"Error in generate-and-execute: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in generate-and-execute: {str(e)}")


@router.get("/status")
def get_comfy_status(user=Depends(protected)):
    """
    GET /api/comfy/status
    
    Checks the status and availability of the ComfyUI server.
    
    Arguments:
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: ComfyUI server status information
    
    Possible errors:
    - 401: Not authenticated
    - 503: ComfyUI server unavailable
    """
    try:
        logger.info("Checking ComfyUI status")
        
        # Try to connect to ComfyUI
        response = requests.get(f"{comfy_client.base_url}/system_stats", timeout=5)
        response.raise_for_status()
        
        logger.info("ComfyUI server is available")
        return JSONResponse(
            status_code=200,
            content={
                "status": "available",
                "base_url": comfy_client.base_url,
                "system_stats": response.json()
            }
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"ComfyUI server unavailable: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"ComfyUI server unavailable at {comfy_client.base_url}"
        )
    except Exception as e:
        logger.error(f"Error checking ComfyUI status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking status: {str(e)}")


@router.get("/result/{prompt_id}")
def get_result_by_prompt_id(prompt_id: str, user=Depends(protected)):
    """
    GET /api/comfy/result/{prompt_id}
    
    Retrieves the result of a specific prompt execution by its ID.
    
    Arguments:
    - prompt_id: The unique identifier of the prompt execution
    - user: Authentication token (automatic via Depends)
    
    Returns:
    - Status: 200 OK
    - Body: Result with image URLs and execution details
    
    Possible errors:
    - 401: Not authenticated
    - 404: Prompt ID not found in history
    - 503: ComfyUI server unavailable
    - 500: Error retrieving result
    """
    try:
        logger.info(f"Fetching result for prompt_id: {prompt_id}")
        
        # Get history from ComfyUI
        response = requests.get(f"{comfy_client.base_url}/history", timeout=10)
        response.raise_for_status()
        history = response.json()
        
        # Check if prompt_id exists in history
        if prompt_id not in history:
            logger.warning(f"Prompt ID {prompt_id} not found in history")
            raise HTTPException(status_code=404, detail="Prompt ID not found in history")
        
        result = history[prompt_id]
        image_urls = []
        
        # Extract image URLs from the result
        for node_output in result["outputs"].values():
            if "images" in node_output:
                for image_info in node_output["images"]:
                    image_url = f"{comfy_client.base_url}/view?filename={image_info['filename']}"
                    image_urls.append(image_url)
        
        logger.info(f"Found {len(image_urls)} images for prompt_id: {prompt_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "prompt_id": prompt_id,
                "images": image_urls,
                "result": result,
                "status": result.get("status", {}).get("status_str", "completed")
            }
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"ComfyUI connection error: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail=f"ComfyUI server unavailable at {comfy_client.base_url}"
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) without modification
        raise
    except Exception as e:
        logger.error(f"Error retrieving result for prompt_id {prompt_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving result: {str(e)}")
