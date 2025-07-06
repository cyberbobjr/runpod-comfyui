#!/usr/bin/env python3

import sys
import os
import json

# Add the back directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams

def test_data_flow():
    """Test that InpaintModelConditioning outputs are properly used in the pipeline."""
    print("Testing data flow with InpaintModelConditioning...")
    
    builder = ComfyWorkflowBuilder()
    
    # Test inpainting workflow
    params = GenerationParams(
        model_key="sdxl",
        prompt="A beautiful restored painting",
        negative_prompt="damaged, incomplete", 
        init_image="test_image.png",
        inpaint_mask="test_mask.png"
    )
    
    workflow = builder.build_prompt_workflow(params)
    
    # Find InpaintModelConditioning node
    inpaint_node_id = None
    for node_id, node in workflow.items():
        if node.get("class_type") == "InpaintModelConditioning":
            inpaint_node_id = node_id
            break
    
    if inpaint_node_id is None:
        print("ERROR: InpaintModelConditioning node not found!")
        return False
    
    print(f"Found InpaintModelConditioning node at ID {inpaint_node_id}")
    
    # Check if sampler uses the outputs from InpaintModelConditioning
    sampler_node = None
    sampler_node_id = None
    for node_id, node in workflow.items():
        if node.get("class_type") in ["KSampler", "SamplerCustomAdvanced"]:
            sampler_node = node
            sampler_node_id = node_id
            break
    
    if sampler_node is None:
        print("ERROR: No sampler node found!")
        return False
        
    print(f"Found sampler node at ID {sampler_node_id}")
    
    # Check that sampler uses positive, negative, and latent from InpaintModelConditioning
    sampler_inputs = sampler_node["inputs"]
    print(f"Sampler inputs: {json.dumps(sampler_inputs, indent=2)}")
    
    # Check positive conditioning
    if "positive" in sampler_inputs:
        pos_ref = sampler_inputs["positive"]
        if pos_ref[0] == inpaint_node_id and pos_ref[1] == 0:
            print("✓ Sampler uses positive conditioning from InpaintModelConditioning")
        else:
            print(f"ERROR: Sampler positive conditioning {pos_ref} doesn't match InpaintModelConditioning output")
            return False
    
    # Check negative conditioning  
    if "negative" in sampler_inputs:
        neg_ref = sampler_inputs["negative"]
        if neg_ref[0] == inpaint_node_id and neg_ref[1] == 1:
            print("✓ Sampler uses negative conditioning from InpaintModelConditioning")
        else:
            print(f"ERROR: Sampler negative conditioning {neg_ref} doesn't match InpaintModelConditioning output")
            return False
    
    # Check latent
    if "latent_image" in sampler_inputs:
        latent_ref = sampler_inputs["latent_image"]
        if latent_ref[0] == inpaint_node_id and latent_ref[1] == 2:
            print("✓ Sampler uses latent from InpaintModelConditioning")
        else:
            print(f"ERROR: Sampler latent {latent_ref} doesn't match InpaintModelConditioning output")
            return False
    
    print("✓ Data flow test passed!")
    return True

if __name__ == "__main__":
    success = test_data_flow()
    
    if success:
        print("\n🎉 Data flow test passed! InpaintModelConditioning outputs are properly connected.")
    else:
        print("\n❌ Data flow test failed!")
        sys.exit(1)
