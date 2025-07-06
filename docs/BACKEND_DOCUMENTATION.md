# Backend Documentation

## Architecture Overview

The backend is built using FastAPI with Python, providing a robust API for ComfyUI workflow management, model handling, and image generation capabilities. The architecture follows a clean separation of concerns with distinct layers for routing, services, and utilities.

## Core Components

### Services Layer

#### ComfyWorkflowBuilder
**Location:** `back/services/comfy_workflow_builder.py`

**Purpose:** Core service for building ComfyUI workflows programmatically with support for multiple model types and advanced generation features.

**Key Features:**
- **Factory Pattern Architecture:** Extensible model loader system using the Factory pattern
- **Multiple Model Support:** Flux, SDXL, HiDream, and custom models
- **Advanced Generation Parameters:** LoRA integration, optimization settings, detail enhancement
- **Workflow Types:** Text-to-image, image-to-image, inpainting, outpainting

**Methods:**
- `build_prompt_workflow(params: GenerationParams)` - Main workflow building method
- `create_generation_params()` - Factory method for parameter creation
- `add_model_loader()` - Adds appropriate model loader based on type
- `_create_*_node()` - Private methods for specific node creation

#### Model Loader System
**Location:** `back/services/comfy_workflow_builder.py`

**Architecture:** Factory pattern with abstract base class and concrete implementations

**Classes:**
- `BaseModelLoader` - Abstract base class for all model loaders
- `CheckpointModelLoader` - Handles SDXL and SD1.5 models
- `FluxModelLoader` - Handles Flux models with complex node setup
- `HiDreamModelLoader` - Handles HiDream models with QuadrupleCLIP
- `ModelLoaderFactory` - Manages loader registration and creation

**Key Methods:**
- `create_loader_nodes()` - Creates appropriate loader nodes for model type
- `create_sampler_nodes()` - Creates sampling nodes specific to model type
- `supports_tea_cache()` - Checks if model supports TeaCache optimization
- `supports_flux_guidance()` - Checks if model supports Flux guidance

### API Routers

#### ComfyUI Router
**Location:** `back/routers/comfy_router.py`

**Endpoints:**
- `GET /api/comfy/models` - List available models
- `POST /api/comfy/workflow/generate` - Generate workflow from parameters
- `POST /api/comfy/workflow/execute` - Execute workflow on ComfyUI server
- `GET /api/comfy/workflow/status/{prompt_id}` - Get workflow execution status
- `GET /api/comfy/workflow/result/{prompt_id}` - Get workflow results

#### Workflow Router
**Location:** `back/routers/workflow_router.py`

**Purpose:** Manages workflow templates and execution

**Endpoints:**
- `GET /api/workflows` - List available workflows
- `POST /api/workflows/upload` - Upload new workflow
- `GET /api/workflows/{workflow_id}` - Get specific workflow
- `DELETE /api/workflows/{workflow_id}` - Delete workflow

#### Model Router
**Location:** `back/routers/model_router.py`

**Purpose:** Manages model metadata and downloads

**Endpoints:**
- `GET /api/models` - List available models
- `POST /api/models/download` - Download model
- `GET /api/models/status` - Get download status
- `POST /api/models/install` - Install model

#### Additional Routers
- `back/routers/auth_router.py` - Authentication and user management
- `back/routers/bundle_router.py` - Bundle management
- `back/routers/download_router.py` - Download management
- `back/routers/file_manager_router.py` - File management
- `back/routers/json_models_router.py` - JSON model management
- `back/routers/model_groups_router.py` - Model group management
- `back/routers/token_router.py` - Token management

### Data Models

#### Generation Parameters
**Location:** `back/models/` and `back/services/comfy_workflow_builder.py`

**Purpose:** Defines parameters for image generation

**Key Fields:**
- `model_key` - Model identifier
- `prompt` - Positive prompt
- `negative_prompt` - Negative prompt
- `steps` - Number of generation steps
- `cfg` - CFG scale
- `width`, `height` - Image dimensions
- `loras` - List of LoRA configurations
- `enable_tea_cache` - TeaCache optimization
- `add_details` - Detail enhancement

#### Additional Models
- `back/models/auth_models.py` - Authentication models
- `back/models/bundle_models.py` - Bundle management models
- `back/models/file_models.py` - File management models
- `back/models/json_models.py` - JSON model definitions
- `back/models/model_models.py` - Model registry models
- `back/models/workflow_models.py` - Workflow models

### Utilities

#### Configuration Management
**Location:** `back/services/config_service.py`

**Purpose:** Centralizes application configuration

**Features:**
- Environment variable loading
- Configuration validation
- Default value management
- Runtime configuration updates

#### Additional Services
- `back/services/auth_service.py` - Authentication service
- `back/services/bundle_service.py` - Bundle management
- `back/services/download_service.py` - Download handling
- `back/services/file_manager_service.py` - File operations
- `back/services/model_service.py` - Model operations
- `back/services/workflow_service.py` - Workflow management

## Advanced Features

### InpaintModelConditioning
**Implementation:** Integrated into `ComfyWorkflowBuilder`

**Purpose:** Handles inpainting and outpainting workflows with proper model conditioning

**Features:**
- Automatic conditioning for inpainting/outpainting tasks
- Universal compatibility with all model types
- Seamless integration with existing workflows
- Optional mask handling for inpainting

**Usage:**
```python
# Automatically used when init_image is provided
params = GenerationParams(
    model_key="sdxl",
    prompt="A beautiful landscape",
    init_image="path/to/image.png",
    # ... other parameters
)
```

### TeaCache Optimization
**Implementation:** Integrated into model loaders

**Purpose:** Provides memory optimization for supported models

**Supported Models:**
- Flux models (flux-dev, flux-schnell)
- HiDream models

**Features:**
- Automatic detection of TeaCache support
- Configurable via `enable_tea_cache` parameter
- Transparent integration with existing workflows

### Seed Generation
**Implementation:** `ComfyWorkflowBuilder._create_seed_generator_node()`

**Purpose:** Handles seed generation for reproducible results

**Features:**
- Random seed generation when not specified
- Seed validation and range checking
- Integration with all workflow types

### Enhanced Model Scanner Service

#### ModelScannerService
**Location:** `back/services/model_scanner_service.py`

**Purpose:** Advanced model file discovery and classification with caching and extended metadata extraction capabilities.

**Key Features:**
- **Intelligent Model Classification:** Content-based analysis for accurate model type identification
- **Performance Caching:** Persistent cache system to avoid re-analyzing unchanged files
- **Extended Metadata Extraction:** Comprehensive model information including parameter counts, tensor shapes, and architecture details
- **Extended Format Support:** Support for additional formats including .pkl, .tar, .gz, .zip files
- **Robust Error Handling:** Graceful handling of corrupted or unreadable model files

**Core Methods:**
##### Model Discovery
- `scan_models_directory()` - Main entry point for directory scanning
- `identify_file(file_path)` - Advanced content-based model identification
- `_analyze_model_file(file_path, models_dir)` - Comprehensive file analysis with metadata extraction

##### Cache Management
- `_load_cache()` - Loads cached analysis results from disk
- `_save_cache()` - Persists cache to disk for future use
- `_get_file_hash(file_path)` - Generates unique file identifier for caching
- `_is_cache_valid(file_hash, file_path)` - Validates cache entry freshness
- `clear_cache()` - Removes all cached data
- `get_cache_info()` - Returns cache statistics and information

##### Extended Metadata
- `_extract_extended_metadata(file_path)` - Extracts comprehensive model metadata
- `_extract_safetensors_metadata(file_path)` - SafeTensors-specific metadata extraction
- `_extract_torch_metadata(file_path)` - PyTorch checkpoint metadata extraction
- `_extract_pickle_metadata(file_path)` - Pickle file metadata extraction

**Supported File Formats:**
- `.safetensors`, `.sft` - SafeTensors format (recommended)
- `.ckpt`, `.pt`, `.pth` - PyTorch checkpoint formats
- `.bin` - Binary model files
- `.pkl` - Pickle format files
- `.tar`, `.gz`, `.zip` - Compressed model archives

**Extended Metadata Fields:**
- `total_parameters` - Total number of model parameters
- `total_parameters_millions` - Parameters in millions for readability
- `tensor_count` - Number of tensors in the model
- `tensor_info` - Detailed tensor information (shapes, dtypes)
- `format` - Model file format
- `file_hash` - Unique file identifier
- `created_time`, `modified_time`, `accessed_time` - File timestamps
- `size_mb`, `size_gb` - File sizes in different units

**Model Classification:**
The service uses a multi-stage approach for accurate model classification:

1. **Content Analysis:** Analyzes actual model tensors and keys
2. **Pattern Recognition:** Identifies model architectures by tensor patterns
3. **Directory Fallback:** Uses directory structure when content analysis fails
4. **Filename Heuristics:** Secondary classification based on filenames

**Supported Model Types:**
- `checkpoint` - Full SD models with UNet, CLIP, and VAE
- `diffusion_loader` - UNet models without CLIP/VAE
- `clip` - Text encoders
- `vae` - Variational autoencoders
- `lora` - LoRA adaptation models
- `controlnet` - ControlNet models
- `embedding` - Textual inversions
- `upscale` - Upscaling models
- `hypernetworks` - Hypernetwork models
- `style_models` - Style transfer models

**Cache Performance:**
- Persistent cache stored in `.model_scanner_cache.pkl`
- Cache invalidation based on file modification time
- Significant performance improvement for repeated scans
- Automatic cache cleanup for deleted files

**Usage Example:**
```python
# Scan all models with caching
results = ModelScannerService.scan_models_directory()

# Get detailed model information
models = results["models"]
checkpoints = models["checkpoints"]

# Access extended metadata
for model in checkpoints:
    if "extended_metadata" in model:
        param_count = model["extended_metadata"]["total_parameters_millions"]
        print(f"Model {model['name']} has {param_count}M parameters")

# Cache management
cache_info = ModelScannerService.get_cache_info()
ModelScannerService.clear_cache()  # Clear if needed
```

**Performance Considerations:**
- First scan may take longer due to content analysis
- Subsequent scans are significantly faster with cache
- Cache automatically invalidates when files are modified
- Large models may require substantial memory for analysis

**Error Handling:**
- Graceful handling of corrupted model files
- Fallback classification when content analysis fails
- Detailed error logging for debugging
- Continues processing even if individual files fail

## Testing

### Test Structure
**Location:** `back/tests/`

**Test Files:**
- `test_comfy_workflow_builder.py` - Main workflow builder tests
- `test_model_loaders.py` - Model loader factory tests
- `test_routers/` - API endpoint tests
- `test_services/` - Service layer tests

### Running Tests
```bash
# Run all tests
pytest back/tests/ -v

# Run specific test file
pytest back/tests/test_comfy_workflow_builder.py -v

# Run with coverage
pytest back/tests/ --cov=back --cov-report=html -v
```

## Best Practices

### Error Handling
- Use try/catch blocks for all async operations
- Implement proper error boundaries
- Log errors with contextual information
- Return meaningful error messages to frontend

### Code Organization
- Follow separation of concerns
- Use dependency injection where appropriate
- Implement proper abstraction layers
- Maintain clean interfaces between components

### Performance
- Use async/await for I/O operations
- Implement proper caching strategies
- Optimize database queries
- Use background tasks for long-running operations

## Development Guidelines

### Adding New Model Types
1. Create new model loader class extending `BaseModelLoader`
2. Implement required abstract methods
3. Register loader with `ModelLoaderFactory`
4. Add corresponding tests
5. Update documentation

### API Development
1. Follow RESTful conventions
2. Use appropriate HTTP status codes
3. Implement proper request/response validation
4. Add comprehensive error handling
5. Include API documentation

### Testing Requirements
- Unit tests for all service methods
- Integration tests for API endpoints
- Test coverage above 80%
- Mock external dependencies
- Test error scenarios

## Configuration

### Environment Variables
- `BASE_DIR` - ComfyUI installation directory
- `HF_TOKEN` - HuggingFace API token
- `CIVITAI_TOKEN` - CivitAI API token
- `LOG_LEVEL` - Application log level
- `DEBUG` - Debug mode flag

### Model Configuration
Models are configured via JSON files in the `models/` directory:
```json
{
  "model_key": "flux-dev",
  "model_type": "flux",
  "model_path": "models/unet/flux-dev.safetensors",
  "clip_path": "models/clip/flux-clip.safetensors",
  "vae_path": "models/vae/flux-vae.safetensors"
}
```

This documentation provides a comprehensive overview of the backend architecture and implementation details for the ComfyUI Model Manager application.
