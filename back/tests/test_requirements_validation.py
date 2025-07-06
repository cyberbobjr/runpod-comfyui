#!/usr/bin/env python3

import sys
import os
import json

# Add the back directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams

def test_inpaint_model_conditioning_requirements():
    """Test that InpaintModelConditioning meets all the specified requirements."""
    
    print("🔧 Testing InpaintModelConditioning implementation against requirements...")
    
    # Test Case 1: Only inpainting enabled
    print("\n1. Testing inpainting only scenario...")
    builder = ComfyWorkflowBuilder()
    params = GenerationParams(
        model_key="sdxl",
        prompt="A beautiful restored painting",
        negative_prompt="damaged, incomplete",
        init_image="test_image.png",
        inpaint_mask="test_mask.png"
    )
    
    workflow = builder.build_prompt_workflow(params)
    
    # Find InpaintModelConditioning node
    inpaint_node = None
    inpaint_node_id = None
    for node_id, node in workflow.items():
        if node.get("class_type") == "InpaintModelConditioning":
            inpaint_node = node
            inpaint_node_id = node_id
            break
    
    if inpaint_node is None:
        print("❌ FAIL: InpaintModelConditioning node not found!")
        return False
    
    # Check inputs
    inputs = inpaint_node["inputs"]
    required_inputs = ["positive", "negative", "vae", "pixels", "mask"]
    
    for req_input in required_inputs:
        if req_input not in inputs:
            print(f"❌ FAIL: Missing required input '{req_input}'")
            return False
    
    print("✓ PASS: All required inputs present for inpainting")
    
    # Test Case 2: Only outpainting enabled
    print("\n2. Testing outpainting only scenario...")
    builder2 = ComfyWorkflowBuilder()
    params2 = GenerationParams(
        model_key="flux-dev",
        prompt="Expand this landscape",
        negative_prompt="cropped, cut off",
        init_image="test_image.png",
        outpaint_padding=128
    )
    
    workflow2 = builder2.build_prompt_workflow(params2)
    
    # Find InpaintModelConditioning node
    inpaint_node2 = None
    inpaint_node_id2 = None
    for node_id, node in workflow2.items():
        if node.get("class_type") == "InpaintModelConditioning":
            inpaint_node2 = node
            inpaint_node_id2 = node_id
            break
    
    if inpaint_node2 is None:
        print("❌ FAIL: InpaintModelConditioning node not found in outpainting workflow!")
        return False
    
    # Check inputs (no mask for outpainting)
    inputs2 = inpaint_node2["inputs"]
    required_inputs2 = ["positive", "negative", "vae", "pixels"]
    
    for req_input in required_inputs2:
        if req_input not in inputs2:
            print(f"❌ FAIL: Missing required input '{req_input}' in outpainting")
            return False
    
    if "mask" in inputs2:
        print("❌ FAIL: Mask should not be present in outpainting-only workflow")
        return False
    
    print("✓ PASS: Correct inputs for outpainting (no mask)")
    
    # Test Case 3: Both inpainting and outpainting enabled
    print("\n3. Testing combined inpainting + outpainting scenario...")
    builder3 = ComfyWorkflowBuilder()
    params3 = GenerationParams(
        model_key="sdxl",
        prompt="A beautiful expanded and restored painting",
        negative_prompt="damaged, incomplete, cropped",
        init_image="test_image.png",
        inpaint_mask="test_mask.png",
        outpaint_padding=128
    )
    
    workflow3 = builder3.build_prompt_workflow(params3)
    
    # Find InpaintModelConditioning node
    inpaint_node3 = None
    inpaint_node_id3 = None
    for node_id, node in workflow3.items():
        if node.get("class_type") == "InpaintModelConditioning":
            inpaint_node3 = node
            inpaint_node_id3 = node_id
            break
    
    if inpaint_node3 is None:
        print("❌ FAIL: InpaintModelConditioning node not found in combined workflow!")
        return False
    
    # Check inputs (should have mask for combined workflow)
    inputs3 = inpaint_node3["inputs"]
    required_inputs3 = ["positive", "negative", "vae", "pixels", "mask"]
    
    for req_input in required_inputs3:
        if req_input not in inputs3:
            print(f"❌ FAIL: Missing required input '{req_input}' in combined workflow")
            return False
    
    print("✓ PASS: All required inputs present for combined workflow")
    
    # Test Case 4: Data flow verification
    print("\n4. Testing data flow - outputs replace pipeline references...")
    
    # Check that sampler uses outputs from InpaintModelConditioning
    sampler_node = None
    for node_id, node in workflow.items():
        if node.get("class_type") in ["KSampler", "SamplerCustomAdvanced"]:
            sampler_node = node
            break
    
    if sampler_node is None:
        print("❌ FAIL: No sampler node found!")
        return False
    
    sampler_inputs = sampler_node["inputs"]
    
    # Check positive conditioning
    if sampler_inputs["positive"] != [inpaint_node_id, 0]:
        print(f"❌ FAIL: Sampler positive conditioning not from InpaintModelConditioning")
        print(f"Expected: [{inpaint_node_id}, 0], Got: {sampler_inputs['positive']}")
        return False
    
    # Check negative conditioning
    if sampler_inputs["negative"] != [inpaint_node_id, 1]:
        print(f"❌ FAIL: Sampler negative conditioning not from InpaintModelConditioning")
        print(f"Expected: [{inpaint_node_id}, 1], Got: {sampler_inputs['negative']}")
        return False
    
    # Check latent
    if sampler_inputs["latent_image"] != [inpaint_node_id, 2]:
        print(f"❌ FAIL: Sampler latent not from InpaintModelConditioning")
        print(f"Expected: [{inpaint_node_id}, 2], Got: {sampler_inputs['latent_image']}")
        return False
    
    print("✓ PASS: Data flow correctly redirected through InpaintModelConditioning")
    
    # Test Case 5: VAE reference correctness
    print("\n5. Testing VAE reference correctness...")
    
    # Test with different model types
    model_types = ["sdxl", "flux-dev", "hidream"]
    
    for model_key in model_types:
        print(f"   Testing VAE reference with {model_key}...")
        builder_vae = ComfyWorkflowBuilder()
        params_vae = GenerationParams(
            model_key=model_key,
            prompt="Test prompt",
            negative_prompt="Test negative",
            init_image="test_image.png",
            inpaint_mask="test_mask.png"
        )
        
        workflow_vae = builder_vae.build_prompt_workflow(params_vae)
        
        # Find InpaintModelConditioning node
        inpaint_node_vae = None
        for node_id, node in workflow_vae.items():
            if node.get("class_type") == "InpaintModelConditioning":
                inpaint_node_vae = node
                break
        
        if inpaint_node_vae is None:
            print(f"❌ FAIL: InpaintModelConditioning not found for {model_key}")
            return False
        
        # Check VAE reference
        vae_ref = inpaint_node_vae["inputs"]["vae"]
        if not isinstance(vae_ref, list) or len(vae_ref) != 2:
            print(f"❌ FAIL: Invalid VAE reference format for {model_key}: {vae_ref}")
            return False
        
        # Check that the VAE node exists
        vae_node = workflow_vae.get(str(vae_ref[0]))
        if vae_node is None:
            print(f"❌ FAIL: VAE node {vae_ref[0]} not found for {model_key}")
            return False
        
        print(f"   ✓ VAE reference valid for {model_key}")
    
    print("✓ PASS: VAE references correct for all model types")
    
    # Test Case 6: Node insertion order
    print("\n6. Testing node insertion order...")
    
    # Build workflow step by step to check order
    builder_order = ComfyWorkflowBuilder()
    params_order = GenerationParams(
        model_key="sdxl",
        prompt="Test prompt",
        negative_prompt="Test negative",
        init_image="test_image.png",
        inpaint_mask="test_mask.png"
    )
    
    workflow_order = builder_order.build_prompt_workflow(params_order)
    
    # Find node IDs
    load_image_id = None
    load_mask_id = None
    text_encode_ids = []
    inpaint_conditioning_id = None
    
    for node_id, node in workflow_order.items():
        class_type = node.get("class_type")
        if class_type == "LoadImage":
            load_image_id = node_id
        elif class_type == "LoadImageMask":
            load_mask_id = node_id
        elif class_type == "CLIPTextEncode":
            text_encode_ids.append(node_id)
        elif class_type == "InpaintModelConditioning":
            inpaint_conditioning_id = node_id
    
    # Check that InpaintModelConditioning comes after image loading and text encoding
    if (load_image_id is None or load_mask_id is None or 
        len(text_encode_ids) < 2 or inpaint_conditioning_id is None):
        print("❌ FAIL: Required nodes not found for order check")
        return False
    
    # Node IDs are sequential, so InpaintModelConditioning should have higher ID
    if (int(inpaint_conditioning_id) <= int(load_image_id) or 
        int(inpaint_conditioning_id) <= int(load_mask_id) or
        int(inpaint_conditioning_id) <= int(max(text_encode_ids))):
        print("❌ FAIL: InpaintModelConditioning not inserted in correct order")
        return False
    
    print("✓ PASS: Node insertion order is correct")
    
    print("\n🎉 All requirements tests passed!")
    return True

if __name__ == "__main__":
    success = test_inpaint_model_conditioning_requirements()
    
    if success:
        print("\n🎯 SUCCESS: InpaintModelConditioning implementation meets all requirements!")
    else:
        print("\n❌ FAILURE: Some requirements not met!")
        sys.exit(1)
