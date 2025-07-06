#!/usr/bin/env python3

import sys
import os
import json

# Add the back directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams

def test_inpainting_workflow():
    """Test inpainting workflow generation."""
    print("Testing inpainting workflow generation...")
    
    builder = ComfyWorkflowBuilder()
    
    # Test inpainting only
    params = GenerationParams(
        model_key="sdxl",
        prompt="A beautiful restored painting",
        negative_prompt="damaged, incomplete",
        init_image="test_image.png",
        inpaint_mask="test_mask.png"
    )
    
    workflow = builder.build_prompt_workflow(params)
    
    print(f"Generated workflow with {len(workflow)} nodes")
    
    # Check for InpaintModelConditioning
    inpaint_node = None
    for node_id, node in workflow.items():
        if node.get("class_type") == "InpaintModelConditioning":
            inpaint_node = node
            print(f"Found InpaintModelConditioning node at ID {node_id}")
            print(f"Node inputs: {json.dumps(node['inputs'], indent=2)}")
            break
    
    if inpaint_node is None:
        print("ERROR: InpaintModelConditioning node not found!")
        return False
    
    # Verify inputs
    inputs = inpaint_node["inputs"]
    required_inputs = ["positive", "negative", "vae", "pixels", "mask"]
    
    for req_input in required_inputs:
        if req_input not in inputs:
            print(f"ERROR: Missing required input '{req_input}' in InpaintModelConditioning node")
            return False
        print(f"✓ Found required input '{req_input}': {inputs[req_input]}")
    
    print("✓ Inpainting workflow test passed!")
    return True

def test_outpainting_workflow():
    """Test outpainting workflow generation."""
    print("\nTesting outpainting workflow generation...")
    
    builder = ComfyWorkflowBuilder()
    
    # Test outpainting only
    params = GenerationParams(
        model_key="flux-dev",
        prompt="Expand this landscape",
        negative_prompt="cropped, cut off",
        init_image="test_image.png",
        outpaint_padding=128
    )
    
    workflow = builder.build_prompt_workflow(params)
    
    print(f"Generated workflow with {len(workflow)} nodes")
    
    # Check for InpaintModelConditioning
    inpaint_node = None
    for node_id, node in workflow.items():
        if node.get("class_type") == "InpaintModelConditioning":
            inpaint_node = node
            print(f"Found InpaintModelConditioning node at ID {node_id}")
            print(f"Node inputs: {json.dumps(node['inputs'], indent=2)}")
            break
    
    if inpaint_node is None:
        print("ERROR: InpaintModelConditioning node not found!")
        return False
    
    # Verify inputs (no mask for outpainting)
    inputs = inpaint_node["inputs"]
    required_inputs = ["positive", "negative", "vae", "pixels"]
    
    for req_input in required_inputs:
        if req_input not in inputs:
            print(f"ERROR: Missing required input '{req_input}' in InpaintModelConditioning node")
            return False
        print(f"✓ Found required input '{req_input}': {inputs[req_input]}")
    
    # Mask should NOT be present for outpainting only
    if "mask" in inputs:
        print("ERROR: Mask should not be present for outpainting-only workflow!")
        return False
    
    print("✓ Outpainting workflow test passed!")
    return True

def test_combined_workflow():
    """Test combined inpainting + outpainting workflow."""
    print("\nTesting combined inpainting + outpainting workflow...")
    
    builder = ComfyWorkflowBuilder()
    
    # Test both inpainting and outpainting
    params = GenerationParams(
        model_key="sdxl",
        prompt="A beautiful expanded and restored painting",
        negative_prompt="damaged, incomplete, cropped",
        init_image="test_image.png",
        inpaint_mask="test_mask.png",
        outpaint_padding=128
    )
    
    workflow = builder.build_prompt_workflow(params)
    
    print(f"Generated workflow with {len(workflow)} nodes")
    
    # Check for InpaintModelConditioning
    inpaint_node = None
    for node_id, node in workflow.items():
        if node.get("class_type") == "InpaintModelConditioning":
            inpaint_node = node
            print(f"Found InpaintModelConditioning node at ID {node_id}")
            print(f"Node inputs: {json.dumps(node['inputs'], indent=2)}")
            break
    
    if inpaint_node is None:
        print("ERROR: InpaintModelConditioning node not found!")
        return False
    
    # Verify inputs (should have mask for combined workflow)
    inputs = inpaint_node["inputs"]
    required_inputs = ["positive", "negative", "vae", "pixels", "mask"]
    
    for req_input in required_inputs:
        if req_input not in inputs:
            print(f"ERROR: Missing required input '{req_input}' in InpaintModelConditioning node")
            return False
        print(f"✓ Found required input '{req_input}': {inputs[req_input]}")
    
    print("✓ Combined workflow test passed!")
    return True

if __name__ == "__main__":
    success = True
    
    success &= test_inpainting_workflow()
    success &= test_outpainting_workflow()  
    success &= test_combined_workflow()
    
    if success:
        print("\n🎉 All tests passed! InpaintModelConditioning is working correctly.")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
