"""
Tests for the ComfyWorkflowBuilder service

These tests validate that the ComfyUI workflow builder correctly generates
workflow JSON structures for various scenarios and configurations.
"""

import pytest
import json
from back.services.comfy_workflow_builder import (
    ComfyWorkflowBuilder, GenerationParams, LoRA, MODEL_REGISTRY
)


class TestComfyWorkflowBuilder:
    """
    Test cases for the ComfyWorkflowBuilder class.
    
    **Description:** Unit tests for ComfyUI workflow generation functionality.
    """

    @pytest.fixture
    def builder(self):
        """
        Create a fresh ComfyWorkflowBuilder instance for each test.
        
        **Description:** Provides a clean builder instance for testing.
        **Returns:** ComfyWorkflowBuilder instance
        """
        return ComfyWorkflowBuilder()

    @pytest.fixture
    def basic_params(self):
        """
        Create basic generation parameters for testing.
        
        **Description:** Provides standard parameters for workflow generation.
        **Returns:** GenerationParams instance
        """
        return GenerationParams(
            model_key="sdxl",
            prompt="A beautiful landscape with mountains and lakes",
            negative_prompt="blurry, low quality, distorted",
            sampler="euler",
            steps=25,
            cfg=7.5,
            width=1024,
            height=1024,
            seed=12345
        )

    @pytest.fixture
    def lora_list(self):
        """
        Create a list of LoRA models for testing.
        
        **Description:** Provides sample LoRA configurations.
        **Returns:** List of LoRA instances
        """
        return [
            LoRA(name="style_lora.safetensors", strength=0.8),
            LoRA(name="character_lora.safetensors", strength=0.6),
            LoRA(name="environment_lora.safetensors", strength=0.4)
        ]

    def test_initialization(self, builder):
        """
        Test ComfyWorkflowBuilder initialization.
        
        **Description:** Verifies that the builder initializes with correct default values.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        **Returns:** None (test assertion)
        """
        assert builder.nodes == {}
        assert builder.node_id == 1
        assert builder.options == {}

    def test_next_id_generation(self, builder):
        """
        Test node ID generation.
        
        **Description:** Verifies that node IDs are generated sequentially.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        **Returns:** None (test assertion)
        """
        first_id = builder._next_id()
        second_id = builder._next_id()
        third_id = builder._next_id()
        
        assert first_id == 2
        assert second_id == 3
        assert third_id == 4

    def test_with_loras_method(self, builder, lora_list):
        """
        Test adding LoRAs to the builder.
        
        **Description:** Verifies that LoRAs are correctly added to options.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        - lora_list (List[LoRA]): List of LoRA configurations
        **Returns:** None (test assertion)
        """
        result = builder.with_loras(lora_list)
        
        assert result is builder  # Method chaining
        assert 'loras' in builder.options
        assert builder.options['loras'] == lora_list

    def test_with_controlnet_method(self, builder):
        """
        Test adding ControlNet configuration to the builder.
        
        **Description:** Verifies that ControlNet options are correctly set.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        **Returns:** None (test assertion)
        """
        image_path = "/path/to/controlnet/image.jpg"
        preprocessor = "canny"
        model = "control_canny.safetensors"
        
        result = builder.with_controlnet(image_path, preprocessor, model)
        
        assert result is builder  # Method chaining
        assert 'controlnet' in builder.options
        assert builder.options['controlnet']['image'] == image_path
        assert builder.options['controlnet']['preprocessor'] == preprocessor
        assert builder.options['controlnet']['model'] == model

    def test_with_init_image_method(self, builder):
        """
        Test adding initialization image to the builder.
        
        **Description:** Verifies that init image path is correctly set.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        **Returns:** None (test assertion)
        """
        image_path = "/path/to/init/image.jpg"
        result = builder.with_init_image(image_path)
        
        assert result is builder  # Method chaining
        assert builder.options['init_image'] == image_path

    def test_enable_inpainting_method(self, builder):
        """
        Test enabling inpainting with mask.
        
        **Description:** Verifies that inpainting mask path is correctly set.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        **Returns:** None (test assertion)
        """
        mask_path = "/path/to/mask.jpg"
        result = builder.enable_inpainting(mask_path)
        
        assert result is builder  # Method chaining
        assert builder.options['inpaint'] == mask_path

    def test_enable_outpainting_method(self, builder):
        """
        Test enabling outpainting with padding.
        
        **Description:** Verifies that outpainting padding is correctly set.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        **Returns:** None (test assertion)
        """
        padding = 256
        result = builder.enable_outpainting(padding)
        
        assert result is builder  # Method chaining
        assert builder.options['outpaint'] == padding

    def test_enable_outpainting_default_padding(self, builder):
        """
        Test enabling outpainting with default padding.
        
        **Description:** Verifies that default padding is used when not specified.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        **Returns:** None (test assertion)
        """
        result = builder.enable_outpainting()
        
        assert result is builder  # Method chaining
        assert builder.options['outpaint'] == 128  # Default value

    def test_add_model_loader_checkpoint(self, builder):
        """
        Test adding checkpoint model loader.
        
        **Description:** Verifies that checkpoint model loader node is correctly created.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        **Returns:** None (test assertion)
        """
        model_path = "sd_xl_base_1.0.safetensors"
        model_ref, clip_ref, vae_ref = builder.add_model_loader("checkpoint", model_path)
        
        assert "model_loader" in builder.nodes
        assert builder.nodes["model_loader"]["class_type"] == "CheckpointLoaderSimple"
        assert builder.nodes["model_loader"]["inputs"]["ckpt_name"] == model_path
        assert model_ref == ["model_loader", 0]
        assert clip_ref == ["model_loader", 1]
        assert vae_ref == ["model_loader", 2]

    def test_add_model_loader_diffusers(self, builder):
        """
        Test adding diffusers model loader.
        
        **Description:** Verifies that diffusers model loader node is correctly created.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        **Returns:** None (test assertion)
        """
        model_path = "/models/diffusers/hivision-v1"
        model_ref, clip_ref, vae_ref = builder.add_model_loader("diffusers", model_path)
        
        assert "model_loader" in builder.nodes
        assert builder.nodes["model_loader"]["class_type"] == "DiffusersLoader"
        assert builder.nodes["model_loader"]["inputs"]["model_path"] == model_path
        assert builder.nodes["model_loader"]["inputs"]["dtype"] == "fp16"

    def test_add_model_loader_flux(self, builder):
        """
        Test adding flux model loader.
        
        **Description:** Verifies that flux model loader node is correctly created.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        **Returns:** None (test assertion)
        """
        model_path = "FluxDev_Fill_Preview.safetensors"
        model_ref, clip_ref, vae_ref = builder.add_model_loader("flux", model_path)
        
        assert "model_loader" in builder.nodes
        assert builder.nodes["model_loader"]["class_type"] == "FluxModelLoader"
        assert builder.nodes["model_loader"]["inputs"]["model_name"] == model_path

    def test_add_model_loader_unsupported(self, builder):
        """
        Test adding unsupported model type raises error.
        
        **Description:** Verifies that unsupported model types raise ValueError.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        **Returns:** None (test assertion)
        """
        with pytest.raises(ValueError, match="Unsupported model_type"):
            builder.add_model_loader("unsupported_type", "model.safetensors")

    def test_basic_workflow_generation(self, builder, basic_params):
        """
        Test basic workflow generation without optional features.
        
        **Description:** Verifies that a basic workflow is correctly generated.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        - basic_params (GenerationParams): Basic generation parameters
        **Returns:** None (test assertion)
        """
        workflow = builder.build_prompt_workflow(basic_params)
        
        assert "prompt" in workflow
        assert isinstance(workflow["prompt"], dict)
        
        # Check essential nodes
        nodes = workflow["prompt"]
        assert "model_loader" in nodes
        assert "positive" in nodes
        assert "negative" in nodes
        assert "sampler" in nodes
        assert "decode" in nodes
        assert "save_image" in nodes
        
        # Verify text encoding
        assert nodes["positive"]["class_type"] == "CLIPTextEncode"
        assert nodes["positive"]["inputs"]["text"] == basic_params.prompt
        assert nodes["negative"]["class_type"] == "CLIPTextEncode"
        assert nodes["negative"]["inputs"]["text"] == basic_params.negative_prompt
        
        # Verify sampling parameters
        assert nodes["sampler"]["class_type"] == "KSampler"
        assert nodes["sampler"]["inputs"]["steps"] == basic_params.steps
        assert nodes["sampler"]["inputs"]["cfg"] == basic_params.cfg
        assert nodes["sampler"]["inputs"]["sampler_name"] == basic_params.sampler
        assert nodes["sampler"]["inputs"]["seed"] == basic_params.seed

    def test_workflow_with_loras(self, builder, basic_params, lora_list):
        """
        Test workflow generation with LoRAs.
        
        **Description:** Verifies that LoRA nodes are correctly added to the workflow.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        - basic_params (GenerationParams): Basic generation parameters
        - lora_list (List[LoRA]): List of LoRA configurations
        **Returns:** None (test assertion)
        """
        # Update params with LoRAs
        basic_params.loras = lora_list
        workflow = builder.build_prompt_workflow(basic_params)
        
        nodes = workflow["prompt"]
        
        # Check that LoRA nodes were created
        for i, lora in enumerate(lora_list):
            lora_node_name = f"lora_{i}"
            assert lora_node_name in nodes
            assert nodes[lora_node_name]["class_type"] == "LoraLoader"

    def test_workflow_with_controlnet(self, builder, basic_params):
        """
        Test workflow generation with ControlNet.
        
        **Description:** Verifies that ControlNet nodes are correctly added to the workflow.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        - basic_params (GenerationParams): Basic generation parameters
        **Returns:** None (test assertion)
        """
        # Update params with ControlNet settings
        basic_params.controlnet_image = "/path/to/control.jpg"
        basic_params.controlnet_preprocessor = "canny"
        basic_params.controlnet_model = "control_canny.safetensors"
        
        workflow = builder.build_prompt_workflow(basic_params)
        
        nodes = workflow["prompt"]
        
        # Check ControlNet nodes
        assert "controlnet_pre" in nodes
        assert "controlnet" in nodes
        assert nodes["controlnet_pre"]["class_type"] == "Preprocessor"
        assert nodes["controlnet"]["class_type"] == "ControlNetApply"

    def test_workflow_with_init_image(self, builder, basic_params):
        """
        Test workflow generation with initialization image.
        
        **Description:** Verifies that init image nodes are correctly added to the workflow.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        - basic_params (GenerationParams): Basic generation parameters
        **Returns:** None (test assertion)
        """
        # Update params with init image
        basic_params.init_image = "/path/to/init.jpg"
        
        workflow = builder.build_prompt_workflow(basic_params)
        
        nodes = workflow["prompt"]
        
        # Check init image nodes
        assert "load_image" in nodes
        assert "encode_latent" in nodes
        assert nodes["load_image"]["class_type"] == "LoadImage"
        assert nodes["encode_latent"]["class_type"] == "VAEEncode"

    def test_workflow_with_inpainting(self, builder, basic_params):
        """
        Test workflow generation with inpainting.
        
        **Description:** Verifies that inpainting nodes are correctly added to the workflow.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        - basic_params (GenerationParams): Basic generation parameters
        **Returns:** None (test assertion)
        """
        # Update params with init image and inpaint mask
        basic_params.init_image = "/path/to/init.jpg"
        basic_params.inpaint_mask = "/path/to/mask.jpg"
        
        workflow = builder.build_prompt_workflow(basic_params)
        
        nodes = workflow["prompt"]
        
        # Check inpainting nodes
        assert "load_mask" in nodes
        assert "encode_mask" in nodes
        assert nodes["load_mask"]["class_type"] == "LoadImage"
        assert nodes["encode_mask"]["class_type"] == "VAEEncode"

    def test_workflow_with_outpainting(self, builder, basic_params):
        """
        Test workflow generation with outpainting.
        
        **Description:** Verifies that outpainting nodes are correctly added to the workflow.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        - basic_params (GenerationParams): Basic generation parameters
        **Returns:** None (test assertion)
        """
        # Update params with init image and outpaint padding
        basic_params.init_image = "/path/to/init.jpg"
        basic_params.outpaint_padding = 256
        
        workflow = builder.build_prompt_workflow(basic_params)
        
        nodes = workflow["prompt"]
        
        # Check outpainting nodes
        assert "padded" in nodes
        assert nodes["padded"]["class_type"] == "PadImage"
        assert nodes["padded"]["inputs"]["left"] == 256
        assert nodes["padded"]["inputs"]["right"] == 256
        assert nodes["padded"]["inputs"]["top"] == 256
        assert nodes["padded"]["inputs"]["bottom"] == 256

    def test_unknown_model_key(self, builder):
        """
        Test workflow generation with unknown model key.
        
        **Description:** Verifies that unknown model keys raise ValueError.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        **Returns:** None (test assertion)
        """
        invalid_params = GenerationParams(
            model_key="unknown_model",
            prompt="Test prompt"
        )
        
        with pytest.raises(ValueError, match="Unknown model key"):
            builder.build_prompt_workflow(invalid_params)

    def test_complex_workflow_generation(self, builder, lora_list):
        """
        Test workflow generation with multiple features combined.
        
        **Description:** Verifies that complex workflows with multiple features work correctly.
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The builder instance to test
        - lora_list (List[LoRA]): List of LoRA configurations
        **Returns:** None (test assertion)
        """
        # Create comprehensive parameters with all features
        params = GenerationParams(
            model_key="flux-dev",
            prompt="A complex scene with multiple elements",
            negative_prompt="bad quality, artifacts",
            sampler="dpmpp_2m",
            steps=30,
            cfg=8.0,
            width=1536,
            height=1024,
            seed=98765,
            loras=lora_list,
            controlnet_image="/path/to/control.jpg",
            controlnet_preprocessor="canny",
            controlnet_model="control_canny.safetensors",
            init_image="/path/to/init.jpg",
            inpaint_mask="/path/to/mask.jpg"
        )
        
        workflow = builder.build_prompt_workflow(params)
        nodes = workflow["prompt"]
        
        # Verify all components are present
        assert "model_loader" in nodes
        assert "lora_0" in nodes and "lora_1" in nodes and "lora_2" in nodes
        assert "controlnet_pre" in nodes and "controlnet" in nodes
        assert "load_image" in nodes and "encode_latent" in nodes
        assert "load_mask" in nodes and "encode_mask" in nodes
        assert "positive" in nodes and "negative" in nodes
        assert "sampler" in nodes
        assert "decode" in nodes and "save_image" in nodes


class TestModelRegistry:
    """
    Test cases for the MODEL_REGISTRY constant.
    
    **Description:** Unit tests for model registry validation.
    """

    def test_model_registry_structure(self):
        """
        Test that MODEL_REGISTRY has the expected structure.
        
        **Description:** Verifies that the model registry contains expected models and metadata.
        **Returns:** None (test assertion)
        """
        assert isinstance(MODEL_REGISTRY, dict)
        assert len(MODEL_REGISTRY) > 0
        
        # Check required models
        required_models = ["sdxl", "flux-dev", "hivision"]
        for model_key in required_models:
            assert model_key in MODEL_REGISTRY
            
            model_info = MODEL_REGISTRY[model_key]
            assert "model_type" in model_info
            assert "filename" in model_info
            assert isinstance(model_info["model_type"], str)
            assert isinstance(model_info["filename"], str)

    def test_model_types_validity(self):
        """
        Test that all model types in the registry are valid.
        
        **Description:** Verifies that model types are supported by the workflow builder.
        **Returns:** None (test assertion)
        """
        valid_types = {"checkpoint", "diffusers", "flux"}
        
        for model_key, model_info in MODEL_REGISTRY.items():
            assert model_info["model_type"] in valid_types, f"Invalid model type for {model_key}: {model_info['model_type']}"


class TestLoRAModel:
    """
    Test cases for the LoRA model class.
    
    **Description:** Unit tests for LoRA model validation.
    """

    def test_lora_creation(self):
        """
        Test LoRA model creation and validation.
        
        **Description:** Verifies that LoRA models are created correctly.
        **Returns:** None (test assertion)
        """
        lora = LoRA(name="test_lora.safetensors", strength=0.75)
        
        assert lora.name == "test_lora.safetensors"
        assert lora.strength == 0.75

    def test_lora_validation(self):
        """
        Test LoRA model validation constraints.
        
        **Description:** Verifies that LoRA validation works correctly.
        **Returns:** None (test assertion)
        """
        # Valid LoRA
        valid_lora = LoRA(name="valid.safetensors", strength=0.5)
        assert valid_lora.strength == 0.5
        
        # Test edge cases
        edge_lora_low = LoRA(name="edge.safetensors", strength=0.0)
        assert edge_lora_low.strength == 0.0
        
        edge_lora_high = LoRA(name="edge.safetensors", strength=1.0)
        assert edge_lora_high.strength == 1.0


class TestGenerationParams:
    """
    Test cases for the GenerationParams model class.
    
    **Description:** Unit tests for generation parameters validation.
    """

    def test_generation_params_creation(self):
        """
        Test GenerationParams creation with all fields.
        
        **Description:** Verifies that generation parameters are created correctly.
        **Returns:** None (test assertion)
        """
        loras = [LoRA(name="test.safetensors", strength=0.8)]
        
        params = GenerationParams(
            model_key="sdxl",
            prompt="A beautiful sunset",
            negative_prompt="blurry",
            sampler="euler_a",
            steps=25,
            cfg=7.0,
            width=1024,
            height=768,
            seed=42,
            loras=loras,
            controlnet_image="/path/to/control.jpg",
            controlnet_preprocessor="canny",
            controlnet_model="control_canny.safetensors",
            init_image="/path/to/init.jpg",
            inpaint_mask="/path/to/mask.jpg",
            outpaint_padding=128,
            wait=True
        )
        
        assert params.model_key == "sdxl"
        assert params.prompt == "A beautiful sunset"
        assert params.negative_prompt == "blurry"
        assert params.sampler == "euler_a"
        assert params.steps == 25
        assert params.cfg == 7.0
        assert params.width == 1024
        assert params.height == 768
        assert params.seed == 42
        assert len(params.loras) == 1
        assert params.controlnet_image == "/path/to/control.jpg"
        assert params.controlnet_preprocessor == "canny"
        assert params.controlnet_model == "control_canny.safetensors"
        assert params.init_image == "/path/to/init.jpg"
        assert params.inpaint_mask == "/path/to/mask.jpg"
        assert params.outpaint_padding == 128
        assert params.wait == True

    def test_generation_params_defaults(self):
        """
        Test GenerationParams creation with default values.
        
        **Description:** Verifies that default values are correctly applied.
        **Returns:** None (test assertion)
        """
        params = GenerationParams(
            model_key="flux-dev",
            prompt="Test prompt"
        )
        
        assert params.negative_prompt == ""
        assert params.sampler == "euler"
        assert params.steps == 30
        assert params.cfg == 7.5
        assert params.width == 1024
        assert params.height == 1024
        assert params.loras == []
        assert params.seed is None
        assert params.controlnet_image is None
        assert params.controlnet_preprocessor is None
        assert params.controlnet_model is None
        assert params.init_image is None
        assert params.inpaint_mask is None
        assert params.outpaint_padding is None
        assert params.wait == False

    def test_create_generation_params_factory(self):
        """
        Test the factory method for creating GenerationParams.
        
        **Description:** Verifies that the factory method creates proper GenerationParams with defaults.
        **Returns:** None (test assertion)
        """
        # Test with minimal parameters
        params = ComfyWorkflowBuilder.create_generation_params(
            model_key="sdxl",
            prompt="A test image"
        )
        
        assert params.model_key == "sdxl"
        assert params.prompt == "A test image"
        assert params.negative_prompt == "blurry, low quality, bad anatomy, worst quality"
        assert params.sampler == "euler"
        assert params.steps == 30
        assert params.wait == False
        
        # Test with overrides
        params_with_overrides = ComfyWorkflowBuilder.create_generation_params(
            model_key="flux-dev",
            prompt="Another test",
            steps=50,
            cfg=8.0,
            wait=True,
            loras=[LoRA(name="test.safetensors", strength=0.8)]
        )
        
        assert params_with_overrides.model_key == "flux-dev"
        assert params_with_overrides.prompt == "Another test"
        assert params_with_overrides.steps == 50
        assert params_with_overrides.cfg == 8.0
        assert params_with_overrides.wait == True
        assert len(params_with_overrides.loras) == 1
