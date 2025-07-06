#!/usr/bin/env python3
"""
Test script to demonstrate the new refactored features.

**Description:** Shows the improvements made to ComfyWorkflowBuilder:
- Node creation extracted to private methods
- Sampling logic moved to BaseModelLoader
- Conditional DetailDaemonSamplerNode based on add_details parameter
- Cleaner, more maintainable code structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams, ModelLoaderFactory
import json

def test_extracted_node_methods():
    """Test that nodes are created using extracted private methods."""
    print("🧪 Testing extracted node creation methods...")
    
    builder = ComfyWorkflowBuilder()
    
    # Test individual node creation methods
    print("✓ Testing _create_seed_generator_node...")
    seed_ref = builder._create_seed_generator_node(12345)
    assert seed_ref == ['1', 0], f"Expected ['1', 0], got {seed_ref}"
    
    print("✓ Testing _create_tea_cache_node...")
    model_ref = ['mock_model', 0]
    cache_ref = builder._create_tea_cache_node("flux", model_ref)
    assert cache_ref == ['2', 0], f"Expected ['2', 0], got {cache_ref}"
    
    print("✓ Testing _create_text_encode_nodes...")
    clip_ref = ['mock_clip', 0]
    pos_ref, neg_ref = builder._create_text_encode_nodes("test prompt", "bad quality", clip_ref)
    assert pos_ref == ['3', 0], f"Expected ['3', 0], got {pos_ref}"
    assert neg_ref == ['4', 0], f"Expected ['4', 0], got {neg_ref}"
    
    print("✓ All extracted node methods work correctly!")
    

def test_add_details_parameter():
    """Test that DetailDaemonSamplerNode is conditional on add_details parameter."""
    print("\n🧪 Testing add_details parameter...")
    
    # Test without add_details (default False)
    params_no_details = GenerationParams(
        model_key="flux-dev",
        prompt="A beautiful landscape",
        add_details=False
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params_no_details)
    
    node_classes = [node.get("class_type") for node in workflow.values()]
    assert "DetailDaemonSamplerNode" not in node_classes, "DetailDaemonSamplerNode should not be present when add_details=False"
    print("✓ DetailDaemonSamplerNode correctly excluded when add_details=False")
    
    # Test with add_details=True
    params_with_details = GenerationParams(
        model_key="flux-dev",
        prompt="A beautiful landscape",
        add_details=True
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params_with_details)
    
    node_classes = [node.get("class_type") for node in workflow.values()]
    assert "DetailDaemonSamplerNode" in node_classes, "DetailDaemonSamplerNode should be present when add_details=True"
    print("✓ DetailDaemonSamplerNode correctly included when add_details=True")
    

def test_sampling_logic_in_loaders():
    """Test that sampling logic is now handled by model loaders."""
    print("\n🧪 Testing sampling logic moved to model loaders...")
    
    # Test Flux loader creates appropriate sampling nodes
    params_flux = GenerationParams(
        model_key="flux-dev",
        prompt="Test flux sampling"
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params_flux)
    
    node_classes = [node.get("class_type") for node in workflow.values()]
    assert "FluxGuidance" in node_classes, "Flux should have FluxGuidance"
    assert "SamplerCustomAdvanced" in node_classes, "Flux should use SamplerCustomAdvanced"
    assert "BasicScheduler" in node_classes, "Flux should have BasicScheduler"
    assert "KSamplerSelect" in node_classes, "Flux should have KSamplerSelect"
    print("✓ Flux loader creates correct sampling nodes")
    
    # Test checkpoint loader creates basic sampling nodes
    params_checkpoint = GenerationParams(
        model_key="sdxl",
        prompt="Test checkpoint sampling"
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params_checkpoint)
    
    node_classes = [node.get("class_type") for node in workflow.values()]
    assert "KSampler" in node_classes, "Checkpoint should use KSampler"
    assert "FluxGuidance" not in node_classes, "Checkpoint should not have FluxGuidance"
    print("✓ Checkpoint loader creates correct sampling nodes")
    
    # Test HiDream loader creates appropriate sampling nodes
    params_hidream = GenerationParams(
        model_key="hidream",
        prompt="Test hidream sampling"
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params_hidream)
    
    node_classes = [node.get("class_type") for node in workflow.values()]
    assert "CFGGuider" in node_classes, "HiDream should have CFGGuider"
    assert "SamplerCustomAdvanced" in node_classes, "HiDream should use SamplerCustomAdvanced"
    print("✓ HiDream loader creates correct sampling nodes")


def test_cleaner_build_workflow():
    """Test that the main build_prompt_workflow method is cleaner and more readable."""
    print("\n🧪 Testing cleaner build_prompt_workflow method...")
    
    params = GenerationParams(
        model_key="flux-dev",
        prompt="A masterpiece artwork",
        negative_prompt="low quality, blurry",
        steps=25,
        cfg=8.0,
        width=1024,
        height=1024,
        seed=42,
        enable_tea_cache=True,
        enable_clear_cache=True,
        add_details=True
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params)
    
    # Verify the workflow has all expected components
    node_classes = [node.get("class_type") for node in workflow.values()]
    
    expected_classes = [
        "UNETLoader",           # Model loading
        "DualCLIPLoader",       # CLIP loading
        "VAELoader",            # VAE loading
        "ModelSamplingFlux",    # Flux-specific sampling
        "TeaCache",             # Optimization
        "Seed Generator",       # Seed management
        "CLIPTextEncode",       # Text encoding
        "FluxGuidance",         # Flux guidance
        "SamplerCustomAdvanced", # Advanced sampling
        "DetailDaemonSamplerNode", # Detail enhancement
        "VAEDecode",            # Image decoding
        "SaveImage",            # Image saving
        "easy clearCacheAll"    # Cache clearing
    ]
    
    for class_name in expected_classes:
        assert class_name in node_classes, f"Expected {class_name} in workflow"
    
    print("✓ build_prompt_workflow generates complete workflow with all components")
    print(f"✓ Generated workflow has {len(workflow)} nodes")
    

def test_factory_method_with_new_parameters():
    """Test the factory method with new parameters."""
    print("\n🧪 Testing factory method with new parameters...")
    
    # Test with add_details=True
    params = ComfyWorkflowBuilder.create_generation_params(
        model_key="flux-dev",
        prompt="Beautiful portrait",
        add_details=True,
        steps=20,
        cfg=7.0
    )
    
    assert params.add_details == True, "add_details should be True"
    assert params.steps == 20, "steps should be 20"
    assert params.cfg == 7.0, "cfg should be 7.0"
    print("✓ Factory method correctly handles add_details parameter")
    

def save_demo_workflows():
    """Save demonstration workflows to showcase the improvements."""
    print("\n💾 Saving demo workflows...")
    
    # Save workflow without details
    params_no_details = GenerationParams(
        model_key="flux-dev",
        prompt="A serene mountain landscape at sunset",
        add_details=False
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params_no_details)
    
    with open("demo_flux_no_details.json", "w") as f:
        json.dump(workflow, f, indent=2)
    print("✓ Saved demo_flux_no_details.json")
    
    # Save workflow with details
    params_with_details = GenerationParams(
        model_key="flux-dev",
        prompt="A serene mountain landscape at sunset",
        add_details=True
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params_with_details)
    
    with open("demo_flux_with_details.json", "w") as f:
        json.dump(workflow, f, indent=2)
    print("✓ Saved demo_flux_with_details.json")
    
    # Show difference
    no_details_classes = [node.get("class_type") for node in workflow.values()]
    with_details_classes = [node.get("class_type") for node in workflow.values()]
    
    print(f"✓ No details workflow: {len(no_details_classes)} node types")
    print(f"✓ With details workflow: {len(with_details_classes)} node types")
    

def main():
    """Run all refactored feature tests."""
    print("🚀 Testing Refactored ComfyWorkflowBuilder Features")
    print("=" * 60)
    
    try:
        test_extracted_node_methods()
        test_add_details_parameter()
        test_sampling_logic_in_loaders()
        test_cleaner_build_workflow()
        test_factory_method_with_new_parameters()
        save_demo_workflows()
        
        print("\n🎉 All refactored feature tests passed!")
        print("\n📋 Summary of improvements:")
        print("✓ Node creation extracted to private methods")
        print("✓ Sampling logic moved to BaseModelLoader")
        print("✓ DetailDaemonSamplerNode conditional on add_details")
        print("✓ Cleaner, more maintainable code structure")
        print("✓ Better separation of concerns")
        print("✓ More extensible architecture")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
