#!/usr/bin/env python3
"""
Example usage of InpaintModelConditioning for inpainting and outpainting workflows.

**Description:** Demonstrates how to use the new InpaintModelConditioning node
for inpainting and outpainting with ComfyWorkflowBuilder.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams
import json

def main():
    """Demonstrate InpaintModelConditioning usage."""
    print("🎨 InpaintModelConditioning Feature Demo")
    print("=" * 50)
    
    # Example 1: Inpainting workflow
    print("\n1️⃣ Creating inpainting workflow")
    params_inpaint = ComfyWorkflowBuilder.create_generation_params(
        model_key="sdxl",
        prompt="A beautiful restored ancient painting",
        negative_prompt="damaged, torn, missing parts, low quality",
        steps=30,
        cfg=7.5,
        init_image="artwork_original.png",
        inpaint_mask="damaged_areas_mask.png"
    )
    
    builder = ComfyWorkflowBuilder()
    workflow_inpaint = builder.build_prompt_workflow(params_inpaint)
    
    inpaint_nodes = [node.get("class_type") for node in workflow_inpaint.values()]
    print(f"✓ Inpainting workflow has {len(workflow_inpaint)} nodes")
    print(f"✓ InpaintModelConditioning present: {'InpaintModelConditioning' in inpaint_nodes}")
    print(f"✓ LoadImageMask present: {'LoadImageMask' in inpaint_nodes}")
    
    # Example 2: Outpainting workflow
    print("\n2️⃣ Creating outpainting workflow")
    params_outpaint = ComfyWorkflowBuilder.create_generation_params(
        model_key="flux-dev",
        prompt="Expand this landscape to show more of the scenery",
        negative_prompt="cropped, cut off, incomplete edges",
        steps=25,
        cfg=8.0,
        init_image="landscape_cropped.png",
        outpaint_padding=128
    )
    
    builder = ComfyWorkflowBuilder()
    workflow_outpaint = builder.build_prompt_workflow(params_outpaint)
    
    outpaint_nodes = [node.get("class_type") for node in workflow_outpaint.values()]
    print(f"✓ Outpainting workflow has {len(workflow_outpaint)} nodes")
    print(f"✓ InpaintModelConditioning present: {'InpaintModelConditioning' in outpaint_nodes}")
    print(f"✓ ImagePadForOutpaint present: {'ImagePadForOutpaint' in outpaint_nodes}")
    
    # Example 3: Combined inpainting + outpainting
    print("\n3️⃣ Creating combined inpainting and outpainting workflow")
    params_combined = ComfyWorkflowBuilder.create_generation_params(
        model_key="hidream",
        prompt="Restore the damaged areas and expand the canvas",
        negative_prompt="damaged, incomplete, cropped, low quality",
        steps=35,
        cfg=7.0,
        init_image="portrait_damaged_cropped.png",
        inpaint_mask="damage_mask.png",
        outpaint_padding=96
    )
    
    builder = ComfyWorkflowBuilder()
    workflow_combined = builder.build_prompt_workflow(params_combined)
    
    combined_nodes = [node.get("class_type") for node in workflow_combined.values()]
    print(f"✓ Combined workflow has {len(workflow_combined)} nodes")
    print(f"✓ InpaintModelConditioning present: {'InpaintModelConditioning' in combined_nodes}")
    print(f"✓ LoadImageMask present: {'LoadImageMask' in combined_nodes}")
    print(f"✓ ImagePadForOutpaint present: {'ImagePadForOutpaint' in combined_nodes}")
    
    # Example 4: Regular img2img (no InpaintModelConditioning)
    print("\n4️⃣ Creating regular img2img workflow (for comparison)")
    params_img2img = ComfyWorkflowBuilder.create_generation_params(
        model_key="sdxl",
        prompt="Transform this photo into a painting",
        negative_prompt="photographic, realistic",
        steps=25,
        cfg=7.5,
        init_image="photo.png"
    )
    
    builder = ComfyWorkflowBuilder()
    workflow_img2img = builder.build_prompt_workflow(params_img2img)
    
    img2img_nodes = [node.get("class_type") for node in workflow_img2img.values()]
    print(f"✓ Img2img workflow has {len(workflow_img2img)} nodes")
    print(f"✓ InpaintModelConditioning present: {'InpaintModelConditioning' in img2img_nodes}")
    print(f"✓ VAEEncode present: {'VAEEncode' in img2img_nodes}")
    
    # Save example workflows
    print("\n5️⃣ Saving example workflows")
    
    with open("example_inpainting.json", "w") as f:
        json.dump(workflow_inpaint, f, indent=2)
    print("✓ Saved example_inpainting.json")
    
    with open("example_outpainting.json", "w") as f:
        json.dump(workflow_outpaint, f, indent=2)
    print("✓ Saved example_outpainting.json")
    
    with open("example_inpaint_outpaint_combined.json", "w") as f:
        json.dump(workflow_combined, f, indent=2)
    print("✓ Saved example_inpaint_outpaint_combined.json")
    
    with open("example_img2img_regular.json", "w") as f:
        json.dump(workflow_img2img, f, indent=2)
    print("✓ Saved example_img2img_regular.json")
    
    # Show data flow analysis
    print("\n6️⃣ Data flow analysis")
    
    # Find InpaintModelConditioning node in inpainting workflow
    for node_id, node in workflow_inpaint.items():
        if node.get("class_type") == "InpaintModelConditioning":
            inputs = node["inputs"]
            print(f"✓ InpaintModelConditioning inputs:")
            print(f"  - positive: {inputs.get('positive')}")
            print(f"  - negative: {inputs.get('negative')}")
            print(f"  - vae: {inputs.get('vae')}")
            print(f"  - pixels: {inputs.get('pixels')}")
            print(f"  - mask: {inputs.get('mask', 'N/A')}")
            break
    
    print("\n🎉 Demo completed successfully!")
    print("\n📋 Key benefits of InpaintModelConditioning:")
    print("  • Proper conditioning for inpainting tasks")
    print("  • Support for outpainting with padding")
    print("  • Compatible with all model types (SDXL, Flux, HiDream)")
    print("  • Seamless data flow through the pipeline")
    print("  • Automatic handling of masks and pixels")
    print("  • Regular workflows remain unchanged")

if __name__ == "__main__":
    main()
