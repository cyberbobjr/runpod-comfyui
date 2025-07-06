#!/usr/bin/env python3

import sys
import os
import json

# Add the back directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams

def test_no_init_image():
    """Test that regular workflow without init_image works normally."""
    print("Testing regular workflow without init_image...")
    
    builder = ComfyWorkflowBuilder()
    
    # Test regular workflow
    params = GenerationParams(
        model_key="sdxl",
        prompt="A beautiful landscape",
        negative_prompt="blurry, bad quality"
    )
    
    workflow = builder.build_prompt_workflow(params)
    
    # Should NOT have InpaintModelConditioning
    for node_id, node in workflow.items():
        if node.get("class_type") == "InpaintModelConditioning":
            print("ERROR: InpaintModelConditioning found in regular workflow!")
            return False
    
    print("✓ Regular workflow test passed!")
    return True

def test_init_image_only():
    """Test that init_image without inpaint/outpaint works normally."""
    print("\nTesting init_image only (img2img)...")
    
    builder = ComfyWorkflowBuilder()
    
    # Test img2img workflow
    params = GenerationParams(
        model_key="sdxl",
        prompt="A beautiful landscape",
        negative_prompt="blurry, bad quality",
        init_image="test_image.png"
    )
    
    workflow = builder.build_prompt_workflow(params)
    
    # Should NOT have InpaintModelConditioning
    for node_id, node in workflow.items():
        if node.get("class_type") == "InpaintModelConditioning":
            print("ERROR: InpaintModelConditioning found in img2img workflow!")
            return False
    
    # Should have VAEEncode for img2img
    vae_encode_found = False
    for node_id, node in workflow.items():
        if node.get("class_type") == "VAEEncode":
            vae_encode_found = True
            break
    
    if not vae_encode_found:
        print("ERROR: VAEEncode not found in img2img workflow!")
        return False
    
    print("✓ img2img workflow test passed!")
    return True

def test_flux_model():
    """Test InpaintModelConditioning with Flux model."""
    print("\nTesting InpaintModelConditioning with Flux model...")
    
    builder = ComfyWorkflowBuilder()
    
    # Test Flux inpainting
    params = GenerationParams(
        model_key="flux-dev",
        prompt="A beautiful restored painting",
        negative_prompt="damaged, incomplete",
        init_image="test_image.png",
        inpaint_mask="test_mask.png"
    )
    
    workflow = builder.build_prompt_workflow(params)
    
    # Find InpaintModelConditioning node
    inpaint_node = None
    for node_id, node in workflow.items():
        if node.get("class_type") == "InpaintModelConditioning":
            inpaint_node = node
            break
    
    if inpaint_node is None:
        print("ERROR: InpaintModelConditioning not found in Flux workflow!")
        return False
    
    # Verify VAE reference is correct
    vae_ref = inpaint_node["inputs"]["vae"]
    print(f"VAE reference in InpaintModelConditioning: {vae_ref}")
    
    # Find VAE node
    vae_node = workflow.get(str(vae_ref[0]))
    if vae_node is None:
        print(f"ERROR: VAE node {vae_ref[0]} not found!")
        return False
    
    print(f"VAE node type: {vae_node.get('class_type')}")
    
    print("✓ Flux model test passed!")
    return True

def test_hidream_model():
    """Test InpaintModelConditioning with HiDream model."""
    print("\nTesting InpaintModelConditioning with HiDream model...")
    
    builder = ComfyWorkflowBuilder()
    
    # Test HiDream inpainting
    params = GenerationParams(
        model_key="hidream",
        prompt="A beautiful restored painting",
        negative_prompt="damaged, incomplete",
        init_image="test_image.png",
        inpaint_mask="test_mask.png"
    )
    
    workflow = builder.build_prompt_workflow(params)
    
    # Find InpaintModelConditioning node
    inpaint_node = None
    for node_id, node in workflow.items():
        if node.get("class_type") == "InpaintModelConditioning":
            inpaint_node = node
            break
    
    if inpaint_node is None:
        print("ERROR: InpaintModelConditioning not found in HiDream workflow!")
        return False
    
    # Verify VAE reference is correct
    vae_ref = inpaint_node["inputs"]["vae"]
    print(f"VAE reference in InpaintModelConditioning: {vae_ref}")
    
    print("✓ HiDream model test passed!")
    return True

if __name__ == "__main__":
    success = True
    
    success &= test_no_init_image()
    success &= test_init_image_only()
    success &= test_flux_model()
    success &= test_hidream_model()
    
    if success:
        print("\n🎉 All edge case tests passed!")
    else:
        print("\n❌ Some edge case tests failed!")
        sys.exit(1)
