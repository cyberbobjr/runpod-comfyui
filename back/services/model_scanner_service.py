import os
import json
import hashlib
import pickle
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from ..utils.logger import get_logger
from ..utils.hash_utils import HashUtils
from .config_service import ConfigService
from .token_service import TokenService
from .civitai_client import CivitAIClient

# Optional imports for model file analysis
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False

try:
    from safetensors.torch import load_file
    SAFETENSORS_AVAILABLE = True
except ImportError:
    load_file = None
    SAFETENSORS_AVAILABLE = False

CACHE_NAME = '.model_scanner_cache.pkl'

# Initialize logger
logger = get_logger(__name__)

class ModelScannerService:
    """
    Service for scanning and analyzing model files in the models directory.
    
    **Purpose:** Handles model discovery and classification including:
    - Scanning models directory for safetensors and sft files
    - Determining model types (checkpoint, diffusion, VAE, CLIP)
    - Providing metadata about discovered models
    - Organizing models by type and location
    - Caching results for performance
    - Extended metadata extraction
    
    **SRP Responsibility:** Model file discovery and classification.
    This class should NOT handle model downloads (use DownloadService) or
    model configuration management (use ModelManager).
    """

    # Model type classifications based on directory structure
    MODEL_TYPES = {
        "checkpoints": ["checkpoint", "diffusion_loader"],
        "vae": ["vae"],
        "clip": ["clip"],
        "clip_vision": ["clip"],
        "controlnet": ["controlnet"],
        "embeddings": ["embeddings"],
        "loras": ["lora"],
        "hypernetworks": ["hypernetworks"],
        "upscale_models": ["upscale"],
        "style_models": ["style"],
        "diffusion_models": ["diffusion_loader"],
        "unet": ["diffusion_loader"],
        "text_encoders": ["clip"]
    }

    # Extended file extensions to scan for
    SUPPORTED_EXTENSIONS = ['.safetensors', '.sft', '.ckpt', '.pt', '.pth', '.bin', '.pkl', '.tar', '.gz', '.zip']

    # Cache for model analysis results
    _cache = {}
    _cache_file = None

    @classmethod
    def _get_cache_file_path(cls) -> str:
        """
        Gets the path to the cache file.
        
        **Description:** Returns the path where the cache file should be stored.
        **Parameters:** None
        **Returns:** str containing the cache file path
        """
        if cls._cache_file is None:
            models_dir = ConfigService.get_models_dir()
            cls._cache_file = os.path.join(models_dir, CACHE_NAME)
        return cls._cache_file

    @classmethod
    def _load_cache(cls) -> None:
        """
        Loads the cache from disk.
        
        **Description:** Loads previously cached model analysis results from disk.
        **Parameters:** None
        **Returns:** None
        """
        cache_file = cls._get_cache_file_path()
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cls._cache = pickle.load(f)
                logger.debug(f"Loaded cache with {len(cls._cache)} entries")
            except Exception as e:
                logger.warning(f"Failed to load cache: {str(e)}")
                cls._cache = {}

    @classmethod
    def _save_cache(cls) -> None:
        """
        Saves the cache to disk.
        
        **Description:** Saves the current cache to disk for future use.
        **Parameters:** None
        **Returns:** None
        """
        cache_file = cls._get_cache_file_path()
        try:
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, 'wb') as f:
                pickle.dump(cls._cache, f)
            logger.debug(f"Saved cache with {len(cls._cache)} entries")
        except Exception as e:
            logger.warning(f"Failed to save cache: {str(e)}")

    @classmethod
    def _get_file_hash(cls, file_path: str) -> str:
        """
        Generates a hash for a file based on its path, size, and modification time.
        
        **Description:** Creates a unique identifier for a file to use as cache key.
        **Parameters:**
        - `file_path` (str): Path to the file
        **Returns:** str containing the file hash
        """
        try:
            stat = os.stat(file_path)
            content = f"{file_path}:{stat.st_size}:{stat.st_mtime}"
            return hashlib.md5(content.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to generate hash for {file_path}: {str(e)}")
            return hashlib.md5(file_path.encode()).hexdigest()

    @classmethod
    def _is_cache_valid(cls, file_hash: str, file_path: str) -> bool:
        """
        Checks if cache entry is still valid.
        
        **Description:** Validates that the cached entry matches the current file state.
        **Parameters:**
        - `file_hash` (str): Hash of the file
        - `file_path` (str): Path to the file
        **Returns:** bool indicating if cache is valid
        """
        if file_hash not in cls._cache:
            return False
        
        cached_entry = cls._cache[file_hash]
        if not os.path.exists(file_path):
            return False
        
        # Check if file has been modified since cache entry
        try:
            stat = os.stat(file_path)
            cached_mtime = cached_entry.get('cache_mtime', 0)
            return stat.st_mtime <= cached_mtime
        except Exception:
            return False

    @staticmethod
    def identify_file(file_path: str) -> Optional[str]:
        # ModelScannerService._load_cache()
        # file_hash = ModelScannerService._get_file_hash(file_path)
        # if ModelScannerService._is_cache_valid(file_hash, file_path):
        #     cached_result = ModelScannerService._cache[file_hash]
        #     logger.debug(f"Using cached identification for {file_path}")
        #     return cached_result.get('identified_type')

        path = Path(file_path)
        ext = path.suffix.lower()

        try:
            # Chargement du fichier selon son format
            if ext in {'.ckpt', '.pth', '.pt'}:
                if not TORCH_AVAILABLE:
                    logger.warning("PyTorch not available")
                    return None
                try:
                    state = torch.load(path, map_location='cpu', weights_only=True)
                except Exception as e:
                    logger.debug(f"Could not load PyTorch file {file_path}: {str(e)}")
                    return "unreadable_checkpoint"
                keys = set(state.keys()) if isinstance(state, dict) else set()

            elif ext in {'.safetensors', '.sft'}:
                if not SAFETENSORS_AVAILABLE:
                    logger.warning("SafeTensors not available")
                    return None
                try:
                    state = load_file(path)
                    keys = set(state.keys())
                except Exception as e:
                    logger.debug(f"Could not load SafeTensors file {file_path}: {str(e)}")
                    return "unreadable_safetensor"

            elif ext == '.pkl':
                try:
                    with open(path, 'rb') as f:
                        state = pickle.load(f)
                    keys = set(state.keys()) if isinstance(state, dict) else set()
                except Exception as e:
                    logger.debug(f"Could not load pickle file {file_path}: {str(e)}")
                    return "unreadable_pickle"

            elif ext in {'.tar', '.gz', '.zip'}:
                logger.debug(f"Compressed file format {ext} not yet supported")
                return "compressed_model"

            else:
                return None

            # === Détection par structure des clés ===
            has_unet = any(k.startswith('model.diffusion_model') or 'unet' in k for k in keys)

            has_clip = any(
                k.startswith('cond_stage_model.') or
                k.startswith('text_encoder.') or
                k.startswith('conditioner.embedders.0') or
                k.startswith('text_model.encoder.') or
                'clip_l' in k
                for k in keys
            )

            has_vae = any(
                k.startswith('vae.') or
                k.startswith('first_stage_model.') or
                'encoder.mid' in k or
                'decoder.up' in k
                for k in keys
            )

            has_lora = any(
                'lora_down' in k or
                'lora_up' in k or
                k.startswith('lora_te_') or
                k.startswith('lora_unet_') or
                k.startswith('lora_clip_')
                for k in keys
            )

            has_controlnet = any('control_model' in k or 'controlnet' in k for k in keys)

            has_embedding = any(
                'string_to_token' in k or 'string_to_param' in k or
                (len(keys) == 1 and any(k.startswith('<') and k.endswith('>') for k in keys))
                for k in keys
            )

            is_upscale = any(
                k.startswith('conv_first') or
                k.startswith('upsample') or
                k.startswith('model.0') or
                k.startswith('body.') or
                k.startswith('params_ema') or
                'realesrgan' in k.lower() or
                'swinir' in k.lower()
                for k in keys
            )

            # === Classification logique ===
            if has_unet and has_clip and has_vae:
                identified_type = 'checkpoint'
            elif has_unet:
                identified_type = 'diffusion_loader'
            elif has_clip:
                identified_type = 'clip'
            elif has_vae:
                identified_type = 'vae'
            elif has_lora:
                identified_type = 'lora'
            elif has_controlnet:
                identified_type = 'controlnet'
            elif has_embedding:
                identified_type = 'embedding'
            elif is_upscale:
                identified_type = 'upscale'
            else:
                identified_type = 'unknown'

            # === Mise en cache ===
            # ModelScannerService._cache[file_hash] = {
            #     'identified_type': identified_type,
            #     'cache_mtime': datetime.now().timestamp(),
            #     'file_path': file_path
            # }
            # ModelScannerService._save_cache()

            return identified_type

        except Exception as e:
            logger.error(f"Error identifying file {file_path}: {str(e)}")
            return None

    @staticmethod
    def scan_models_directory() -> Dict[str, List[Dict[str, Any]]]:
        """
        Scans the models directory for all supported model files.
        
        **Description:** Recursively scans the models directory and classifies found models.
        **Parameters:** None
        **Returns:** Dict containing categorized model information
        """
        models_dir = ConfigService.get_models_dir()
        
        if not os.path.exists(models_dir):
            logger.warning(f"Models directory not found: {models_dir}")
            return {
                "error": f"Models directory not found: {models_dir}",
                "models": {}
            }
        
        discovered_models = {
            "checkpoints": [],
            "vae": [],
            "clip": [],
            "controlnet": [],
            "embeddings": [],
            "loras": [],
            "hypernetworks": [],
            "upscale_models": [],
            "style_models": [],
            "diffusion_models": [],
            "unet": [],
            "text_encoders": [],
            "other": []
        }
        
        logger.info(f"Scanning models directory: {models_dir}")
        
        try:
            # Walk through all subdirectories
            for root, _, files in os.walk(models_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_extension = Path(file).suffix.lower()
                    file_name = os.path.basename(file_path)
                    if file_name == CACHE_NAME:
                        continue
                    if file_extension in ModelScannerService.SUPPORTED_EXTENSIONS:
                        model_info = ModelScannerService._analyze_model_file(file_path, models_dir)
                        
                        # Use the category determined by _analyze_model_file
                        category = model_info.get("category", "other")
                        
                        # If category is "other", try to identify using CivitAI
                        if category == "other":
                            enhanced_model_info = ModelScannerService._enhance_model_with_civitai(model_info)
                            if enhanced_model_info:
                                model_info = enhanced_model_info
                                category = model_info.get("category", "other")
                        
                        if category in discovered_models:
                            discovered_models[category].append(model_info)
                        else:
                            discovered_models["other"].append(model_info)
            
            # Log summary
            total_models = sum(len(models) for models in discovered_models.values())
            logger.info(f"Discovered {total_models} models in {models_dir}")
            
            return {
                "models_directory": models_dir,
                "total_models": total_models,
                "models": discovered_models
            }
            
        except Exception as e:
            logger.error(f"Error scanning models directory: {str(e)}")
            return {
                "error": f"Error scanning models directory: {str(e)}",
                "models": {}
            }

    @staticmethod
    def _analyze_model_file(file_path: str, models_dir: str) -> Dict[str, Any]:
        """
        Analyzes a single model file and extracts metadata.
        
        **Description:** Extracts comprehensive information about a model file including size, type, location, and extended metadata.
        **Parameters:**
        - `file_path` (str): Full path to the model file
        - `models_dir` (str): Base models directory path
        **Returns:** Dict containing model file metadata including category and extended information
        """
        try:
            # Get file stats
            stat = os.stat(file_path)
            file_size = stat.st_size
            
            # Calculate relative path from models directory
            relative_path = os.path.relpath(file_path, models_dir)
            
            # Extract directory information
            dir_parts = Path(relative_path).parts
            subdirectory = dir_parts[0] if len(dir_parts) > 1 else ""
            
            # Get file information
            file_name = os.path.basename(file_path)
            file_extension = Path(file_path).suffix.lower()
            
            # Use advanced model identification first
            identified_type = ModelScannerService.identify_file(file_path)
            
            # Extract extended metadata
            extended_metadata = ModelScannerService._extract_extended_metadata(file_path)
            
            # Determine model type and category
            if identified_type:
                if identified_type in ['unreadable_checkpoint', 'unreadable_safetensor', 'unreadable_pickle', 'compressed_model']:
                    model_type = [identified_type]
                    category = "other"
                else:
                    # Map identified types to our classification system
                    model_type = ModelScannerService._map_identified_type_to_classification(identified_type)
                    category = ModelScannerService._get_category_from_identified_type(identified_type)
            else:
                # Fallback to directory-based classification
                model_type = ModelScannerService._determine_model_type(file_path, subdirectory)
                category = ModelScannerService._get_category_from_directory(subdirectory)
            
            # Build comprehensive result
            result = {
                "name": file_name,
                "path": file_path,
                "relative_path": relative_path,
                "subdirectory": subdirectory,
                "size": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "size_gb": round(file_size / (1024 * 1024 * 1024), 3),
                "extension": file_extension,
                "type": model_type,
                "identified_type": identified_type,
                "category": category,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "exists": True
            }
            
            # Add extended metadata if available
            if extended_metadata:
                result["extended_metadata"] = extended_metadata
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing model file {file_path}: {str(e)}")
            return {
                "name": os.path.basename(file_path),
                "path": file_path,
                "relative_path": os.path.relpath(file_path, models_dir),
                "error": str(e),
                "category": "other",
                "exists": False
            }

    @staticmethod
    def _extract_extended_metadata(file_path: str) -> Dict[str, Any]:
        """
        Extracts extended metadata from model files.
        
        **Description:** Extracts additional information like tensor shapes, parameter counts, and model architecture details.
        **Parameters:**
        - `file_path` (str): Path to the model file
        **Returns:** Dict containing extended metadata
        """
        metadata = {}
        path = Path(file_path)
        ext = path.suffix.lower()
        
        try:
            # Try to extract metadata based on file type
            if ext in {'.safetensors', '.sft'} and SAFETENSORS_AVAILABLE:
                metadata = ModelScannerService._extract_safetensors_metadata(file_path)
            elif ext in {'.ckpt', '.pth', '.pt'} and TORCH_AVAILABLE:
                metadata = ModelScannerService._extract_torch_metadata(file_path)
            elif ext in {'.pkl'}:
                metadata = ModelScannerService._extract_pickle_metadata(file_path)
            
            # Add file-based metadata
            metadata.update({
                "file_hash": ModelScannerService._get_file_hash(file_path),
                "is_compressed": ext in {'.tar', '.gz', '.zip'},
                "supported_format": ext in ModelScannerService.SUPPORTED_EXTENSIONS
            })
            
        except Exception as e:
            logger.debug(f"Could not extract extended metadata from {file_path}: {str(e)}")
            metadata["extraction_error"] = str(e)
        
        return metadata

    @staticmethod
    def _extract_safetensors_metadata(file_path: str) -> Dict[str, Any]:
        """
        Extracts metadata from SafeTensors files.
        
        **Description:** Extracts tensor information and metadata from SafeTensors files.
        **Parameters:**
        - `file_path` (str): Path to the SafeTensors file
        **Returns:** Dict containing SafeTensors metadata
        """
        metadata = {}
        try:
            # Load SafeTensors file
            state = load_file(file_path)
            
            # Count parameters and tensors
            total_params = 0
            tensor_info = {}
            
            for key, tensor in state.items():
                if hasattr(tensor, 'shape'):
                    tensor_info[key] = {
                        "shape": list(tensor.shape),
                        "dtype": str(tensor.dtype),
                        "size": tensor.numel() if hasattr(tensor, 'numel') else len(tensor.flatten())
                    }
                    total_params += tensor_info[key]["size"]
            
            metadata.update({
                "total_parameters": total_params,
                "total_parameters_millions": round(total_params / 1_000_000, 2),
                "tensor_count": len(tensor_info),
                "tensor_info": tensor_info,
                "format": "safetensors"
            })
            
        except Exception as e:
            logger.debug(f"Error extracting SafeTensors metadata: {str(e)}")
            metadata["error"] = str(e)
        
        return metadata

    @staticmethod
    def _extract_torch_metadata(file_path: str) -> Dict[str, Any]:
        """
        Extracts metadata from PyTorch files.
        
        **Description:** Extracts tensor information and metadata from PyTorch checkpoint files.
        **Parameters:**
        - `file_path` (str): Path to the PyTorch file
        **Returns:** Dict containing PyTorch metadata
        """
        metadata = {}
        try:
            # Load PyTorch file
            state = torch.load(file_path, map_location='cpu', weights_only=True)
            
            if isinstance(state, dict):
                # Count parameters and tensors
                total_params = 0
                tensor_info = {}
                
                for key, tensor in state.items():
                    if hasattr(tensor, 'shape'):
                        tensor_info[key] = {
                            "shape": list(tensor.shape),
                            "dtype": str(tensor.dtype),
                            "size": tensor.numel()
                        }
                        total_params += tensor_info[key]["size"]
                
                metadata.update({
                    "total_parameters": total_params,
                    "total_parameters_millions": round(total_params / 1_000_000, 2),
                    "tensor_count": len(tensor_info),
                    "tensor_info": tensor_info,
                    "format": "pytorch"
                })
                
        except Exception as e:
            logger.debug(f"Error extracting PyTorch metadata: {str(e)}")
            metadata["error"] = str(e)
        
        return metadata

    @staticmethod
    def _extract_pickle_metadata(file_path: str) -> Dict[str, Any]:
        """
        Extracts metadata from pickle files.
        
        **Description:** Extracts basic information from pickle files.
        **Parameters:**
        - `file_path` (str): Path to the pickle file
        **Returns:** Dict containing pickle metadata
        """
        metadata = {}
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            metadata.update({
                "format": "pickle",
                "data_type": str(type(data)),
                "is_dict": isinstance(data, dict),
                "keys_count": len(data.keys()) if isinstance(data, dict) else 0
            })
            
            if isinstance(data, dict):
                metadata["top_level_keys"] = list(data.keys())[:10]  # First 10 keys
                
        except Exception as e:
            logger.debug(f"Error extracting pickle metadata: {str(e)}")
            metadata["error"] = str(e)
        
        return metadata

    @staticmethod
    def _get_category_from_identified_type(identified_type: str) -> str:
        """
        Maps advanced identification results to category names.
        
        **Description:** Converts the advanced model identification result to category names.
        **Parameters:**
        - `identified_type` (str): The type identified by advanced analysis
        **Returns:** str containing the category name
        """
        type_to_category = {
            'checkpoint': 'checkpoints',
            'diffusion_loader': 'diffusion_models',
            'clip': 'clip',
            'vae': 'vae',
            'lora': 'loras',
            'controlnet': 'controlnet',
            'embedding': 'embeddings',
            'upscale': 'upscale_models',
            'unknown': 'other',
            'unreadable_checkpoint': 'other',
            'unreadable_safetensor': 'other'
        }
        
        return type_to_category.get(identified_type, 'other')

    @staticmethod
    def _get_category_from_directory(subdirectory: str) -> str:
        """
        Determines category based on directory structure as fallback.
        
        **Description:** Uses directory structure to determine model category when advanced identification fails.
        **Parameters:**
        - `subdirectory` (str): Subdirectory within models folder
        **Returns:** str containing the category name
        """
        if not subdirectory:
            return "checkpoints"  # Default for models in root directory
        
        subdirectory_lower = subdirectory.lower()
        
        # Check against known directory patterns
        if "checkpoint" in subdirectory_lower or "ckpt" in subdirectory_lower:
            return "checkpoints"
        elif "vae" in subdirectory_lower:
            return "vae"
        elif "clip" in subdirectory_lower:
            return "clip"
        elif "controlnet" in subdirectory_lower or "control" in subdirectory_lower:
            return "controlnet"
        elif "lora" in subdirectory_lower:
            return "loras"
        elif "embed" in subdirectory_lower:
            return "embeddings"
        elif "upscale" in subdirectory_lower:
            return "upscale_models"
        elif "diffusion" in subdirectory_lower or "unet" in subdirectory_lower:
            return "diffusion_models"
        elif "hypernetwork" in subdirectory_lower:
            return "hypernetworks"
        elif "style" in subdirectory_lower:
            return "style_models"
        elif "text_encoder" in subdirectory_lower:
            return "text_encoders"
        
        return "other"

    @staticmethod
    def _determine_model_type(file_path: str, subdirectory: str) -> List[str]:
        """
        Determines the possible model types based on file analysis.
        
        **Description:** Analyzes file characteristics to determine compatible model types.
        **Parameters:**
        - `file_path` (str): Full path to the model file
        - `subdirectory` (str): Subdirectory within models folder
        **Returns:** List of possible model types
        """
        file_name = os.path.basename(file_path).lower()
        subdirectory_lower = subdirectory.lower()
        
        # Determine possible types based on directory and filename
        possible_types = []
        
        # Check directory-based classification
        if "checkpoint" in subdirectory_lower or "ckpt" in subdirectory_lower:
            possible_types.extend(["checkpoint", "diffusion_loader"])
        elif "vae" in subdirectory_lower:
            possible_types.append("vae")
        elif "clip" in subdirectory_lower:
            possible_types.append("clip")
        elif "controlnet" in subdirectory_lower:
            possible_types.append("controlnet")
        elif "lora" in subdirectory_lower:
            possible_types.append("lora")
        elif "embed" in subdirectory_lower:
            possible_types.append("embeddings")
        elif "upscale" in subdirectory_lower:
            possible_types.append("upscale")
        elif "diffusion" in subdirectory_lower or "unet" in subdirectory_lower:
            possible_types.append("diffusion_loader")
        
        # Check filename-based patterns
        if "vae" in file_name:
            possible_types.append("vae")
        if "clip" in file_name:
            possible_types.append("clip")
        if "controlnet" in file_name or "control" in file_name:
            possible_types.append("controlnet")
        if "lora" in file_name:
            possible_types.append("lora")
        if "embed" in file_name:
            possible_types.append("embeddings")
        if "upscale" in file_name:
            possible_types.append("upscale")
        
        # Default fallback
        if not possible_types:
            if subdirectory_lower:
                possible_types = ["unknown"]
            else:
                possible_types = ["checkpoint", "diffusion_loader"]
        
        return possible_types

    @staticmethod
    def _map_identified_type_to_classification(identified_type: str) -> List[str]:
        """
        Maps advanced identification results to our classification system.
        
        **Description:** Converts the advanced model identification result to our internal classification types.
        **Parameters:**
        - `identified_type` (str): The type identified by advanced analysis
        **Returns:** List[str] containing compatible classification types
        """
        mapping = {
            'checkpoint': ['checkpoint'],
            'diffusion_loader': ['diffusion_loader'],
            'clip': ['clip'],
            'vae': ['vae'],
            'lora': ['lora'],
            'controlnet': ['controlnet'],
            'embedding': ['embeddings'],
            'upscale': ['upscale'],
            'unknown': ['unknown'],
            'unreadable_checkpoint': ['unreadable'],
            'unreadable_safetensor': ['unreadable'],
            'unreadable_pickle': ['unreadable'],
            'compressed_model': ['compressed']
        }
        
        return mapping.get(identified_type, ['unknown'])

    @staticmethod
    def clear_cache() -> None:
        """
        Clears the model scanner cache.
        
        **Description:** Removes all cached model analysis results.
        **Parameters:** None
        **Returns:** None
        """
        ModelScannerService._cache.clear()
        cache_file = ModelScannerService._get_cache_file_path()
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                logger.info("Model scanner cache cleared")
            except Exception as e:
                logger.warning(f"Failed to remove cache file: {str(e)}")

    @staticmethod
    def get_cache_info() -> Dict[str, Any]:
        """
        Gets information about the current cache state.
        
        **Description:** Returns statistics about the cache including size and entries.
        **Parameters:** None
        **Returns:** Dict containing cache information
        """
        ModelScannerService._load_cache()
        cache_file = ModelScannerService._get_cache_file_path()
        
        cache_info = {
            "entries_count": len(ModelScannerService._cache),
            "cache_file_exists": os.path.exists(cache_file),
            "cache_file_path": cache_file
        }
        
        if os.path.exists(cache_file):
            try:
                stat = os.stat(cache_file)
                cache_info.update({
                    "cache_file_size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "cache_last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception as e:
                cache_info["cache_file_error"] = str(e)
        
        return cache_info

    @staticmethod
    def get_model_summary() -> Dict[str, Any]:
        """
        Gets a summary of all discovered models.
        
        **Description:** Provides a high-level overview of model discovery results.
        **Parameters:** None
        **Returns:** Dict containing model summary statistics
        """
        scan_results = ModelScannerService.scan_models_directory()
        
        if "error" in scan_results:
            return scan_results
        
        models = scan_results.get("models", {})
        summary = {
            "total_models": scan_results.get("total_models", 0),
            "models_directory": scan_results.get("models_directory", ""),
            "categories": {}
        }
        
        for category, model_list in models.items():
            if model_list:  # Only include categories with models
                summary["categories"][category] = {
                    "count": len(model_list),
                    "total_size_mb": sum(model.get("size_mb", 0) for model in model_list)
                }
        
        return summary

    @staticmethod
    def search_models(query: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Searches for models matching a query string.
        
        **Description:** Searches through discovered models by name or path.
        **Parameters:**
        - `query` (str): Search query string
        - `category` (str, optional): Specific category to search in
        **Returns:** Dict containing matching models
        """
        scan_results = ModelScannerService.scan_models_directory()
        
        if "error" in scan_results:
            return scan_results
        
        models = scan_results.get("models", {})
        matches = {}
        query_lower = query.lower()
        
        for cat, model_list in models.items():
            if category and cat != category:
                continue
                
            matching_models = []
            for model in model_list:
                model_name = model.get("name", "").lower()
                model_path = model.get("relative_path", "").lower()
                
                if query_lower in model_name or query_lower in model_path:
                    matching_models.append(model)
            
            if matching_models:
                matches[cat] = matching_models
        
        return {
            "query": query,
            "category": category,
            "matches": matches,
            "total_matches": sum(len(models) for models in matches.values())
        }

    @staticmethod
    def _enhance_model_with_civitai(model_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enhances model information using CivitAI API for unknown models.
        
        **Description:** When a model category is "other", attempts to identify it using CivitAI's database
        by computing an AutoV2 hash and querying the API once. Includes a 3-second delay to be respectful to CivitAI servers.
        **Parameters:**
        - `model_info` (Dict[str, Any]): Original model information
        **Returns:** Optional[Dict[str, Any]] containing enhanced model information or None if not found
        """
        try:
            # Get CivitAI token
            tokens = TokenService.get_tokens()
            civitai_token = tokens.get("civitai_token")
            
            if not civitai_token:
                logger.debug("CivitAI token not available, skipping CivitAI enhancement")
                return None
            
            # Initialize CivitAI client
            client = CivitAIClient(api_key=civitai_token)
            
            file_path = model_info.get("path")
            if not file_path or not os.path.exists(file_path):
                logger.warning(f"File path not found for CivitAI enhancement: {file_path}")
                return None
            
            # Use only AutoV2 algorithm to minimize API calls
            algorithm = 'AutoV2'
            civitai_info = None
            
            try:
                # Compute hash
                file_hash = HashUtils.get_file_hash(file_path, algorithm)
                if not file_hash:
                    logger.debug(f"Failed to compute {algorithm} hash for {file_path}")
                    return None
                
                logger.debug(f"Trying CivitAI lookup with {algorithm} hash: {file_hash}")
                
                # Query CivitAI API
                civitai_info = client.get_model_version_by_hash(file_hash)
                # Rate limiting - wait 3 seconds to be respectful to CivitAI servers
                time.sleep(3)
                
                if civitai_info:
                    with open("temp.json", 'w') as f:
                        json.dump(civitai_info, f, indent=2)
                    logger.info(f"Found CivitAI match for {file_path} using {algorithm} hash")
                else:
                    logger.debug(f"No CivitAI match found with {algorithm} hash")
                
            except Exception as e:
                logger.warning(f"Error querying CivitAI with {algorithm} hash: {str(e)}")
                return None
            
            if not civitai_info:
                logger.debug(f"No CivitAI information found for {file_path}")
                return None
            
            # Enhance model info with CivitAI data
            enhanced_info = model_info.copy()
            
            # Extract relevant CivitAI information
            civitai_model = civitai_info.get("model", {})
            civitai_files = civitai_info.get("files", [])
            
            # Determine category from CivitAI model type
            civitai_type = civitai_model.get("type", "").lower()
            category = ModelScannerService._map_civitai_type_to_category(civitai_type)
            
            # Update model info with CivitAI data
            enhanced_info.update({
                "category": category,
                "civitai_info": {
                    "model_id": civitai_model.get("id"),
                    "model_name": civitai_model.get("name"),
                    "model_type": civitai_type,
                    "version_id": civitai_info.get("id"),
                    "version_name": civitai_info.get("name"),
                    "base_model": civitai_info.get("baseModel"),
                    "description": civitai_model.get("description"),
                    "tags": civitai_model.get("tags", []),
                    "nsfw": civitai_model.get("nsfw", False),
                    "creator": civitai_model.get("creator", {}).get("username"),
                    "download_url": civitai_info.get("downloadUrl"),
                    "image_urls": [img.get("url") for img in civitai_info.get("images", [])],
                    "stats": civitai_model.get("stats", {}),
                    "hash_algorithm": algorithm,
                    "hash_value": file_hash
                }
            })
            
            logger.info(f"Enhanced model info for {file_path} with CivitAI data: {civitai_model.get('name')} ({civitai_type})")
            return enhanced_info
            
        except Exception as e:
            logger.error(f"Error enhancing model with CivitAI: {str(e)}")
            return None
    
    @staticmethod
    def _map_civitai_type_to_category(civitai_type: str) -> str:
        """
        Maps CivitAI model types to our internal categories.
        
        **Description:** Converts CivitAI model type strings to our category system.
        **Parameters:**
        - `civitai_type` (str): CivitAI model type
        **Returns:** str containing the mapped category
        """
        type_mapping = {
            "checkpoint": "checkpoints",
            "textualinversion": "embeddings",
            "hypernetwork": "hypernetworks",
            "aestheticgradient": "other",
            "lora": "loras",
            "controlnet": "controlnet",
            "upscaler": "upscale_models",
            "motionmodule": "other",
            "vae": "vae",
            "poses": "other",
            "wildcards": "other",
            "workflows": "other",
            "other": "other"
        }
        
        return type_mapping.get(civitai_type, "other")
