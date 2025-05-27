# ComfyUI Model & Bundle Manager

A comprehensive web application for managing ComfyUI models, workflows, and bundles with a FastAPI backend and Vue.js frontend.

## Features

### 🔐 Authentication System
- JWT-based authentication
- User login/logout functionality
- Password-protected API endpoints
- User credential management

### 📦 Model Management
- **Model Groups**: Organize models into logical groups (Flux, SDXL, Upscale, etc.)
- **Model Entries**: Track individual models with metadata:
  - Download URLs (HTTP/HTTPS)
  - Git repositories
  - Destination paths
  - Model types and tags
  - File hashes and sizes
  - Custom headers for downloads
- **Download Management**:
  - Background downloads with progress tracking
  - Support for HuggingFace and CivitAI tokens
  - Download pause/resume functionality
  - Concurrent download support
  - Automatic directory creation

### 🛠️ Workflow Management
- Upload ComfyUI workflow JSON files
- List and browse available workflows
- Download workflow files
- Integration with bundle system
- Automatic workflow deployment to ComfyUI

### 📋 Bundle System
- **Bundle Creation**: Package models and workflows together
- **Hardware Profiles**: Different configurations for various hardware setups
  - Tag-based model filtering (include/exclude tags)
  - Custom model definitions per profile
- **Bundle Operations**:
  - Install/uninstall bundles
  - Export bundles as ZIP files
  - Import bundles from ZIP files
  - Duplicate existing bundles
  - Track installed bundles
- **Smart Installation**:
  - Dependency resolution
  - Avoid duplicate downloads
  - Background installation process
  - Installation progress tracking

### 🗃️ File Management
- **Directory Structure**: Organized file hierarchy
  - `${BASE_DIR}/models/` - Model files
  - `${BASE_DIR}/user/default/workflows/` - Workflow files
  - `${BASE_DIR}/bundles/` - Bundle packages
- **Path Resolution**: Automatic `${BASE_DIR}` variable substitution
- **File Operations**: Upload, download, delete files
- **Storage Management**: Track disk usage and file sizes

### ⚙️ Configuration Management
- **Base Directory**: Configurable root directory for all files
- **API Tokens**: Secure storage of HuggingFace and CivitAI tokens
- **Environment Variables**: Support for `.env` file configuration
- **Dynamic Configuration**: Runtime configuration updates

### 🌐 API Architecture
- **RESTful API**: Well-structured REST endpoints
- **Route Modules**:
  - `/api/auth` - Authentication
  - `/api/models` - Model management
  - `/api/bundles` - Bundle operations
  - `/api/workflows` - Workflow management
  - `/api/files` - File operations
- **Request/Response Models**: Pydantic-based data validation
- **Error Handling**: Comprehensive error responses
- **CORS Support**: Frontend integration ready

## Project Structure

```
f:\runpod-comfyui\
├── main.py                 # FastAPI application entry point
├── api.py                  # Core API routes and authentication
├── api_models.py          # Model management API
├── api_bundle.py          # Bundle management API
├── api_workflows.py       # Workflow management API
├── api_file_manager.py    # File operations API
├── model_utils.py         # Model utilities and download manager
├── auth.py                # Authentication utilities
├── models.json            # Model definitions and configuration
├── front/                 # Vue.js frontend application
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── composables/   # Vue composables
│   │   └── main.js        # Frontend entry point
└── README.md              # This file
```

## Key Components

### DownloadManager
Centralized download management with:
- Progress tracking for all downloads
- Support for HTTP and Git downloads
- Token-based authentication for private repositories
- Background processing with thread safety
- Download cancellation capabilities

### ModelManager
Utility class providing:
- Path resolution and normalization
- Model existence checking
- Configuration management
- Directory structure management
- Cross-platform file operations

### Bundle System
Comprehensive bundle management:
- JSON schema validation
- ZIP-based bundle packaging
- Hardware profile support
- Dependency tracking
- Installation state management

## Supported Model Sources

### Direct Downloads
- **HuggingFace**: Models from Hugging Face Hub
- **CivitAI**: Models from CivitAI marketplace
- **Direct URLs**: Any HTTP/HTTPS downloadable file

### Git Repositories
- **GitHub**: Public and private repositories
- **GitLab**: Git-based model repositories
- **Custom Git**: Any Git-accessible repository

### Model Types Supported
- **Checkpoints**: Base diffusion models
- **LoRA**: Low-Rank Adaptation models
- **VAE**: Variational Autoencoders
- **ControlNet**: Control networks
- **Upscalers**: Image upscaling models
- **Text Encoders**: CLIP and T5 encoders
- **Custom Nodes**: ComfyUI extensions

## Hardware Profiles

### Predefined Profiles
- **High-End**: Full precision models (fp16/fp32)
- **Mid-Range**: Optimized models (fp8, quantized)
- **Low-End**: Highly compressed models (GGUF, Q4)
- **Custom**: User-defined configurations

### Model Selection System
- **Direct Model Storage**: Models are directly stored in bundle JSON with full metadata
- **Profile-Specific Models**: Each hardware profile contains its specific model list
- **Model Metadata**: Complete model information including:
  - Download URLs and destinations
  - Model types and tags
  - File sizes and hashes
  - Git repository information
- **Examples**:
  - High-End Profile: Full fp16 SDXL models, high-quality LoRAs
  - Low-End Profile: Quantized models, compressed checkpoints
  - Custom Profile: User-selected models for specific workflows

### Bundle Model Management
- **Visual Model Selection**: Interactive UI for choosing models from available groups
- **Tag-Based Filtering**: Filter available models by tags during selection
- **Model Validation**: Automatic validation of model definitions
- **Dependency Tracking**: Track which models are used by which profiles

## Installation States

### Bundle Tracking
- **Installed Bundles**: Track which bundles are installed
- **Installation Profiles**: Remember which profile was used
- **Installation Timestamps**: Track when bundles were installed
- **Dependency Management**: Prevent deletion of shared resources

### Smart Uninstallation
- **Dependency Checking**: Only remove unused files
- **Shared Resource Protection**: Keep files used by other bundles
- **Clean Removal**: Remove unused workflows and models

## Security Features

### Token Management
- **Secure Storage**: API tokens stored in `.env` files
- **Automatic Injection**: Tokens automatically added to requests
- **Scope Isolation**: Tokens only used for appropriate services

### Access Control
- **Authentication Required**: All API endpoints require authentication
- **JWT Tokens**: Secure session management
- **Protected Routes**: Frontend route protection

## Development Features

### Logging & Monitoring
- **Comprehensive Logging**: Detailed operation logs
- **Progress Tracking**: Real-time download progress
- **Error Reporting**: Detailed error messages and stack traces
- **Performance Monitoring**: Download speeds and completion times

### Extensibility
- **Modular Architecture**: Easy to add new model sources
- **Plugin System**: Support for custom model types
- **Configuration Driven**: Behavior controlled via JSON configuration
- **API First**: All functionality available via REST API

## Use Cases

### Content Creators
- Quick setup of ComfyUI with required models
- Hardware-appropriate model selection
- Workflow sharing and distribution
- Batch model installation

### Researchers
- Model collection management
- Experiment reproducibility
- Custom model organization
- Version control for model sets

### Developers
- Automated ComfyUI deployment
- Model dependency management
- Custom bundle creation
- Integration with existing workflows

### System Administrators
- Centralized model management
- Storage optimization
- User access control
- Resource monitoring

## Configuration

### Environment Variables
- `BASE_DIR`: Root directory for all files
- `COMFYUI_MODEL_DIR`: Alternative base directory
- `HF_TOKEN`: HuggingFace API token
- `CIVITAI_TOKEN`: CivitAI API token

### Runtime Configuration
All configuration can be modified through the web interface without server restart.

## API Documentation

The application provides comprehensive REST API endpoints for all functionality. Each endpoint includes:
- **Request/Response Examples**: Complete API documentation
- **Error Codes**: Detailed error handling
- **Authentication**: Required token information
- **Parameters**: Complete parameter documentation

For detailed API documentation, run the application and visit `/docs` for the interactive Swagger documentation.