from typing import List, Dict, Optional, Tuple, Protocol
from pydantic import BaseModel
from abc import ABC, abstractmethod


class BaseModelLoader(ABC):
    """
    Abstract base class for model loaders in ComfyUI workflow builder.
    
    **Description:** Defines the interface for creating model loader nodes
    specific to different model types (Flux, SDXL, HiDream, etc.).
    """
    
    @abstractmethod
    def create_loader_nodes(self, builder: 'ComfyWorkflowBuilder', model_path: str) -> Tuple[List, List, List]:
        """
        Create the appropriate loader nodes for this model type.
        
        **Parameters:**
        - builder (ComfyWorkflowBuilder): The workflow builder instance
        - model_path (str): Path to the model file
        
        **Returns:** Tuple of (model_ref, clip_ref, vae_ref)
        """
        pass
    
    def supports_tea_cache(self) -> bool:
        """
        Check if this model type supports TeaCache optimization.
        
        **Description:** Returns whether TeaCache can be used with this model type.
        **Returns:** True if TeaCache is supported, False otherwise
        """
        return False
    
    def supports_flux_guidance(self) -> bool:
        """
        Check if this model type supports FluxGuidance.
        
        **Description:** Returns whether FluxGuidance should be used with this model type.
        **Returns:** True if FluxGuidance is supported, False otherwise
        """
        return False
    
    def supports_model_sampling_flux(self) -> bool:
        """
        Check if this model type supports ModelSamplingFlux.
        
        **Description:** Returns whether ModelSamplingFlux nodes need dimension updates.
        **Returns:** True if ModelSamplingFlux is supported, False otherwise
        """
        return False
    
    def get_sampler_type(self) -> str:
        """
        Get the appropriate sampler type for this model.
        
        **Description:** Returns the sampler type that should be used for this model.
        **Returns:** "custom" for advanced samplers, "basic" for standard KSampler
        """
        return "basic"
    
    def create_sampler_nodes(self, builder: 'ComfyWorkflowBuilder', params: 'GenerationParams', 
                           model_ref: List, positive_ref: List, negative_ref: List,
                           latent_ref: List, seed_ref: List) -> List:
        """
        Create the appropriate sampler nodes for this model type.
        
        **Description:** Creates sampler and scheduler nodes specific to this model type.
        **Parameters:**
        - builder: The workflow builder instance
        - params: Generation parameters
        - model_ref: Model reference from loader
        - positive_ref: Positive conditioning reference
        - negative_ref: Negative conditioning reference
        - latent_ref: Latent image reference
        - seed_ref: Seed reference
        
        **Returns:** Reference to the sampled latent output
        """
        # Default implementation uses basic KSampler
        sampler_id = builder._next_id()
        sampler_inputs = {
            "seed": seed_ref,
            "steps": params.steps,
            "cfg": params.cfg,
            "sampler_name": params.sampler,
            "scheduler": "normal",
            "denoise": 1.0,
            "model": model_ref,
            "positive": positive_ref,
            "negative": negative_ref,
            "latent_image": latent_ref
        }
        
        if "mask_ref" in builder.options:
            sampler_inputs["mask"] = builder.options["mask_ref"]
            
        builder.nodes[sampler_id] = {
            "class_type": "KSampler",
            "inputs": sampler_inputs,
            "_meta": {"title": "KSampler"}
        }
        return [sampler_id, 0]


class CheckpointModelLoader(BaseModelLoader):
    """
    Model loader for checkpoint models (SDXL, SD1.5).
    
    **Description:** Creates a single CheckpointLoaderSimple node.
    """
    
    def create_loader_nodes(self, builder: 'ComfyWorkflowBuilder', model_path: str) -> Tuple[List, List, List]:
        """Create CheckpointLoaderSimple node for checkpoint models."""
        node_id = builder._next_id()
        builder.nodes[node_id] = {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": model_path},
            "_meta": {"title": "Load Checkpoint"}
        }
        return [node_id, 0], [node_id, 1], [node_id, 2]


class FluxModelLoader(BaseModelLoader):
    """
    Model loader for Flux models.
    
    **Description:** Creates separate UNet, DualCLIP, VAE, and ModelSamplingFlux nodes.
    """
    
    def create_loader_nodes(self, builder: 'ComfyWorkflowBuilder', model_path: str) -> Tuple[List, List, List]:
        """Create separate loader nodes for Flux models."""
        unet_id = builder._next_id()
        clip_id = builder._next_id()
        vae_id = builder._next_id()
        model_sampling_id = builder._next_id()
        
        # UNet Loader
        builder.nodes[unet_id] = {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": f"Flux/{model_path}",
                "weight_dtype": "fp8_e4m3fn"
            },
            "_meta": {"title": "Load Diffusion Model"}
        }
        
        # DualCLIPLoader for Flux
        builder.nodes[clip_id] = {
            "class_type": "DualCLIPLoader", 
            "inputs": {
                "clip_name1": "Flux/clip_l.safetensors",
                "clip_name2": "Flux/t5xxl_fp8_e4m3fn.safetensors",
                "type": "flux",
                "device": "default"
            },
            "_meta": {"title": "DualCLIPLoader"}
        }
        
        # VAE Loader
        builder.nodes[vae_id] = {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "Flux/ae.safetensors"},
            "_meta": {"title": "Load VAE"}
        }
        
        # ModelSamplingFlux for Flux
        builder.nodes[model_sampling_id] = {
            "class_type": "ModelSamplingFlux",
            "inputs": {
                "max_shift": 1.15,
                "base_shift": 0.5,
                "width": 1024,  # Will be updated later with actual dimensions
                "height": 1024,
                "model": [unet_id, 0]
            },
            "_meta": {"title": "ModelSamplingFlux"}
        }
        
        return [model_sampling_id, 0], [clip_id, 0], [vae_id, 0]
    
    def supports_tea_cache(self) -> bool:
        """Flux models support TeaCache optimization."""
        return True
    
    def supports_flux_guidance(self) -> bool:
        """Flux models support FluxGuidance."""
        return True
    
    def supports_model_sampling_flux(self) -> bool:
        """Flux models support ModelSamplingFlux."""
        return True
    
    def get_sampler_type(self) -> str:
        """Flux models use custom samplers."""
        return "custom"
    
    def create_sampler_nodes(self, builder: 'ComfyWorkflowBuilder', params: 'GenerationParams', 
                           model_ref: List, positive_ref: List, negative_ref: List,
                           latent_ref: List, seed_ref: List) -> List:
        """Create FluxGuidance and SamplerCustomAdvanced nodes for Flux models."""
        # FluxGuidance node
        flux_guidance_id = builder._next_id()
        builder.nodes[flux_guidance_id] = {
            "class_type": "FluxGuidance",
            "inputs": {
                "guidance": params.cfg,
                "conditioning": positive_ref
            },
            "_meta": {"title": "FluxGuidance"}
        }
        
        # BasicScheduler
        scheduler_id = builder._next_id()
        builder.nodes[scheduler_id] = {
            "class_type": "BasicScheduler",
            "inputs": {
                "scheduler": "simple",
                "steps": params.steps,
                "denoise": 1.0,
                "model": model_ref
            },
            "_meta": {"title": "BasicScheduler"}
        }
        
        # KSamplerSelect
        sampler_select_id = builder._next_id()
        builder.nodes[sampler_select_id] = {
            "class_type": "KSamplerSelect",
            "inputs": {"sampler_name": "dpmpp_2m_sde"},
            "_meta": {"title": "KSamplerSelect"}
        }
        
        # Detail Daemon Sampler (conditional on add_details)
        sampler_ref = [sampler_select_id, 0]
        if params.add_details:
            sampler_ref = builder._create_detail_daemon_sampler_node(sampler_ref)
        
        # SamplerCustomAdvanced
        sampler_id = builder._next_id()
        sampler_inputs = {
            "noise": seed_ref,
            "guider": [flux_guidance_id, 0],
            "sampler": sampler_ref,
            "sigmas": [scheduler_id, 0],
            "latent_image": latent_ref
        }
        
        if "mask_ref" in builder.options:
            sampler_inputs["mask"] = builder.options["mask_ref"]
            
        builder.nodes[sampler_id] = {
            "class_type": "SamplerCustomAdvanced",
            "inputs": sampler_inputs,
            "_meta": {"title": "SamplerCustomAdvanced"}
        }
        return [sampler_id, 0]


class HiDreamModelLoader(BaseModelLoader):
    """
    Model loader for HiDream models.
    
    **Description:** Creates separate UNet, QuadrupleCLIP, VAE, and ModelSamplingSD3 nodes.
    """
    
    def create_loader_nodes(self, builder: 'ComfyWorkflowBuilder', model_path: str) -> Tuple[List, List, List]:
        """Create separate loader nodes for HiDream models."""
        unet_id = builder._next_id()
        clip_id = builder._next_id()
        vae_id = builder._next_id()
        model_sampling_id = builder._next_id()
        
        # UNet Loader
        builder.nodes[unet_id] = {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": f"HiDream/{model_path}",
                "weight_dtype": "fp8_e4m3fn"
            },
            "_meta": {"title": "Load Diffusion Model"}
        }
        
        # QuadrupleCLIPLoader for HiDream
        builder.nodes[clip_id] = {
            "class_type": "QuadrupleCLIPLoader",
            "inputs": {
                "clip_name1": "HiDream/clip_l_hidream.safetensors",
                "clip_name2": "HiDream/clip_g_hidream.safetensors",
                "clip_name3": "HiDream/t5xxl_fp8_e4m3fn_scaled.safetensors",
                "clip_name4": "HiDream/llama_3.1_8b_instruct_fp8_scaled.safetensors"
            },
            "_meta": {"title": "QuadrupleCLIPLoader"}
        }
        
        # VAE Loader
        builder.nodes[vae_id] = {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "HiDream/ae.safetensors"},
            "_meta": {"title": "Load VAE"}
        }
        
        # ModelSamplingSD3 for HiDream (uses SD3 sampling)
        builder.nodes[model_sampling_id] = {
            "class_type": "ModelSamplingSD3",
            "inputs": {
                "shift": 3.0,
                "model": [unet_id, 0]
            },
            "_meta": {"title": "ModelSamplingSD3"}
        }
        
        return [model_sampling_id, 0], [clip_id, 0], [vae_id, 0]
    
    def supports_tea_cache(self) -> bool:
        """HiDream models support TeaCache optimization."""
        return True
    
    def supports_flux_guidance(self) -> bool:
        """HiDream models do not support FluxGuidance."""
        return False
    
    def supports_model_sampling_flux(self) -> bool:
        """HiDream models do not support ModelSamplingFlux."""
        return False
    
    def get_sampler_type(self) -> str:
        """HiDream models use custom samplers."""
        return "custom"
    
    def create_sampler_nodes(self, builder: 'ComfyWorkflowBuilder', params: 'GenerationParams', 
                           model_ref: List, positive_ref: List, negative_ref: List,
                           latent_ref: List, seed_ref: List) -> List:
        """Create SamplerCustomAdvanced nodes for HiDream models."""
        # CFGGuider
        cfg_guider_id = builder._next_id()
        builder.nodes[cfg_guider_id] = {
            "class_type": "CFGGuider",
            "inputs": {
                "model": model_ref,
                "positive": positive_ref,
                "negative": negative_ref,
                "cfg": params.cfg
            },
            "_meta": {"title": "CFGGuider"}
        }
        
        # BasicScheduler
        scheduler_id = builder._next_id()
        builder.nodes[scheduler_id] = {
            "class_type": "BasicScheduler",
            "inputs": {
                "scheduler": "simple",
                "steps": params.steps,
                "denoise": 1.0,
                "model": model_ref
            },
            "_meta": {"title": "BasicScheduler"}
        }
        
        # KSamplerSelect
        sampler_select_id = builder._next_id()
        builder.nodes[sampler_select_id] = {
            "class_type": "KSamplerSelect",
            "inputs": {"sampler_name": "dpmpp_2m_sde"},
            "_meta": {"title": "KSamplerSelect"}
        }
        
        # Detail Daemon Sampler (conditional on add_details)
        sampler_ref = [sampler_select_id, 0]
        if params.add_details:
            sampler_ref = builder._create_detail_daemon_sampler_node(sampler_ref)
        
        # SamplerCustomAdvanced
        sampler_id = builder._next_id()
        sampler_inputs = {
            "noise": seed_ref,
            "guider": [cfg_guider_id, 0],
            "sampler": sampler_ref,
            "sigmas": [scheduler_id, 0],
            "latent_image": latent_ref
        }
        
        if "mask_ref" in builder.options:
            sampler_inputs["mask"] = builder.options["mask_ref"]
            
        builder.nodes[sampler_id] = {
            "class_type": "SamplerCustomAdvanced",
            "inputs": sampler_inputs,
            "_meta": {"title": "SamplerCustomAdvanced"}
        }
        return [sampler_id, 0]


class ModelLoaderFactory:
    """
    Factory class for creating model loader instances.
    
    **Description:** Manages registration and creation of model loaders
    for different model types. Supports runtime registration of new loaders.
    """
    
    _loaders: Dict[str, BaseModelLoader] = {}
    
    @classmethod
    def register_loader(cls, model_type: str, loader: BaseModelLoader):
        """
        Register a new model loader for a specific model type.
        
        **Parameters:**
        - model_type (str): The type of model (e.g., "flux", "checkpoint")
        - loader (BaseModelLoader): The loader instance to register
        """
        cls._loaders[model_type] = loader
    
    @classmethod
    def get_loader(cls, model_type: str) -> BaseModelLoader:
        """
        Get the registered loader for a specific model type.
        
        **Parameters:**
        - model_type (str): The type of model to get loader for
        
        **Returns:** The registered loader instance
        
        **Raises:** ValueError if model_type is not registered
        """
        if model_type not in cls._loaders:
            raise ValueError(f"No loader registered for model_type: {model_type}")
        return cls._loaders[model_type]
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of all supported model types."""
        return list(cls._loaders.keys())


# Register the default loaders
ModelLoaderFactory.register_loader("checkpoint", CheckpointModelLoader())
ModelLoaderFactory.register_loader("flux", FluxModelLoader())
ModelLoaderFactory.register_loader("hidream", HiDreamModelLoader())


class LoRA(BaseModel):
    name: str
    strength: float


class GenerationParams(BaseModel):
    # Basic generation parameters
    model_key: str
    prompt: str
    negative_prompt: str = ""
    sampler: str = "euler"
    steps: int = 30
    cfg: float = 7.5
    width: int = 1024
    height: int = 1024
    seed: Optional[int] = None
    
    # LoRA parameters
    loras: List[LoRA] = []
    
    # ControlNet parameters
    controlnet_image: Optional[str] = None
    controlnet_preprocessor: Optional[str] = None
    controlnet_model: Optional[str] = None
    
    # Image-to-image parameters
    init_image: Optional[str] = None
    
    # Inpainting parameters
    inpaint_mask: Optional[str] = None
    
    # Outpainting parameters
    outpaint_padding: Optional[int] = None
    
    # Optimization parameters
    enable_tea_cache: bool = True
    enable_clear_cache: bool = True
    
    # Detail enhancement parameters
    add_details: bool = False
    
    # Execution control
    wait: bool = False


MODEL_REGISTRY = {
    "sdxl": {
        "model_type": "checkpoint",
        "filename": "sd_xl_base_1.0.safetensors"
    },
    "sd15": {
        "model_type": "checkpoint", 
        "filename": "v1-5-pruned-emaonly.safetensors"
    },
    "flux-dev": {
        "model_type": "flux",
        "filename": "flux1-dev-fp8.safetensors"
    },
    "flux-schnell": {
        "model_type": "flux",
        "filename": "flux1-schnell-fp8.safetensors"
    },
    "hidream": {
        "model_type": "hidream",
        "filename": "hidream_i1_fast_fp8.safetensors"
    }
}

class ComfyWorkflowBuilder:
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.node_id = 1
        self.options: Dict = {}

    def _next_id(self):
        current_id = self.node_id
        self.node_id += 1
        return str(current_id)

    def with_loras(self, loras: List[LoRA]):
        self.options['loras'] = loras
        return self

    def with_controlnet(self, image_path: str, preprocessor: str, model: str):
        self.options['controlnet'] = {
            "image": image_path,
            "preprocessor": preprocessor,
            "model": model,
        }
        return self

    def with_init_image(self, image_path: str):
        self.options['init_image'] = image_path
        return self

    def enable_inpainting(self, mask_path: str):
        self.options['inpaint'] = mask_path
        return self

    def enable_outpainting(self, padding: int = 128):
        self.options['outpaint'] = padding
        return self

    def _create_tea_cache_node(self, model_type: str, model_ref: List) -> List:
        """
        Create TeaCache optimization node.
        
        **Description:** Creates a TeaCache node for model optimization.
        **Parameters:**
        - model_type (str): Type of model for cache configuration
        - model_ref (List): Reference to the model to cache
        **Returns:** Reference to the cached model output
        """
        cache_id = self._next_id()
        self.nodes[cache_id] = {
            "class_type": "TeaCache",
            "inputs": {
                "model_type": model_type,
                "rel_l1_thresh": 0.4,
                "start_percent": 0,
                "end_percent": 1,
                "cache_device": "cuda",
                "model": model_ref
            },
            "_meta": {"title": "TeaCache"}
        }
        return [cache_id, 0]
    
    def _create_seed_generator_node(self, seed: Optional[int] = None) -> List:
        """
        Create seed generator node.
        
        **Description:** Creates a Seed Generator node with random seed if none provided.
        **Parameters:**
        - seed (Optional[int]): Specific seed to use, random if None
        **Returns:** Reference to the seed output
        """
        import random
        seed_id = self._next_id()
        actual_seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.nodes[seed_id] = {
            "class_type": "Seed Generator",
            "inputs": {"seed": actual_seed},
            "_meta": {"title": "Seed Generator"}
        }
        return [seed_id, 0]
    
    def _create_text_encode_nodes(self, prompt: str, negative_prompt: str, clip_ref: List) -> Tuple[List, List]:
        """
        Create CLIP text encoding nodes for positive and negative prompts.
        
        **Description:** Creates CLIPTextEncode nodes for both positive and negative conditioning.
        **Parameters:**
        - prompt (str): Positive prompt text
        - negative_prompt (str): Negative prompt text
        - clip_ref (List): Reference to the CLIP model
        **Returns:** Tuple of (positive_ref, negative_ref)
        """
        positive_id = self._next_id()
        negative_id = self._next_id()
        
        self.nodes[positive_id] = {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": clip_ref
            },
            "_meta": {"title": "CLIP Text Encode (Positive)"}
        }
        
        self.nodes[negative_id] = {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative_prompt,
                "clip": clip_ref
            },
            "_meta": {"title": "CLIP Text Encode (Negative)"}
        }
        
        return [positive_id, 0], [negative_id, 0]
    
    def _create_aspect_ratio_node(self, width: int, height: int) -> List:
        """
        Create CR SDXL Aspect Ratio node for empty latent generation.
        
        **Description:** Creates a CR SDXL Aspect Ratio node with custom dimensions.
        **Parameters:**
        - width (int): Target width
        - height (int): Target height
        **Returns:** Reference to the latent output
        """
        aspect_id = self._next_id()
        self.nodes[aspect_id] = {
            "class_type": "CR SDXL Aspect Ratio",
            "inputs": {
                "width": width,
                "height": height,
                "aspect_ratio": "custom",
                "swap_dimensions": "Off",
                "upscale_factor": 1,
                "batch_size": 1
            },
            "_meta": {"title": "🔳 CR SDXL Aspect Ratio"}
        }
        return [aspect_id, 4]  # Output 4 is the latent
    
    def _create_vae_decode_node(self, samples_ref: List, vae_ref: List) -> List:
        """
        Create VAE decode node to convert latents to images.
        
        **Description:** Creates a VAEDecode node to convert latent samples to images.
        **Parameters:**
        - samples_ref (List): Reference to the latent samples
        - vae_ref (List): Reference to the VAE model
        **Returns:** Reference to the decoded images
        """
        decode_id = self._next_id()
        self.nodes[decode_id] = {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": samples_ref,
                "vae": vae_ref
            },
            "_meta": {"title": "VAE Decode"}
        }
        return [decode_id, 0]
    
    def _create_save_image_node(self, images_ref: List, filename_prefix: str = "generated_") -> List:
        """
        Create SaveImage node to save generated images.
        
        **Description:** Creates a SaveImage node with specified filename prefix.
        **Parameters:**
        - images_ref (List): Reference to the images to save
        - filename_prefix (str): Prefix for saved filenames
        **Returns:** Reference to the save node output
        """
        save_id = self._next_id()
        self.nodes[save_id] = {
            "class_type": "SaveImage",
            "inputs": {
                "images": images_ref,
                "filename_prefix": filename_prefix
            },
            "_meta": {"title": "Save Image"}
        }
        return [save_id, 0]
    
    def _create_detail_daemon_sampler_node(self, sampler_ref: List, detail_amount: float = 0.3) -> List:
        """
        Create DetailDaemonSampler node for enhanced quality.
        
        **Description:** Creates a DetailDaemonSamplerNode for improved detail rendering.
        **Parameters:**
        - sampler_ref (List): Reference to the base sampler
        - detail_amount (float): Amount of detail enhancement (0.0-1.0)
        **Returns:** Reference to the enhanced sampler output
        """
        detail_daemon_id = self._next_id()
        self.nodes[detail_daemon_id] = {
            "class_type": "DetailDaemonSamplerNode",
            "inputs": {
                "detail_amount": detail_amount,
                "start": 0.2,
                "end": 0.8,
                "bias": 0.5,
                "exponent": 1,
                "start_offset": 0,
                "end_offset": 0,
                "fade": 0,
                "smooth": True,
                "cfg_scale_override": 0,
                "sampler": sampler_ref
            },
            "_meta": {"title": "Detail Daemon Sampler"}
        }
        return [detail_daemon_id, 0]

    def _create_clear_cache_node(self, trigger_ref: List) -> List:
        """
        Create cache clearing node for optimization.
        
        **Description:** Creates an easy clearCacheAll node for memory optimization.
        **Parameters:**
        - trigger_ref (List): Reference to trigger the cache clear
        **Returns:** Reference to the clear cache output
        """
        clear_id = self._next_id()
        self.nodes[clear_id] = {
            "class_type": "easy clearCacheAll",
            "inputs": {"anything": trigger_ref},
            "_meta": {"title": "Clear Cache All"}
        }
        return [clear_id, 0]

    def add_model_loader(self, model_type: str, model_path: str):
        """
        Add appropriate model loader based on model type using Factory pattern.
        
        **Description:** Creates the correct loader nodes based on the model type
        using the registered model loaders in the factory.
        
        **Parameters:**
        - model_type (str): Type of model (checkpoint, flux, hidream, etc.)
        - model_path (str): Path to the model file
        
        **Returns:** Tuple of (model_ref, clip_ref, vae_ref)
        
        **Raises:** ValueError if model_type is not supported
        """
        loader = ModelLoaderFactory.get_loader(model_type)
        return loader.create_loader_nodes(self, model_path)

    def _add_loras(self):
        loras = self.options.get("loras", [])
        base_model = self.options["model_ref"]
        base_clip = self.options["clip_ref"]
        
        if loras:
            # Use Power Lora Loader for Flux models
            lora_id = self._next_id()
            lora_inputs = {
                "PowerLoraLoaderHeaderWidget": {
                    "type": "PowerLoraLoaderHeaderWidget"
                },
                "➕ Add Lora": "",
                "model": base_model,
                "clip": base_clip
            }
            
            # Add each LoRA to the inputs
            for i, lora in enumerate(loras[:5], 1):  # Max 5 LoRAs
                lora_inputs[f"lora_{i}"] = {
                    "lora": lora.name,
                    "on": True,
                    "strength": lora.strength
                }
            
            # Fill remaining slots with empty LoRAs
            for i in range(len(loras) + 1, 6):
                lora_inputs[f"lora_{i}"] = {
                    "on": False,
                    "lora": "",
                    "strength": 1
                }
            
            self.nodes[lora_id] = {
                "class_type": "Power Lora Loader (rgthree)",
                "inputs": lora_inputs,
                "_meta": {"title": "Lora Loader"}
            }
            
            self.options["model_ref"] = [lora_id, 0]
            self.options["clip_ref"] = [lora_id, 1]

    def _add_controlnet(self):
        """
        Add ControlNet processing to the workflow.
        
        **Description:** Adds ControlNet image loading, preprocessing, and application nodes.
        **TODO:** Make the preprocessor configurable instead of hardcoded to Canny.
        """
        cfg = self.options["controlnet"]
        pre_id = self._next_id()
        
        # Load ControlNet image
        load_img_id = self._next_id()
        self.nodes[load_img_id] = {
            "class_type": "LoadImage",
            "inputs": {"image": cfg["image"]},
            "_meta": {"title": "Load ControlNet Image"}
        }
        
        # Preprocessor - TODO: Make this configurable
        self.nodes[pre_id] = {
            "class_type": "CannyEdgePreprocessor",
            "inputs": {
                "image": [load_img_id, 0],
                "low_threshold": 100,
                "high_threshold": 200
            },
            "_meta": {"title": "Canny Edge Preprocessor"}
        }
        
        # ControlNet Apply
        cn_id = self._next_id()
        model_ref = self.options.get("model_ref")
        self.nodes[cn_id] = {
            "class_type": "ControlNetApply",
            "inputs": {
                "conditioning": self.options.get("positive_conditioning"),
                "control_net": cfg["model"],
                "image": [pre_id, 0],
                "strength": 1.0
            },
            "_meta": {"title": "Apply ControlNet"}
        }
        self.options["positive_conditioning"] = [cn_id, 0]

    def _add_init_image(self):
        """
        Load initial image for image-to-image generation.
        
        **Description:** Loads an initial image and stores the pixels reference.
        For inpainting/outpainting, the pixels will be used by InpaintModelConditioning.
        """
        path = self.options["init_image"]
        load_id = self._next_id()
        
        self.nodes[load_id] = {
            "class_type": "LoadImage",
            "inputs": {"image": path},
            "_meta": {"title": "Load Init Image"}
        }
        
        # Store pixels reference for potential inpainting/outpainting use
        self.options["pixels_ref"] = [load_id, 0]
        
        # For regular img2img (without inpainting/outpainting), encode to latent
        if "inpaint" not in self.options and "outpaint" not in self.options:
            encode_id = self._next_id()
            self.nodes[encode_id] = {
                "class_type": "VAEEncode",
                "inputs": {
                    "pixels": [load_id, 0],
                    "vae": self.options["vae_ref"]
                },
                "_meta": {"title": "VAE Encode"}
            }
            self.options["latent_ref"] = [encode_id, 0]

    def _add_inpainting(self):
        """
        Load inpainting mask for inpainting workflows.
        
        **Description:** Loads an inpainting mask and stores the mask reference.
        The mask will be used by InpaintModelConditioning node.
        """
        mask_path = self.options["inpaint"]
        load_mask_id = self._next_id()
        
        self.nodes[load_mask_id] = {
            "class_type": "LoadImageMask",
            "inputs": {
                "image": mask_path,
                "channel": "alpha"
            },
            "_meta": {"title": "Load Inpaint Mask"}
        }
        self.options["mask_ref"] = [load_mask_id, 0]

    def _add_outpainting(self):
        """
        Add outpainting padding for outpainting workflows.
        
        **Description:** Pads an existing image for outpainting and stores the padded pixels reference.
        The padded pixels will be used by InpaintModelConditioning node.
        """
        pad = self.options["outpaint"]
        pad_id = self._next_id()
        
        # Use the pixels from init_image if available, otherwise fallback
        pixels_ref = self.options.get("pixels_ref", ["1", 0])  # fallback
        
        self.nodes[pad_id] = {
            "class_type": "ImagePadForOutpaint",
            "inputs": {
                "image": pixels_ref,
                "left": pad,
                "top": pad, 
                "right": pad,
                "bottom": pad,
                "feathering": 20
            },
            "_meta": {"title": "Pad Image for Outpaint"}
        }
        
        # Store padded pixels reference for InpaintModelConditioning
        self.options["pixels_ref"] = [pad_id, 0]

    def build_prompt_workflow(self, params: GenerationParams) -> Dict:
        """
        Build a ComfyUI workflow based on generation parameters.
        
        **Description:** Creates a complete ComfyUI workflow JSON from GenerationParams.
        **Parameters:**
        - params (GenerationParams): The generation parameters including model, prompt, etc.
        **Returns:** A dictionary representing the ComfyUI workflow JSON
        """
        model_meta = MODEL_REGISTRY.get(params.model_key)
        if not model_meta:
            raise ValueError(f"Unknown model key: {params.model_key}")

        # Load model components
        model_ref, clip_ref, vae_ref = self.add_model_loader(model_meta["model_type"], model_meta["filename"])
        self.options["model_ref"] = model_ref
        self.options["clip_ref"] = clip_ref
        self.options["vae_ref"] = vae_ref

        # Configure features based on GenerationParams
        if params.loras:
            self.options['loras'] = params.loras
            
        if params.controlnet_image and params.controlnet_preprocessor and params.controlnet_model:
            self.options['controlnet'] = {
                "image": params.controlnet_image,
                "preprocessor": params.controlnet_preprocessor,
                "model": params.controlnet_model,
            }
            
        if params.init_image:
            self.options['init_image'] = params.init_image
            
        if params.inpaint_mask:
            self.options['inpaint'] = params.inpaint_mask
            
        if params.outpaint_padding:
            self.options['outpaint'] = params.outpaint_padding

        # Process features in correct order
        if "loras" in self.options:
            self._add_loras()
        if "init_image" in self.options:
            self._add_init_image()
        if "outpaint" in self.options:
            self._add_outpainting()
        if "inpaint" in self.options:
            self._add_inpainting()

        # Add TeaCache for models that support it (optimization) - only if enabled
        loader = ModelLoaderFactory.get_loader(model_meta["model_type"])
        if params.enable_tea_cache and loader.supports_tea_cache():
            self.options["model_ref"] = self._create_tea_cache_node(model_meta["model_type"], self.options["model_ref"])

        # Create seed generator
        seed_ref = self._create_seed_generator_node(params.seed)

        # Create text encoding nodes
        positive_ref, negative_ref = self._create_text_encode_nodes(params.prompt, params.negative_prompt, self.options["clip_ref"])

        # Apply ControlNet if specified
        if "controlnet" in self.options:
            self._add_controlnet()
            positive_ref = self.options["positive_conditioning"]

        # Handle inpainting/outpainting with InpaintModelConditioning node
        if ("inpaint" in self.options or "outpaint" in self.options) and "pixels_ref" in self.options:
            # Get mask reference if inpainting is enabled
            mask_ref = self.options.get("mask_ref") if "inpaint" in self.options else None
            
            # Create InpaintModelConditioning node
            positive_ref, negative_ref, latent_ref = self._create_inpaint_model_conditioning_node(
                positive_ref,
                negative_ref, 
                vae_ref,
                self.options["pixels_ref"],
                mask_ref
            )
            
            # Update references for the rest of the pipeline
            self.options["latent_ref"] = latent_ref

        # Create empty latent if no init image and no inpainting/outpainting
        if "latent_ref" not in self.options:
            self.options["latent_ref"] = self._create_aspect_ratio_node(params.width, params.height)

        # Update ModelSamplingFlux dimensions for models that support it
        if loader.supports_model_sampling_flux():
            for node in self.nodes.values():
                if node.get("class_type") == "ModelSamplingFlux":
                    node["inputs"]["width"] = params.width
                    node["inputs"]["height"] = params.height

        # Create sampler using the model loader's sampling logic
        sampled_latent_ref = loader.create_sampler_nodes(
            self, params, 
            self.options["model_ref"],
            positive_ref, 
            negative_ref,
            self.options["latent_ref"],
            seed_ref
        )

        # VAE Decode
        decoded_images_ref = self._create_vae_decode_node(sampled_latent_ref, vae_ref)

        # Save Image
        self._create_save_image_node(decoded_images_ref)

        # Add cache clear for optimization - only if enabled
        if params.enable_clear_cache:
            self._create_clear_cache_node(seed_ref)

        # Return the workflow in the correct format (just the nodes, not wrapped)
        return self.nodes


    @staticmethod
    def create_generation_params(
        model_key: str,
        prompt: str,
        **kwargs
    ) -> GenerationParams:
        """
        Create GenerationParams with sensible defaults and optional overrides.
        
        **Description:** Factory method to create GenerationParams instances with common defaults.
        **Parameters:**
        - model_key (str): The model identifier from MODEL_REGISTRY
        - prompt (str): The main generation prompt
        - **kwargs: Additional parameters to override defaults
        **Returns:** GenerationParams instance with applied settings
        """
        defaults = {
            "negative_prompt": "blurry, low quality, bad anatomy, worst quality",
            "sampler": "euler",
            "steps": 30,
            "cfg": 7.5,
            "width": 1024,
            "height": 1024,
            "seed": None,
            "loras": [],
            "controlnet_image": None,
            "controlnet_preprocessor": None,
            "controlnet_model": None,
            "init_image": None,
            "inpaint_mask": None,
            "outpaint_padding": None,
            "enable_tea_cache": True,
            "enable_clear_cache": True,
            "add_details": False,
            "wait": False
        }
        
        # Update defaults with provided kwargs
        defaults.update(kwargs)
        
        return GenerationParams(
            model_key=model_key,
            prompt=prompt,
            **defaults
        )
    def _create_inpaint_model_conditioning_node(self, positive_ref: List, negative_ref: List, 
                                               vae_ref: List, pixels_ref: List, mask_ref: Optional[List] = None) -> Tuple[List, List, List]:
        """
        Create InpaintModelConditioning node for inpainting and outpainting workflows.
        
        **Description:** Creates an InpaintModelConditioning node that properly conditions
        the model for inpainting or outpainting tasks by combining positive/negative conditioning
        with image pixels and optional mask.
        
        **Parameters:**
        - positive_ref (List): Reference to positive conditioning
        - negative_ref (List): Reference to negative conditioning  
        - vae_ref (List): Reference to VAE model
        - pixels_ref (List): Reference to image pixels (init_image or padded image)
        - mask_ref (Optional[List]): Reference to mask for inpainting, None for outpainting
        
        **Returns:** Tuple of (positive_conditioning_ref, negative_conditioning_ref, latent_ref)
        """
        inpaint_conditioning_id = self._next_id()
        
        inputs = {
            "positive": positive_ref,
            "negative": negative_ref,
            "vae": vae_ref,
            "pixels": pixels_ref
        }
        
        # Add mask if provided (for inpainting)
        if mask_ref is not None:
            inputs["mask"] = mask_ref
            
        self.nodes[inpaint_conditioning_id] = {
            "class_type": "InpaintModelConditioning",
            "inputs": inputs,
            "_meta": {"title": "Inpaint Model Conditioning"}
        }
        
        return ([inpaint_conditioning_id, 0], [inpaint_conditioning_id, 1], [inpaint_conditioning_id, 2])
