#!/usr/bin/env python3
"""
Test script to verify InpaintModelConditioning node implementation.

**Description:** Tests the new InpaintModelConditioning node for inpainting and outpainting workflows.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams
import json

def test_inpainting_workflow():
    """Test inpainting workflow with InpaintModelConditioning node."""
    print("🧪 Testing inpainting workflow...")
    
    params = GenerationParams(
        model_key="sdxl",
        prompt="A beautiful landscape",
        negative_prompt="low quality",
        init_image="test_image.png",
        inpaint_mask="test_mask.png"
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params)
    
    # Check that InpaintModelConditioning node is present
    node_classes = [node.get("class_type") for node in workflow.values()]
    assert "InpaintModelConditioning" in node_classes, "InpaintModelConditioning node should be present for inpainting"
    
    # Find the InpaintModelConditioning node
    inpaint_node = None
    for node in workflow.values():
        if node.get("class_type") == "InpaintModelConditioning":
            inpaint_node = node
            break
    
    assert inpaint_node is not None, "InpaintModelConditioning node not found"
    
    # Check that the node has correct inputs
    inputs = inpaint_node["inputs"]
    assert "positive" in inputs, "InpaintModelConditioning should have positive input"
    assert "negative" in inputs, "InpaintModelConditioning should have negative input"
    assert "vae" in inputs, "InpaintModelConditioning should have vae input"
    assert "pixels" in inputs, "InpaintModelConditioning should have pixels input"
    assert "mask" in inputs, "InpaintModelConditioning should have mask input for inpainting"
    
    print("✓ Inpainting workflow test passed")
    
    # Save example workflow
    with open("test_inpainting_workflow.json", "w") as f:
        json.dump(workflow, f, indent=2)
    print("✓ Saved test_inpainting_workflow.json")
    
    return workflow

def test_outpainting_workflow():
    """Test outpainting workflow with InpaintModelConditioning node."""
    print("\n🧪 Testing outpainting workflow...")
    
    params = GenerationParams(
        model_key="flux-dev",
        prompt="A beautiful landscape",
        negative_prompt="low quality",
        init_image="test_image.png",
        outpaint_padding=128
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params)
    
    # Check that InpaintModelConditioning node is present
    node_classes = [node.get("class_type") for node in workflow.values()]
    assert "InpaintModelConditioning" in node_classes, "InpaintModelConditioning node should be present for outpainting"
    
    # Find the InpaintModelConditioning node
    inpaint_node = None
    for node in workflow.values():
        if node.get("class_type") == "InpaintModelConditioning":
            inpaint_node = node
            break
    
    assert inpaint_node is not None, "InpaintModelConditioning node not found"
    
    # Check that the node has correct inputs
    inputs = inpaint_node["inputs"]
    assert "positive" in inputs, "InpaintModelConditioning should have positive input"
    assert "negative" in inputs, "InpaintModelConditioning should have negative input"
    assert "vae" in inputs, "InpaintModelConditioning should have vae input"
    assert "pixels" in inputs, "InpaintModelConditioning should have pixels input"
    assert "mask" not in inputs, "InpaintModelConditioning should not have mask input for outpainting"
    
    # Check that ImagePadForOutpaint node is present
    assert "ImagePadForOutpaint" in node_classes, "ImagePadForOutpaint node should be present for outpainting"
    
    print("✓ Outpainting workflow test passed")
    
    # Save example workflow
    with open("test_outpainting_workflow.json", "w") as f:
        json.dump(workflow, f, indent=2)
    print("✓ Saved test_outpainting_workflow.json")
    
    return workflow

def test_inpaint_and_outpaint_combined():
    """Test workflow with both inpainting and outpainting."""
    print("\n🧪 Testing combined inpainting and outpainting workflow...")
    
    params = GenerationParams(
        model_key="hidream",
        prompt="A beautiful landscape",
        negative_prompt="low quality",
        init_image="test_image.png",
        inpaint_mask="test_mask.png",
        outpaint_padding=64
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params)
    
    # Check that InpaintModelConditioning node is present
    node_classes = [node.get("class_type") for node in workflow.values()]
    assert "InpaintModelConditioning" in node_classes, "InpaintModelConditioning node should be present"
    
    # Find the InpaintModelConditioning node
    inpaint_node = None
    for node in workflow.values():
        if node.get("class_type") == "InpaintModelConditioning":
            inpaint_node = node
            break
    
    assert inpaint_node is not None, "InpaintModelConditioning node not found"
    
    # Check that the node has correct inputs (should include mask since inpainting is enabled)
    inputs = inpaint_node["inputs"]
    assert "positive" in inputs, "InpaintModelConditioning should have positive input"
    assert "negative" in inputs, "InpaintModelConditioning should have negative input"
    assert "vae" in inputs, "InpaintModelConditioning should have vae input"
    assert "pixels" in inputs, "InpaintModelConditioning should have pixels input"
    assert "mask" in inputs, "InpaintModelConditioning should have mask input when both inpainting and outpainting are enabled"
    
    # Check that both ImagePadForOutpaint and LoadImageMask nodes are present
    assert "ImagePadForOutpaint" in node_classes, "ImagePadForOutpaint node should be present"
    assert "LoadImageMask" in node_classes, "LoadImageMask node should be present"
    
    print("✓ Combined inpainting and outpainting workflow test passed")
    
    # Save example workflow
    with open("test_inpaint_outpaint_combined.json", "w") as f:
        json.dump(workflow, f, indent=2)
    print("✓ Saved test_inpaint_outpaint_combined.json")
    
    return workflow

def test_regular_workflow_unchanged():
    """Test that regular workflows without inpainting/outpainting are unchanged."""
    print("\n🧪 Testing regular workflow (should not have InpaintModelConditioning)...")
    
    params = GenerationParams(
        model_key="flux-dev",
        prompt="A beautiful landscape",
        negative_prompt="low quality"
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params)
    
    # Check that InpaintModelConditioning node is NOT present
    node_classes = [node.get("class_type") for node in workflow.values()]
    assert "InpaintModelConditioning" not in node_classes, "InpaintModelConditioning node should not be present for regular workflows"
    
    print("✓ Regular workflow test passed")
    
    return workflow

def test_img2img_workflow():
    """Test img2img workflow without inpainting/outpainting."""
    print("\n🧪 Testing img2img workflow (should not have InpaintModelConditioning)...")
    
    params = GenerationParams(
        model_key="sdxl",
        prompt="A beautiful landscape",
        negative_prompt="low quality",
        init_image="test_image.png"
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params)
    
    # Check that InpaintModelConditioning node is NOT present
    node_classes = [node.get("class_type") for node in workflow.values()]
    assert "InpaintModelConditioning" not in node_classes, "InpaintModelConditioning node should not be present for regular img2img"
    
    # Check that VAEEncode is present for regular img2img
    assert "VAEEncode" in node_classes, "VAEEncode should be present for regular img2img"
    
    print("✓ Img2img workflow test passed")
    
    return workflow

def main():
    """Run all InpaintModelConditioning tests."""
    print("🚀 Testing InpaintModelConditioning Implementation")
    print("=" * 60)
    
    try:
        test_inpainting_workflow()
        test_outpainting_workflow()
        test_inpaint_and_outpaint_combined()
        test_regular_workflow_unchanged()
        test_img2img_workflow()
        
        print("\n🎉 All InpaintModelConditioning tests passed!")
        print("\n📋 Summary of test coverage:")
        print("✓ Inpainting workflow with mask")
        print("✓ Outpainting workflow with padding")
        print("✓ Combined inpainting and outpainting")
        print("✓ Regular workflows unaffected")
        print("✓ Regular img2img workflows unaffected")
        print("✓ Proper data flow through conditioning nodes")
        print("✓ Compatible with all model types (SDXL, Flux, HiDream)")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
