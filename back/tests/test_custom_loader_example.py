#!/usr/bin/env python3
"""
Example demonstrating how to extend the ComfyWorkflowBuilder with a custom model loader.

**Description:** This example shows how the Factory pattern makes it easy to add
support for new model types without modifying the core ComfyWorkflowBuilder class.
"""

import sys
import os
import json

# Add the back directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.comfy_workflow_builder import (
    ComfyWorkflowBuilder, 
    ModelLoaderFactory, 
    BaseModelLoader,
    GenerationParams
)


class SD3ModelLoader(BaseModelLoader):
    """
    Custom model loader for SD3 models.
    
    **Description:** Example implementation of a custom loader that could be
    added to support SD3 models with their specific requirements.
    """
    
    def create_loader_nodes(self, builder: ComfyWorkflowBuilder, model_path: str):
        """Create loader nodes for SD3 models."""
        # Create separate loaders for SD3
        unet_id = builder._next_id()
        clip_id = builder._next_id()
        vae_id = builder._next_id()
        model_sampling_id = builder._next_id()
        
        # UNet Loader for SD3
        builder.nodes[unet_id] = {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": f"SD3/{model_path}",
                "weight_dtype": "fp16"
            },
            "_meta": {"title": "Load SD3 Diffusion Model"}
        }
        
        # Triple CLIP Loader for SD3
        builder.nodes[clip_id] = {
            "class_type": "TripleCLIPLoader",
            "inputs": {
                "clip_name1": "SD3/clip_l.safetensors",
                "clip_name2": "SD3/clip_g.safetensors", 
                "clip_name3": "SD3/t5xxl_fp16.safetensors"
            },
            "_meta": {"title": "TripleCLIPLoader"}
        }
        
        # VAE Loader for SD3
        builder.nodes[vae_id] = {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "SD3/sd3_vae.safetensors"},
            "_meta": {"title": "Load SD3 VAE"}
        }
        
        # ModelSamplingSD3
        builder.nodes[model_sampling_id] = {
            "class_type": "ModelSamplingSD3",
            "inputs": {
                "shift": 3.0,
                "model": [unet_id, 0]
            },
            "_meta": {"title": "ModelSamplingSD3"}
        }
        
        return [model_sampling_id, 0], [clip_id, 0], [vae_id, 0]


def demonstrate_custom_loader():
    """Demonstrate how to register and use a custom model loader."""
    
    print("=== Custom Model Loader Demo ===\n")
    
    # Step 1: Register the custom loader
    print("1. Registering custom SD3 loader...")
    ModelLoaderFactory.register_loader("sd3", SD3ModelLoader())
    
    # Step 2: Verify it's registered
    print("2. Supported model types:", ModelLoaderFactory.get_supported_types())
    
    # Step 3: Add SD3 model to registry (normally would be in config)
    from services.comfy_workflow_builder import MODEL_REGISTRY
    MODEL_REGISTRY["sd3-medium"] = {
        "model_type": "sd3",
        "filename": "sd3_medium.safetensors"
    }
    
    # Step 4: Generate workflow with the custom loader
    print("3. Generating workflow with custom SD3 loader...")
    
    params = GenerationParams(
        model_key="sd3-medium",
        prompt="A cyberpunk cityscape with neon lights",
        negative_prompt="blurry, low quality",
        steps=25,
        cfg=7.0,
        width=1024,
        height=1024,
        seed=12345
    )
    
    builder = ComfyWorkflowBuilder()
    workflow = builder.build_prompt_workflow(params)
    
    # Step 5: Analyze the generated workflow
    print(f"4. Generated workflow with {len(workflow)} nodes")
    
    # Find our custom nodes
    sd3_nodes = []
    for node_id, node in workflow.items():
        if any(keyword in node["class_type"] for keyword in ["TripleCLIPLoader", "ModelSamplingSD3"]):
            sd3_nodes.append((node_id, node["class_type"]))
    
    print("5. Found custom SD3 nodes:")
    for node_id, class_type in sd3_nodes:
        print(f"   - Node {node_id}: {class_type}")
    
    # Step 6: Save example workflow
    with open("example_sd3_workflow.json", "w") as f:
        json.dump(workflow, f, indent=2)
    
    print("6. Saved example workflow to 'example_sd3_workflow.json'")
    
    print("\n=== Benefits of Factory Pattern ===")
    print("✓ No modification of core ComfyWorkflowBuilder class needed")
    print("✓ Clean separation of concerns - each loader handles its own logic")
    print("✓ Easy to add new model types at runtime")
    print("✓ Consistent interface for all model loaders")
    print("✓ Extensible - can register loaders from external plugins")


if __name__ == "__main__":
    demonstrate_custom_loader()
