import unittest
import json
import sys
import os
from typing import Dict, Any

# Add the back directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams, LoRA, MODEL_REGISTRY


class TestComfyWorkflowBuilder(unittest.TestCase):
    """
    Unit tests for ComfyWorkflowBuilder class.
    
    **Description:** Tests the workflow generation functionality to ensure 
    correct ComfyUI workflows are created from GenerationParams.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.builder = ComfyWorkflowBuilder()

    def test_basic_sdxl_workflow_generation(self):
        """
        Test basic SDXL workflow generation.
        
        **Description:** Verifies that a basic SDXL workflow is generated correctly 
        with proper node structure and connections.
        """
        params = GenerationParams(
            model_key="sdxl",
            prompt="A beautiful landscape",
            negative_prompt="blurry, bad quality",
            steps=30,
            cfg=7.5,
            width=1024,
            height=1024,
            seed=42
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        # Verify workflow structure
        self.assertIsInstance(workflow, dict)
        self.assertGreater(len(workflow), 0)
        
        # Verify node IDs are strings
        for node_id in workflow.keys():
            self.assertIsInstance(node_id, str)
        
        # Verify essential nodes exist
        node_classes = [node.get("class_type") for node in workflow.values()]
        self.assertIn("CheckpointLoaderSimple", node_classes)
        self.assertIn("CLIPTextEncode", node_classes)
        self.assertIn("KSampler", node_classes)
        self.assertIn("VAEDecode", node_classes)
        self.assertIn("SaveImage", node_classes)

    def test_flux_workflow_generation(self):
        """
        Test Flux workflow generation.
        
        **Description:** Verifies that a Flux workflow is generated with 
        proper Flux-specific components like UNETLoader, DualCLIPLoader, etc.
        """
        params = GenerationParams(
            model_key="flux-dev",
            prompt="A futuristic cityscape",
            negative_prompt="ugly, bad, wrong",
            steps=24,
            cfg=4.0,
            width=1024,
            height=1024,
            seed=808466373884902
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        # Verify Flux-specific components
        node_classes = [node.get("class_type") for node in workflow.values()]
        self.assertIn("UNETLoader", node_classes)
        self.assertIn("DualCLIPLoader", node_classes)
        self.assertIn("VAELoader", node_classes)
        self.assertIn("ModelSamplingFlux", node_classes)
        self.assertIn("FluxGuidance", node_classes)
        self.assertIn("SamplerCustomAdvanced", node_classes)
        self.assertIn("TeaCache", node_classes)
        self.assertIn("Seed Generator", node_classes)
        
        # DetailDaemonSamplerNode should not be present by default (add_details=False)
        self.assertNotIn("DetailDaemonSamplerNode", node_classes)
        
        # Test with add_details=True
        params_with_details = GenerationParams(
            model_key="flux-dev",
            prompt="High quality portrait",
            add_details=True
        )
        
        workflow_with_details = self.builder.build_prompt_workflow(params_with_details)
        node_classes_with_details = [node.get("class_type") for node in workflow_with_details.values()]
        
        # DetailDaemonSamplerNode should be present when add_details=True
        self.assertIn("DetailDaemonSamplerNode", node_classes_with_details)

    def test_hidream_workflow_generation(self):
        """
        Test HiDream workflow generation.
        
        **Description:** Verifies that a HiDream workflow is generated with 
        proper HiDream-specific components like QuadrupleCLIPLoader and ModelSamplingSD3.
        """
        params = GenerationParams(
            model_key="hidream",
            prompt="A portrait of a person",
            negative_prompt="bad quality",
            steps=20,
            cfg=6.0
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        # Verify HiDream-specific components
        node_classes = [node.get("class_type") for node in workflow.values()]
        self.assertIn("UNETLoader", node_classes)
        self.assertIn("QuadrupleCLIPLoader", node_classes)
        self.assertIn("ModelSamplingSD3", node_classes)
        self.assertIn("SamplerCustomAdvanced", node_classes)
        self.assertIn("CFGGuider", node_classes)

    def test_optimization_flags(self):
        """
        Test TeaCache and ClearCache flags.
        
        **Description:** Verifies that optimization flags control whether 
        TeaCache and easy clearCacheAll nodes are included in the workflow.
        """
        # Test with optimizations enabled
        params = GenerationParams(
            model_key="flux-dev",
            prompt="Test prompt",
            enable_tea_cache=True,
            enable_clear_cache=True
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        node_classes = [node.get("class_type") for node in workflow.values()]
        
        self.assertIn("TeaCache", node_classes)
        self.assertIn("easy clearCacheAll", node_classes)
        
        # Test with optimizations disabled
        builder2 = ComfyWorkflowBuilder()
        params2 = GenerationParams(
            model_key="flux-dev",
            prompt="Test prompt",
            enable_tea_cache=False,
            enable_clear_cache=False
        )
        
        workflow2 = builder2.build_prompt_workflow(params2)
        node_classes2 = [node.get("class_type") for node in workflow2.values()]
        
        self.assertNotIn("TeaCache", node_classes2)
        self.assertNotIn("easy clearCacheAll", node_classes2)

    def test_checkpoint_no_extra_loaders(self):
        """
        Test that checkpoint models don't have extra loaders.
        
        **Description:** Verifies that checkpoint models (SDXL, SD1.5) use 
        only CheckpointLoaderSimple and don't have separate UNet/CLIP loaders.
        """
        params = GenerationParams(
            model_key="sdxl",
            prompt="Test prompt"
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        node_classes = [node.get("class_type") for node in workflow.values()]
        
        # Should have checkpoint loader but not separate loaders
        self.assertIn("CheckpointLoaderSimple", node_classes)
        self.assertNotIn("UNETLoader", node_classes)
        self.assertNotIn("DualCLIPLoader", node_classes)
        self.assertNotIn("QuadrupleCLIPLoader", node_classes)

    def test_lora_workflow_generation(self):
        """
        Test workflow generation with LoRAs.
        
        **Description:** Verifies that LoRAs are properly added to the workflow 
        using the Power Lora Loader component.
        """
        loras = [
            LoRA(name="style_lora.safetensors", strength=0.8),
            LoRA(name="character_lora.safetensors", strength=0.6)
        ]
        
        params = GenerationParams(
            model_key="flux-dev",
            prompt="Anime character in detailed style",
            loras=loras
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        # Find Power Lora Loader node
        lora_nodes = [
            node for node in workflow.values()
            if node.get("class_type") == "Power Lora Loader (rgthree)"
        ]
        
        self.assertEqual(len(lora_nodes), 1)
        lora_node = lora_nodes[0]
        
        # Verify LoRA inputs
        inputs = lora_node["inputs"]
        self.assertIn("lora_1", inputs)
        self.assertIn("lora_2", inputs)
        self.assertEqual(inputs["lora_1"]["lora"], "style_lora.safetensors")
        self.assertEqual(inputs["lora_1"]["strength"], 0.8)
        self.assertTrue(inputs["lora_1"]["on"])

    def test_node_id_generation(self):
        """
        Test that node IDs are generated as strings and incremented correctly.
        
        **Description:** Verifies the internal node ID generation mechanism 
        produces unique string IDs.
        """
        builder = ComfyWorkflowBuilder()
        
        # Test initial ID
        first_id = builder._next_id()
        self.assertIsInstance(first_id, str)
        self.assertEqual(first_id, "1")
        
        # Test incremental IDs
        second_id = builder._next_id()
        self.assertEqual(second_id, "2")
        
        third_id = builder._next_id()
        self.assertEqual(third_id, "3")

    def test_model_registry_lookup(self):
        """
        Test model registry lookup functionality.
        
        **Description:** Verifies that model configurations are correctly 
        retrieved from the MODEL_REGISTRY.
        """
        # Test valid model keys
        self.assertIn("sdxl", MODEL_REGISTRY)
        self.assertIn("flux-dev", MODEL_REGISTRY)
        
        sdxl_meta = MODEL_REGISTRY["sdxl"]
        self.assertEqual(sdxl_meta["model_type"], "checkpoint")
        self.assertIn("filename", sdxl_meta)
        
        flux_meta = MODEL_REGISTRY["flux-dev"]
        self.assertEqual(flux_meta["model_type"], "flux")
        self.assertIn("filename", flux_meta)

    def test_invalid_model_key_raises_error(self):
        """
        Test that invalid model keys raise appropriate errors.
        
        **Description:** Verifies that using an unknown model key 
        raises a ValueError with appropriate message.
        """
        params = GenerationParams(
            model_key="unknown_model",
            prompt="Test prompt"
        )
        
        with self.assertRaises(ValueError) as context:
            self.builder.build_prompt_workflow(params)
        
        self.assertIn("Unknown model key: unknown_model", str(context.exception))

    def test_create_generation_params_factory(self):
        """
        Test the factory method for creating GenerationParams.
        
        **Description:** Verifies that the static factory method creates 
        GenerationParams with proper defaults and overrides.
        """
        # Test basic creation
        params = ComfyWorkflowBuilder.create_generation_params(
            model_key="sdxl",
            prompt="Test prompt"
        )
        
        self.assertEqual(params.model_key, "sdxl")
        self.assertEqual(params.prompt, "Test prompt")
        self.assertEqual(params.sampler, "euler")  # Default value
        self.assertEqual(params.steps, 30)  # Default value
        
        # Test with overrides
        params_with_overrides = ComfyWorkflowBuilder.create_generation_params(
            model_key="flux-dev",
            prompt="Another prompt",
            steps=20,
            cfg=3.5,
            width=512,
            height=768
        )
        
        self.assertEqual(params_with_overrides.steps, 20)
        self.assertEqual(params_with_overrides.cfg, 3.5)
        self.assertEqual(params_with_overrides.width, 512)
        self.assertEqual(params_with_overrides.height, 768)

    def test_workflow_json_serialization(self):
        """
        Test that generated workflows can be properly serialized to JSON.
        
        **Description:** Verifies that the workflow output is JSON-serializable
        for use with ComfyUI API.
        """
        params = GenerationParams(
            model_key="sdxl",
            prompt="Serialization test"
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        # Should not raise an exception
        json_str = json.dumps(workflow, indent=2)
        self.assertIsInstance(json_str, str)
        self.assertGreater(len(json_str), 0)
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        self.assertEqual(workflow, parsed)

    def test_controlnet_not_implemented_yet(self):
        """
        Test ControlNet functionality (placeholder for future implementation).
        
        **Description:** Currently ControlNet is not fully implemented, 
        this test serves as a placeholder for future functionality.
        """
        params = GenerationParams(
            model_key="sdxl",
            prompt="ControlNet test",
            controlnet_image="test_image.png",
            controlnet_preprocessor="canny",
            controlnet_model="control_canny"
        )
        
        # For now, just verify it doesn't crash
        workflow = self.builder.build_prompt_workflow(params)
        self.assertIsInstance(workflow, dict)

    def test_node_metadata_structure(self):
        """
        Test that all nodes have proper metadata structure.
        
        **Description:** Verifies that generated nodes have the required 
        _meta field with title information.
        """
        params = GenerationParams(
            model_key="flux-dev",
            prompt="Metadata test"
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        for node_id, node in workflow.items():
            # Every node should have required fields
            self.assertIn("class_type", node)
            self.assertIn("inputs", node)
            self.assertIn("_meta", node)
            
            # _meta should have title
            self.assertIn("title", node["_meta"])
            self.assertIsInstance(node["_meta"]["title"], str)
            self.assertGreater(len(node["_meta"]["title"]), 0)

    def test_seed_generator_connections(self):
        """
        Test that Seed Generator is correctly connected to samplers.
        
        **Description:** Verifies that the Seed Generator node is properly
        connected to KSampler (for checkpoint models) and SamplerCustom (for Flux models).
        """
        # Test with checkpoint model (uses KSampler)
        params = GenerationParams(
            model_key="sdxl",
            prompt="Test seed connection",
            seed=12345
        )
        
        builder = ComfyWorkflowBuilder()
        workflow = builder.build_prompt_workflow(params)
        
        # Find Seed Generator and KSampler nodes
        seed_node_id = None
        sampler_node_id = None
        
        for node_id, node in workflow.items():
            if node["class_type"] == "Seed Generator":
                seed_node_id = node_id
            elif node["class_type"] == "KSampler":
                sampler_node_id = node_id
        
        self.assertIsNotNone(seed_node_id, "Seed Generator node not found")
        self.assertIsNotNone(sampler_node_id, "KSampler node not found")
        
        # Verify KSampler uses seed from Seed Generator
        sampler_node = workflow[sampler_node_id]
        self.assertEqual(sampler_node["inputs"]["seed"], [seed_node_id, 0])
        
        # Test with Flux model (uses SamplerCustom)
        params = GenerationParams(
            model_key="flux-dev",
            prompt="Test seed connection",
            seed=67890
        )
        
        builder = ComfyWorkflowBuilder()
        workflow = builder.build_prompt_workflow(params)
        
        # Find Seed Generator and SamplerCustom nodes
        seed_node_id = None
        sampler_node_id = None
        
        for node_id, node in workflow.items():
            if node["class_type"] == "Seed Generator":
                seed_node_id = node_id
            elif node["class_type"] == "SamplerCustomAdvanced":
                sampler_node_id = node_id
        
        self.assertIsNotNone(seed_node_id, "Seed Generator node not found")
        self.assertIsNotNone(sampler_node_id, "SamplerCustomAdvanced node not found")
        
        # Verify SamplerCustomAdvanced uses noise from Seed Generator
        sampler_node = workflow[sampler_node_id]
        self.assertEqual(sampler_node["inputs"]["noise"], [seed_node_id, 0])

    def test_inpainting_workflow_generation(self):
        """
        Test inpainting workflow generation with InpaintModelConditioning.
        
        **Description:** Verifies that inpainting workflows correctly use
        InpaintModelConditioning node with proper data flow.
        """
        params = GenerationParams(
            model_key="sdxl",
            prompt="A beautiful restored painting",
            negative_prompt="damaged, incomplete",
            init_image="test_image.png",
            inpaint_mask="test_mask.png"
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        # Verify inpainting-specific components
        node_classes = [node.get("class_type") for node in workflow.values()]
        self.assertIn("LoadImage", node_classes)
        self.assertIn("LoadImageMask", node_classes)
        self.assertIn("InpaintModelConditioning", node_classes)
        
        # Find InpaintModelConditioning node
        inpaint_node = None
        for node in workflow.values():
            if node.get("class_type") == "InpaintModelConditioning":
                inpaint_node = node
                break
        
        self.assertIsNotNone(inpaint_node, "InpaintModelConditioning node should be present")
        
        # Verify inputs
        inputs = inpaint_node["inputs"]
        self.assertIn("positive", inputs)
        self.assertIn("negative", inputs)
        self.assertIn("vae", inputs)
        self.assertIn("pixels", inputs)
        self.assertIn("mask", inputs)

    def test_outpainting_workflow_generation(self):
        """
        Test outpainting workflow generation with InpaintModelConditioning.
        
        **Description:** Verifies that outpainting workflows correctly use
        InpaintModelConditioning node with ImagePadForOutpaint.
        """
        params = GenerationParams(
            model_key="flux-dev",
            prompt="Expand this landscape",
            negative_prompt="cropped, cut off",
            init_image="test_image.png",
            outpaint_padding=128
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        # Verify outpainting-specific components
        node_classes = [node.get("class_type") for node in workflow.values()]
        self.assertIn("LoadImage", node_classes)
        self.assertIn("ImagePadForOutpaint", node_classes)
        self.assertIn("InpaintModelConditioning", node_classes)
        
        # Find InpaintModelConditioning node
        inpaint_node = None
        for node in workflow.values():
            if node.get("class_type") == "InpaintModelConditioning":
                inpaint_node = node
                break
        
        self.assertIsNotNone(inpaint_node, "InpaintModelConditioning node should be present")
        
        # Verify inputs (should not have mask for outpainting)
        inputs = inpaint_node["inputs"]
        self.assertIn("positive", inputs)
        self.assertIn("negative", inputs)
        self.assertIn("vae", inputs)
        self.assertIn("pixels", inputs)
        self.assertNotIn("mask", inputs)

    def test_combined_inpaint_outpaint_workflow(self):
        """
        Test combined inpainting and outpainting workflow.
        
        **Description:** Verifies that workflows with both inpainting and outpainting
        use the correct processing order and node connections.
        """
        params = GenerationParams(
            model_key="hidream",
            prompt="Restore and expand this artwork",
            negative_prompt="damaged, incomplete",
            init_image="test_image.png",
            inpaint_mask="test_mask.png",
            outpaint_padding=64
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        # Verify all components are present
        node_classes = [node.get("class_type") for node in workflow.values()]
        self.assertIn("LoadImage", node_classes)
        self.assertIn("LoadImageMask", node_classes)
        self.assertIn("ImagePadForOutpaint", node_classes)
        self.assertIn("InpaintModelConditioning", node_classes)
        
        # Find InpaintModelConditioning node
        inpaint_node = None
        for node in workflow.values():
            if node.get("class_type") == "InpaintModelConditioning":
                inpaint_node = node
                break
        
        self.assertIsNotNone(inpaint_node, "InpaintModelConditioning node should be present")
        
        # Verify inputs (should have mask when both are enabled)
        inputs = inpaint_node["inputs"]
        self.assertIn("positive", inputs)
        self.assertIn("negative", inputs)
        self.assertIn("vae", inputs)
        self.assertIn("pixels", inputs)
        self.assertIn("mask", inputs)

    def test_workflow_json_serialization(self):
        """
        Test that generated workflows can be properly serialized to JSON.
        
        **Description:** Verifies that the workflow output is JSON-serializable
        for use with ComfyUI API.
        """
        params = GenerationParams(
            model_key="sdxl",
            prompt="Serialization test"
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        # Should not raise an exception
        json_str = json.dumps(workflow, indent=2)
        self.assertIsInstance(json_str, str)
        self.assertGreater(len(json_str), 0)
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        self.assertEqual(workflow, parsed)

    def test_controlnet_not_implemented_yet(self):
        """
        Test ControlNet functionality (placeholder for future implementation).
        
        **Description:** Currently ControlNet is not fully implemented, 
        this test serves as a placeholder for future functionality.
        """
        params = GenerationParams(
            model_key="sdxl",
            prompt="ControlNet test",
            controlnet_image="test_image.png",
            controlnet_preprocessor="canny",
            controlnet_model="control_canny"
        )
        
        # For now, just verify it doesn't crash
        workflow = self.builder.build_prompt_workflow(params)
        self.assertIsInstance(workflow, dict)

    def test_node_metadata_structure(self):
        """
        Test that all nodes have proper metadata structure.
        
        **Description:** Verifies that generated nodes have the required 
        _meta field with title information.
        """
        params = GenerationParams(
            model_key="flux-dev",
            prompt="Metadata test"
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        for node_id, node in workflow.items():
            # Every node should have required fields
            self.assertIn("class_type", node)
            self.assertIn("inputs", node)
            self.assertIn("_meta", node)
            
            # _meta should have title
            self.assertIn("title", node["_meta"])
            self.assertIsInstance(node["_meta"]["title"], str)
            self.assertGreater(len(node["_meta"]["title"]), 0)

    def test_seed_generator_connections(self):
        """
        Test that Seed Generator is correctly connected to samplers.
        
        **Description:** Verifies that the Seed Generator node is properly
        connected to KSampler (for checkpoint models) and SamplerCustom (for Flux models).
        """
        # Test with checkpoint model (uses KSampler)
        params = GenerationParams(
            model_key="sdxl",
            prompt="Test seed connection",
            seed=12345
        )
        
        builder = ComfyWorkflowBuilder()
        workflow = builder.build_prompt_workflow(params)
        
        # Find Seed Generator and KSampler nodes
        seed_node_id = None
        sampler_node_id = None
        
        for node_id, node in workflow.items():
            if node["class_type"] == "Seed Generator":
                seed_node_id = node_id
            elif node["class_type"] == "KSampler":
                sampler_node_id = node_id
        
        self.assertIsNotNone(seed_node_id, "Seed Generator node not found")
        self.assertIsNotNone(sampler_node_id, "KSampler node not found")
        
        # Verify KSampler uses seed from Seed Generator
        sampler_node = workflow[sampler_node_id]
        self.assertEqual(sampler_node["inputs"]["seed"], [seed_node_id, 0])
        
        # Test with Flux model (uses SamplerCustom)
        params = GenerationParams(
            model_key="flux-dev",
            prompt="Test seed connection",
            seed=67890
        )
        
        builder = ComfyWorkflowBuilder()
        workflow = builder.build_prompt_workflow(params)
        
        # Find Seed Generator and SamplerCustom nodes
        seed_node_id = None
        sampler_node_id = None
        
        for node_id, node in workflow.items():
            if node["class_type"] == "Seed Generator":
                seed_node_id = node_id
            elif node["class_type"] == "SamplerCustomAdvanced":
                sampler_node_id = node_id
        
        self.assertIsNotNone(seed_node_id, "Seed Generator node not found")
        self.assertIsNotNone(sampler_node_id, "SamplerCustomAdvanced node not found")
        
        # Verify SamplerCustomAdvanced uses noise from Seed Generator
        sampler_node = workflow[sampler_node_id]
        self.assertEqual(sampler_node["inputs"]["noise"], [seed_node_id, 0])

    def test_inpainting_workflow_generation(self):
        """
        Test inpainting workflow generation with InpaintModelConditioning.
        
        **Description:** Verifies that inpainting workflows correctly use
        InpaintModelConditioning node with proper data flow.
        """
        params = GenerationParams(
            model_key="sdxl",
            prompt="A beautiful restored painting",
            negative_prompt="damaged, incomplete",
            init_image="test_image.png",
            inpaint_mask="test_mask.png"
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        # Verify inpainting-specific components
        node_classes = [node.get("class_type") for node in workflow.values()]
        self.assertIn("LoadImage", node_classes)
        self.assertIn("LoadImageMask", node_classes)
        self.assertIn("InpaintModelConditioning", node_classes)
        
        # Find InpaintModelConditioning node
        inpaint_node = None
        for node in workflow.values():
            if node.get("class_type") == "InpaintModelConditioning":
                inpaint_node = node
                break
        
        self.assertIsNotNone(inpaint_node, "InpaintModelConditioning node should be present")
        
        # Verify inputs
        inputs = inpaint_node["inputs"]
        self.assertIn("positive", inputs)
        self.assertIn("negative", inputs)
        self.assertIn("vae", inputs)
        self.assertIn("pixels", inputs)
        self.assertIn("mask", inputs)

    def test_outpainting_workflow_generation(self):
        """
        Test outpainting workflow generation with InpaintModelConditioning.
        
        **Description:** Verifies that outpainting workflows correctly use
        InpaintModelConditioning node with ImagePadForOutpaint.
        """
        params = GenerationParams(
            model_key="flux-dev",
            prompt="Expand this landscape",
            negative_prompt="cropped, cut off",
            init_image="test_image.png",
            outpaint_padding=128
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        # Verify outpainting-specific components
        node_classes = [node.get("class_type") for node in workflow.values()]
        self.assertIn("LoadImage", node_classes)
        self.assertIn("ImagePadForOutpaint", node_classes)
        self.assertIn("InpaintModelConditioning", node_classes)
        
        # Find InpaintModelConditioning node
        inpaint_node = None
        for node in workflow.values():
            if node.get("class_type") == "InpaintModelConditioning":
                inpaint_node = node
                break
        
        self.assertIsNotNone(inpaint_node, "InpaintModelConditioning node should be present")
        
        # Verify inputs (should not have mask for outpainting)
        inputs = inpaint_node["inputs"]
        self.assertIn("positive", inputs)
        self.assertIn("negative", inputs)
        self.assertIn("vae", inputs)
        self.assertIn("pixels", inputs)
        self.assertNotIn("mask", inputs)

    def test_combined_inpaint_outpaint_workflow(self):
        """
        Test combined inpainting and outpainting workflow.
        
        **Description:** Verifies that workflows with both inpainting and outpainting
        use the correct processing order and node connections.
        """
        params = GenerationParams(
            model_key="hidream",
            prompt="Restore and expand this artwork",
            negative_prompt="damaged, incomplete",
            init_image="test_image.png",
            inpaint_mask="test_mask.png",
            outpaint_padding=64
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        # Verify all components are present
        node_classes = [node.get("class_type") for node in workflow.values()]
        self.assertIn("LoadImage", node_classes)
        self.assertIn("LoadImageMask", node_classes)
        self.assertIn("ImagePadForOutpaint", node_classes)
        self.assertIn("InpaintModelConditioning", node_classes)
        
        # Find InpaintModelConditioning node
        inpaint_node = None
        for node in workflow.values():
            if node.get("class_type") == "InpaintModelConditioning":
                inpaint_node = node
                break
        
        self.assertIsNotNone(inpaint_node, "InpaintModelConditioning node should be present")
        
        # Verify inputs (should have mask when both are enabled)
        inputs = inpaint_node["inputs"]
        self.assertIn("positive", inputs)
        self.assertIn("negative", inputs)
        self.assertIn("vae", inputs)
        self.assertIn("pixels", inputs)
        self.assertIn("mask", inputs)

    def test_workflow_json_serialization(self):
        """
        Test that generated workflows can be properly serialized to JSON.
        
        **Description:** Verifies that the workflow output is JSON-serializable
        for use with ComfyUI API.
        """
        params = GenerationParams(
            model_key="sdxl",
            prompt="Serialization test"
        )
        
        workflow = self.builder.build_prompt_workflow(params)
        
        # Should not raise an exception
        json_str = json.dumps(workflow, indent=2)
        self.assertIsInstance(json_str, str)
        self.assertGreater(len(json_str), 0)
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        self.assertEqual(workflow, parsed)


class TestModelLoaderFactory(unittest.TestCase):
    """
    Unit tests for ModelLoaderFactory and related classes.
    
    **Description:** Tests the Factory pattern implementation for model loaders
    to ensure proper registration and creation of loaders.
    """

    def test_factory_registration(self):
        """
        Test that default loaders are registered correctly.
        
        **Description:** Verifies that the ModelLoaderFactory has registered
        the expected default loaders.
        """
        from services.comfy_workflow_builder import ModelLoaderFactory
        
        supported_types = ModelLoaderFactory.get_supported_types()
        self.assertIn("checkpoint", supported_types)
        self.assertIn("flux", supported_types)
        self.assertIn("hidream", supported_types)

    def test_factory_unsupported_type(self):
        """
        Test that factory raises error for unsupported model types.
        
        **Description:** Verifies that requesting an unsupported model type
        raises a ValueError.
        """
        from services.comfy_workflow_builder import ModelLoaderFactory
        
        with self.assertRaises(ValueError):
            ModelLoaderFactory.get_loader("unsupported_type")

    def test_custom_loader_registration(self):
        """
        Test custom loader registration and retrieval.
        
        **Description:** Verifies that custom loaders can be registered
        and retrieved from the factory.
        """
        from services.comfy_workflow_builder import ModelLoaderFactory, BaseModelLoader
        
        class TestLoader(BaseModelLoader):
            def create_loader_nodes(self, builder, model_path):
                return ["test", 0], ["test", 1], ["test", 2]
        
        # Register custom loader
        test_loader = TestLoader()
        ModelLoaderFactory.register_loader("test_type", test_loader)
        
        # Should be able to retrieve it
        retrieved = ModelLoaderFactory.get_loader("test_type")
        self.assertEqual(retrieved, test_loader)
        
        # Should be in supported types
        supported_types = ModelLoaderFactory.get_supported_types()
        self.assertIn("test_type", supported_types)

    def test_loader_node_creation(self):
        """
        Test that loaders create correct nodes through factory.
        
        **Description:** Verifies that model loaders create the expected
        node structures when called through the factory.
        """
        from services.comfy_workflow_builder import ComfyWorkflowBuilder, ModelLoaderFactory
        
        builder = ComfyWorkflowBuilder()
        
        # Test checkpoint loader
        checkpoint_loader = ModelLoaderFactory.get_loader("checkpoint")
        model_ref, clip_ref, vae_ref = checkpoint_loader.create_loader_nodes(builder, "test.safetensors")
        
        self.assertIsInstance(model_ref, list)
        self.assertIsInstance(clip_ref, list)
        self.assertIsInstance(vae_ref, list)
        
        # Should have created a CheckpointLoaderSimple node
        node_classes = [node.get("class_type") for node in builder.nodes.values()]
        self.assertIn("CheckpointLoaderSimple", node_classes)

    def test_model_loader_support_methods(self):
        """
        Test that model loaders correctly report their capabilities.
        
        **Description:** Verifies that each model loader correctly implements
        the support methods for various features.
        """
        from services.comfy_workflow_builder import ModelLoaderFactory
        
        # Test checkpoint loader capabilities
        checkpoint_loader = ModelLoaderFactory.get_loader("checkpoint")
        self.assertFalse(checkpoint_loader.supports_tea_cache())
        self.assertFalse(checkpoint_loader.supports_flux_guidance())
        self.assertFalse(checkpoint_loader.supports_model_sampling_flux())
        self.assertEqual(checkpoint_loader.get_sampler_type(), "basic")
        
        # Test flux loader capabilities
        flux_loader = ModelLoaderFactory.get_loader("flux")
        self.assertTrue(flux_loader.supports_tea_cache())
        self.assertTrue(flux_loader.supports_flux_guidance())
        self.assertTrue(flux_loader.supports_model_sampling_flux())
        self.assertEqual(flux_loader.get_sampler_type(), "custom")
        
        # Test hidream loader capabilities
        hidream_loader = ModelLoaderFactory.get_loader("hidream")
        self.assertTrue(hidream_loader.supports_tea_cache())
        self.assertFalse(hidream_loader.supports_flux_guidance())
        self.assertFalse(hidream_loader.supports_model_sampling_flux())
        self.assertEqual(hidream_loader.get_sampler_type(), "custom")

    def test_tea_cache_optimization_logic(self):
        """
        Test that TeaCache is only added for models that support it.
        
        **Description:** Verifies that TeaCache nodes are only created
        for models that return True for supports_tea_cache().
        """
        from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams
        
        # Test with checkpoint model (doesn't support TeaCache)
        params_checkpoint = GenerationParams(
            model_key="sdxl",
            prompt="Test TeaCache",
            enable_tea_cache=True
        )
        
        builder = ComfyWorkflowBuilder()
        workflow = builder.build_prompt_workflow(params_checkpoint)
        
        node_classes = [node.get("class_type") for node in workflow.values()]
        self.assertNotIn("TeaCache", node_classes)
        
        # Test with Flux model (supports TeaCache)
        params_flux = GenerationParams(
            model_key="flux-dev",
            prompt="Test TeaCache",
            enable_tea_cache=True
        )
        
        builder = ComfyWorkflowBuilder()
        workflow = builder.build_prompt_workflow(params_flux)
        
        node_classes = [node.get("class_type") for node in workflow.values()]
        self.assertIn("TeaCache", node_classes)

    def test_flux_guidance_logic(self):
        """
        Test that FluxGuidance is only added for models that support it.
        
        **Description:** Verifies that FluxGuidance nodes are only created
        for models that return True for supports_flux_guidance().
        """
        from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams
        
        # Test with checkpoint model (doesn't support FluxGuidance)
        params_checkpoint = GenerationParams(
            model_key="sdxl",
            prompt="Test FluxGuidance"
        )
        
        builder = ComfyWorkflowBuilder()
        workflow = builder.build_prompt_workflow(params_checkpoint)
        
        node_classes = [node.get("class_type") for node in workflow.values()]
        self.assertNotIn("FluxGuidance", node_classes)
        
        # Test with Flux model (supports FluxGuidance)
        params_flux = GenerationParams(
            model_key="flux-dev",
            prompt="Test FluxGuidance"
        )
        
        builder = ComfyWorkflowBuilder()
        workflow = builder.build_prompt_workflow(params_flux)
        
        node_classes = [node.get("class_type") for node in workflow.values()]
        self.assertIn("FluxGuidance", node_classes)

    def test_sampler_type_selection(self):
        """
        Test that correct sampler types are used based on model capabilities.
        
        **Description:** Verifies that different model types use appropriate
        sampler implementations based on their get_sampler_type() method.
        """
        # Test with Flux model (should use SamplerCustomAdvanced)
        params_flux = GenerationParams(
            model_key="flux-dev",
            prompt="Test custom sampler"
        )
        
        builder = ComfyWorkflowBuilder()
        workflow = builder.build_prompt_workflow(params_flux)
        
        custom_samplers = [node for node in workflow.values() if node["class_type"] == "SamplerCustomAdvanced"]
        basic_samplers = [node for node in workflow.values() if node["class_type"] == "KSampler"]
        
        self.assertEqual(len(custom_samplers), 1, "Flux should use SamplerCustomAdvanced")
        self.assertEqual(len(basic_samplers), 0, "Flux should not use KSampler")
        
        # Test with SDXL model (should use KSampler)
        params_sdxl = GenerationParams(
            model_key="sdxl",
            prompt="Test basic sampler"
        )
        
        builder = ComfyWorkflowBuilder()
        workflow = builder.build_prompt_workflow(params_sdxl)
        
        custom_samplers = [node for node in workflow.values() if node["class_type"] == "SamplerCustomAdvanced"]
        basic_samplers = [node for node in workflow.values() if node["class_type"] == "KSampler"]
        
        self.assertEqual(len(custom_samplers), 0, "SDXL should not use SamplerCustomAdvanced")
        self.assertEqual(len(basic_samplers), 1, "SDXL should use KSampler")

    def test_random_seed_generation(self):
        """
        Test that random seeds are generated when no seed is provided.
        
        **Description:** Verifies that the seed generator creates random seeds
        when params.seed is None.
        """
        from services.comfy_workflow_builder import ComfyWorkflowBuilder, GenerationParams
        
        params = GenerationParams(
            model_key="sdxl",
            prompt="Test random seed",
            seed=None  # Should generate random seed
        )
        
        builder1 = ComfyWorkflowBuilder()
        workflow1 = builder1.build_prompt_workflow(params)
        
        builder2 = ComfyWorkflowBuilder()
        workflow2 = builder2.build_prompt_workflow(params)
        
        # Find seed generator nodes
        seed1 = None
        seed2 = None
        
        for node in workflow1.values():
            if node.get("class_type") == "Seed Generator":
                seed1 = node["inputs"]["seed"]
                break
        
        for node in workflow2.values():
            if node.get("class_type") == "Seed Generator":
                seed2 = node["inputs"]["seed"]
                break
        
        self.assertIsNotNone(seed1)
        self.assertIsNotNone(seed2)
        self.assertIsInstance(seed1, int)
        self.assertIsInstance(seed2, int)
        # Seeds should be different (very high probability)
        self.assertNotEqual(seed1, seed2)


if __name__ == '__main__':
    unittest.main()
