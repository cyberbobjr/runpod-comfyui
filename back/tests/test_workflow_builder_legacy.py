#!/usr/bin/env python3
"""
Test script to verify ComfyWorkflowBuilder generates correct workflows
"""

import json
import sys
import os

# Add the back directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams, LoRA
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def test_basic_sdxl_workflow():
    """Test basic SDXL workflow generation"""
    print("Testing basic SDXL workflow...")
    
    builder = ComfyWorkflowBuilder()
    params = GenerationParams(
        model_key="sdxl",
        prompt="A beautiful landscape with mountains and trees",
        negative_prompt="blurry, low quality",
        steps=30,
        cfg=7.5,
        width=1024,
        height=1024,
        seed=42
    )
    
    workflow = builder.build_prompt_workflow(params)
    
    # Verify structure
    assert isinstance(workflow, dict), "Workflow should be a dictionary"
    assert len(workflow) > 0, "Workflow should not be empty"
    
    # Check that IDs are strings
    for node_id, node in workflow.items():
        assert isinstance(node_id, str), f"Node ID should be string, got {type(node_id)}"
        assert "class_type" in node, f"Node {node_id} missing class_type"
        assert "inputs" in node, f"Node {node_id} missing inputs"
        assert "_meta" in node, f"Node {node_id} missing _meta"
    
    print("✓ Basic SDXL workflow test passed")
    return workflow

def test_flux_workflow():
    """Test Flux workflow generation"""
    print("Testing Flux workflow...")
    
    builder = ComfyWorkflowBuilder()
    params = GenerationParams(
        model_key="flux-dev",
        prompt="A futuristic cityscape at sunset",
        negative_prompt="ugly, bad, wrong",
        steps=24,
        cfg=4.0,
        width=1024,
        height=1024,
        seed=808466373884902
    )
    
    workflow = builder.build_prompt_workflow(params)
    
    # Verify Flux-specific components
    node_classes = [node.get("class_type") for node in workflow.values()]
    required_classes = [
        "UNETLoader",
        "DualCLIPLoader", 
        "VAELoader",
        "ModelSamplingFlux",
        "FluxGuidance",
        "SamplerCustomAdvanced",
        "TeaCache",
        "Seed Generator"
    ]
    
    for class_name in required_classes:
        assert class_name in node_classes, f"Flux workflow should have {class_name}"
    
    # Check that we're NOT using the old SamplerCustom
    assert "SamplerCustom" not in node_classes, "Flux workflow should not have SamplerCustom"
    
    print("✓ Flux workflow test passed")
    return workflow

def test_lora_workflow():
    """Test workflow with LoRAs"""
    print("Testing workflow with LoRAs...")
    
    builder = ComfyWorkflowBuilder()
    loras = [
        LoRA(name="FLUX\\Hand v2.safetensors", strength=1.0),
        LoRA(name="FLUX\\aidmaImageUprader-FLUX-v0.3.safetensors", strength=0.8)
    ]
    
    params = GenerationParams(
        model_key="flux-dev",
        prompt="A character in anime style with perfect hands",
        loras=loras
    )
    
    workflow = builder.build_prompt_workflow(params)
    
    # Check for Power Lora Loader
    lora_loaders = [node for node in workflow.values() if node.get("class_type") == "Power Lora Loader (rgthree)"]
    assert len(lora_loaders) == 1, f"Expected 1 Power Lora Loader, got {len(lora_loaders)}"
    
    # Check LoRA configuration
    lora_node = lora_loaders[0]
    inputs = lora_node["inputs"]
    assert "lora_1" in inputs, "Should have lora_1 input"
    assert inputs["lora_1"]["lora"] == "FLUX\\Hand v2.safetensors", "LoRA 1 name mismatch"
    assert inputs["lora_1"]["strength"] == 1.0, "LoRA 1 strength mismatch"
    assert inputs["lora_1"]["on"] == True, "LoRA 1 should be enabled"
    
    print("✓ LoRA workflow test passed")
    return workflow

def compare_with_reference(workflow, reference_file):
    """Compare generated workflow with reference"""
    print(f"Comparing with reference: {reference_file}")
    
    try:
        with open(reference_file, 'r', encoding='utf-8') as f:
            reference = json.load(f)
    except FileNotFoundError:
        print(f"Warning: Reference file {reference_file} not found, skipping comparison")
        return
    
    # Compare node classes
    workflow_classes = set(node.get("class_type") for node in workflow.values())
    reference_classes = set(node.get("class_type") for node in reference.values())
    
    print(f"Generated workflow has {len(workflow_classes)} unique node types")
    print(f"Reference workflow has {len(reference_classes)} unique node types")
    
    common_classes = workflow_classes & reference_classes
    print(f"Common node types: {len(common_classes)}")
    
    missing_in_generated = reference_classes - workflow_classes
    if missing_in_generated:
        print(f"Missing in generated: {missing_in_generated}")
    
    extra_in_generated = workflow_classes - reference_classes
    if extra_in_generated:
        print(f"Extra in generated: {extra_in_generated}")

def save_workflow_sample(workflow, filename):
    """Save workflow to file for inspection"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)
    print(f"Sample workflow saved to {filename}")

def main():
    """Main function to run all legacy tests."""
    try:
        print("🧪 Testing ComfyWorkflowBuilder...")
        print("=" * 50)
        
        # Test basic SDXL workflow
        sdxl_workflow = test_basic_sdxl_workflow()
        save_workflow_sample(sdxl_workflow, "sample_sdxl_workflow.json")
        
        print()
        
        # Test Flux workflow  
        flux_workflow = test_flux_workflow()
        save_workflow_sample(flux_workflow, "sample_flux_workflow.json")
        
        # Compare with reference
        reference_file = os.path.join("docs", "image_generation_flux_2.json")
        compare_with_reference(flux_workflow, reference_file)
        
        print()
        
        # Test LoRA workflow
        lora_workflow = test_lora_workflow()
        save_workflow_sample(lora_workflow, "sample_lora_workflow.json")
        
        print()
        print("🎉 All tests passed!")
        print("Sample workflows have been generated for inspection.")
        print("Compare the generated Flux workflow with docs/image_generation_flux_2.json")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
if __name__ == "__main__":
    main()
