#!/usr/bin/env python3
"""
Example usage of the refactored ComfyWorkflowBuilder with add_details feature.

**Description:** Demonstrates how to use the new add_details parameter
to control the DetailDaemonSamplerNode inclusion in workflows.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams
import json

def main():
    """Demonstrate add_details parameter usage."""
    print("🎨 ComfyWorkflowBuilder add_details Feature Demo")
    print("=" * 50)
    
    # Example 1: Basic workflow (no details)
    print("\n1️⃣ Creating basic Flux workflow (add_details=False)")
    params_basic = ComfyWorkflowBuilder.create_generation_params(
        model_key="flux-dev",
        prompt="A beautiful mountain landscape",
        negative_prompt="blurry, low quality",
        steps=20,
        cfg=7.0,
        add_details=False  # Default value
    )
    
    builder = ComfyWorkflowBuilder()
    workflow_basic = builder.build_prompt_workflow(params_basic)
    
    basic_nodes = [node.get("class_type") for node in workflow_basic.values()]
    print(f"✓ Basic workflow has {len(workflow_basic)} nodes")
    print(f"✓ DetailDaemonSamplerNode present: {'DetailDaemonSamplerNode' in basic_nodes}")
    
    # Example 2: Enhanced workflow (with details)
    print("\n2️⃣ Creating enhanced Flux workflow (add_details=True)")
    params_enhanced = ComfyWorkflowBuilder.create_generation_params(
        model_key="flux-dev",
        prompt="A beautiful mountain landscape",
        negative_prompt="blurry, low quality",
        steps=20,
        cfg=7.0,
        add_details=True  # Enable detail enhancement
    )
    
    builder = ComfyWorkflowBuilder()
    workflow_enhanced = builder.build_prompt_workflow(params_enhanced)
    
    enhanced_nodes = [node.get("class_type") for node in workflow_enhanced.values()]
    print(f"✓ Enhanced workflow has {len(workflow_enhanced)} nodes")
    print(f"✓ DetailDaemonSamplerNode present: {'DetailDaemonSamplerNode' in enhanced_nodes}")
    
    # Example 3: Compare different model types
    print("\n3️⃣ Comparing model types with add_details=True")
    
    # Flux model
    flux_params = GenerationParams(
        model_key="flux-dev",
        prompt="Test prompt",
        add_details=True
    )
    flux_workflow = ComfyWorkflowBuilder().build_prompt_workflow(flux_params)
    flux_nodes = [node.get("class_type") for node in flux_workflow.values()]
    
    # HiDream model  
    hidream_params = GenerationParams(
        model_key="hidream",
        prompt="Test prompt",
        add_details=True
    )
    hidream_workflow = ComfyWorkflowBuilder().build_prompt_workflow(hidream_params)
    hidream_nodes = [node.get("class_type") for node in hidream_workflow.values()]
    
    # Checkpoint model (doesn't use DetailDaemonSamplerNode)
    checkpoint_params = GenerationParams(
        model_key="sdxl",
        prompt="Test prompt",
        add_details=True  # Won't affect checkpoint models
    )
    checkpoint_workflow = ComfyWorkflowBuilder().build_prompt_workflow(checkpoint_params)
    checkpoint_nodes = [node.get("class_type") for node in checkpoint_workflow.values()]
    
    print(f"✓ Flux with details: {'DetailDaemonSamplerNode' in flux_nodes}")
    print(f"✓ HiDream with details: {'DetailDaemonSamplerNode' in hidream_nodes}")
    print(f"✓ Checkpoint with details: {'DetailDaemonSamplerNode' in checkpoint_nodes}")
    
    # Example 4: Show node count differences
    print("\n4️⃣ Node count comparison")
    print(f"✓ Basic Flux workflow: {len(workflow_basic)} nodes")
    print(f"✓ Enhanced Flux workflow: {len(workflow_enhanced)} nodes")
    print(f"✓ Difference: {len(workflow_enhanced) - len(workflow_basic)} additional nodes")
    
    # Save example workflows
    print("\n5️⃣ Saving example workflows")
    
    with open("example_basic_flux.json", "w") as f:
        json.dump(workflow_basic, f, indent=2)
    print("✓ Saved example_basic_flux.json")
    
    with open("example_enhanced_flux.json", "w") as f:
        json.dump(workflow_enhanced, f, indent=2)
    print("✓ Saved example_enhanced_flux.json")
    
    # Example 5: Show practical usage patterns
    print("\n6️⃣ Practical usage examples")
    
    # For quick generation
    quick_params = ComfyWorkflowBuilder.create_generation_params(
        model_key="flux-dev",
        prompt="A cat sitting on a windowsill",
        steps=15,
        add_details=False  # Fast generation
    )
    
    # For high-quality generation
    quality_params = ComfyWorkflowBuilder.create_generation_params(
        model_key="flux-dev", 
        prompt="A cat sitting on a windowsill",
        steps=30,
        add_details=True  # High quality
    )
    
    print("✓ Quick generation: add_details=False for faster workflows")
    print("✓ Quality generation: add_details=True for enhanced results")
    
    print("\n🎉 Demo completed successfully!")
    print("\n📋 Key benefits of add_details parameter:")
    print("  • User control over detail enhancement")
    print("  • Lighter workflows by default")
    print("  • Better performance for simple use cases")
    print("  • Enhanced quality when needed")

if __name__ == "__main__":
    main()
