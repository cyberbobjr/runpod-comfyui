#!/usr/bin/env python3

import sys
import os
import json

# Add the back directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams

def generate_sample_workflows():
    """Generate sample workflows to demonstrate InpaintModelConditioning implementation."""
    
    print("🎨 Generating sample workflows with InpaintModelConditioning...")
    
    # Sample 1: Inpainting workflow
    print("\n1. Generating inpainting workflow...")
    builder1 = ComfyWorkflowBuilder()
    params1 = GenerationParams(
        model_key="sdxl",
        prompt="A beautiful restored vintage painting with vibrant colors",
        negative_prompt="damaged, scratched, faded, low quality",
        init_image="vintage_painting.png",
        inpaint_mask="damage_mask.png",
        steps=30,
        cfg=7.5,
        width=1024,
        height=1024,
        seed=42
    )
    
    workflow1 = builder1.build_prompt_workflow(params1)
    
    # Save workflow
    with open("sample_inpainting_workflow.json", "w") as f:
        json.dump(workflow1, f, indent=2)
    
    print(f"✓ Inpainting workflow saved with {len(workflow1)} nodes")
    
    # Sample 2: Outpainting workflow  
    print("\n2. Generating outpainting workflow...")
    builder2 = ComfyWorkflowBuilder()
    params2 = GenerationParams(
        model_key="flux-dev",
        prompt="Expand this landscape with rolling hills and distant mountains",
        negative_prompt="cropped, cut off, borders, frame",
        init_image="landscape.png",
        outpaint_padding=256,
        steps=20,
        cfg=1.0,
        width=1024,
        height=1024,
        seed=123
    )
    
    workflow2 = builder2.build_prompt_workflow(params2)
    
    # Save workflow
    with open("sample_outpainting_workflow.json", "w") as f:
        json.dump(workflow2, f, indent=2)
    
    print(f"✓ Outpainting workflow saved with {len(workflow2)} nodes")
    
    # Sample 3: Combined workflow
    print("\n3. Generating combined inpainting + outpainting workflow...")
    builder3 = ComfyWorkflowBuilder()
    params3 = GenerationParams(
        model_key="sdxl",
        prompt="A magnificent restored and expanded portrait in Renaissance style",
        negative_prompt="damaged, incomplete, cropped, modern style",
        init_image="portrait.png",
        inpaint_mask="portrait_damage.png",
        outpaint_padding=128,
        steps=35,
        cfg=8.0,
        width=1024,
        height=1024,
        seed=456
    )
    
    workflow3 = builder3.build_prompt_workflow(params3)
    
    # Save workflow
    with open("sample_combined_workflow.json", "w") as f:
        json.dump(workflow3, f, indent=2)
    
    print(f"✓ Combined workflow saved with {len(workflow3)} nodes")
    
    # Print summary of InpaintModelConditioning usage
    print("\n📋 InpaintModelConditioning Node Summary:")
    
    workflows = [
        ("Inpainting", workflow1),
        ("Outpainting", workflow2), 
        ("Combined", workflow3)
    ]
    
    for name, workflow in workflows:
        for node_id, node in workflow.items():
            if node.get("class_type") == "InpaintModelConditioning":
                print(f"\n{name} Workflow - Node ID: {node_id}")
                print(f"  Inputs: {list(node['inputs'].keys())}")
                for input_name, input_ref in node['inputs'].items():
                    print(f"    {input_name}: {input_ref}")
                break
    
    print("\n🎉 Sample workflows generated successfully!")

if __name__ == "__main__":
    generate_sample_workflows()
