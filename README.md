## Components

### ModelSelectorModal.vue

- **Location:** `/front/src/components/common/ModelSelectorModal.vue`
- **Goal:** Provide a reusable, filterable modal for model selection, usable in any part of the application where model selection is needed.
- **Test file:** `/back/tests/test_model_selector_modal.spec.js`

This component allows users to select models for a profile, with tag-based filtering and grouping. It emits events for closing and applying the selection.

### InstallProgressIndicator.stories.js
- **Location:** `/front/src/stories/InstallProgressIndicator.stories.js`
- **Goal:** Storybook stories for the InstallProgressIndicator component, demonstrating its different states (idle, in-progress, completed, error) for UI development and testing.
- **Test file:** `/front/src/stories/InstallProgressIndicator.spec.js`

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

### ⚡ ComfyUI Integration
- **Workflow Generation**: Dynamically generate ComfyUI workflows from parameters
  - Support for multiple model types (SDXL, Flux, HiDream, etc.)
  - **Factory Pattern Architecture**: Extensible model loader system
    - Easy addition of new model types without code modification
    - Consistent interface for all model loaders
    - Clean separation of concerns for different model architectures
  - LoRA integration with configurable strengths
  - ControlNet support with preprocessors
  - Image-to-image workflows with initialization images
  - Inpainting and outpainting capabilities
- **Workflow Execution**: Direct integration with ComfyUI server
  - Send workflows to ComfyUI for processing
  - Real-time execution status monitoring
  - Background execution with progress tracking
  - Automatic result retrieval
  - Query execution results by prompt ID
  - Access generated images and execution history
- **Model Registry**: Centralized model configuration
  - Pre-configured model definitions
  - Support for checkpoint, diffusers, flux, and hidream models
  - Automatic model loader selection via Factory pattern
- **Advanced Features**:
  - Combination workflows (generate and execute in one call)
  - ComfyUI server status monitoring
  - Error handling and timeout management
  - WebSocket support for live previews
  - **Extensible Architecture**: Add custom model loaders at runtime

### 🎨 ComfyUI Image Generation
- **Interactive Generation Interface**: Full-featured UI for creating images with ComfyUI
- **Real-time Preview**: Live preview of generation progress via WebSocket
- **Model Support**: Support for multiple model types (Flux, SDXL, HiDream, etc.)
- **Advanced Parameters**: 
  - Samplers, steps, CFG scale configuration
  - LoRA integration support
  - ControlNet and Image-to-Image workflows
  - Optimization settings (TeaCache, memory management)
- **Workflow Management**: Automatic workflow generation based on parameters
- **Result Management**: Download and preview generated images
- **Server Integration**: Direct communication with ComfyUI backend

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

### 🔍 Model Scanner & Discovery
- **Automatic Model Detection**: Scans the models directory to discover all available model files
- **Smart Categorization**: Automatically categorizes models by type:
  - **Checkpoints**: Full model checkpoints and diffusion models
  - **VAE**: Variational Autoencoders for image encoding/decoding
  - **CLIP**: Text encoders for prompt understanding
  - **ControlNet**: Models for guided generation control
  - **LoRA**: Low-Rank Adaptation models for fine-tuning
  - **Embeddings**: Text embeddings and textual inversions
  - **Upscale Models**: Models for image resolution enhancement
  - **Other Categories**: Hypernetworks, style models, UNet architectures
- **File Format Support**: Supports all major model formats:
  - `.safetensors` - SafeTensors format (recommended)
  - `.sft` - SafeTensors shortened extension
  - `.ckpt` - Legacy checkpoint format
  - `.pt`, `.pth` - PyTorch formats
  - `.bin` - Binary model format
- **Model Information**: Provides detailed metadata for each model:
  - File size and location
  - Model type classification
  - Compatibility information
  - Directory organization
- **Search & Filter**: Advanced search capabilities:
  - Search by model name or path
  - Filter by model category
  - Quick model discovery
- **Statistics & Summary**: Overview of model collection:
  - Total models by category
  - Disk usage statistics
  - Storage optimization insights

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
  - `/api/models/scanner` - Model discovery and scanning
  - `/api/bundles` - Bundle operations
  - `/api/workflows` - Workflow management
  - `/api/comfy` - ComfyUI workflow generation and execution
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
│   │   │   ├── common/
│   │   │   │   ├── ButtonDropdownComponent.vue   # Split button with dropdown (main action + dropdown menu)
│   │   ├── composables/   # Vue composables
│   │   └── main.js        # Frontend entry point
└── README.md              # This file
```

## Installation & Setup

### Prerequisites

- **Python 3.8+**: Required for the FastAPI backend
- **Node.js 16+**: Required for the Vue.js frontend
- **Git**: For cloning repositories and downloading Git-based models

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd runpod-comfyui
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory:
   ```env
   # Base directory for all model files (required)
   BASE_DIR=C:\ComfyUI
   
   # Optional: Alternative base directory
   COMFYUI_MODEL_DIR=C:\ComfyUI
   
   # API tokens for authenticated downloads (optional)
   HF_TOKEN=your_huggingface_token_here
   CIVITAI_TOKEN=your_civitai_token_here 
   ```

5. **Initialize the models configuration:**
   Create or modify `models.json` with your model definitions:
   ```json
   {
     "groups": {
       "Flux": [
         {
           "url": "https://huggingface.co/black-forest-labs/FLUX.1-dev",
           "dest": "models/checkpoints/flux1-dev.safetensors",
           "type": "checkpoint",
           "tags": ["flux", "base", "fp16"]
         }
       ]
     }
   }
   ```

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd front
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Build the frontend for production:**
   ```bash
   npm run build
   ```

## Running the Application

### Development Mode

1. **Start the backend server:**
   ```bash
   # From the root directory
   python main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the frontend development server:**
   ```bash
   # In a separate terminal, from the front/ directory
   cd front
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

### Production Mode

1. **Build the frontend:**
   ```bash
   cd front
   npm run build
   ```

2. **Start the production server:**
   ```bash
   # From the root directory
   python main.py
   ```
   The application will be available at `http://localhost:8000`

### Docker Setup (Optional)

Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git nodejs npm

# Copy backend files
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy frontend files and build
COPY front/ ./front/
WORKDIR /app/front
RUN npm install && npm run build

# Copy backend source
WORKDIR /app
COPY . .

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "main.py"]
```

## Initial Configuration

### First-Time Setup

1. **Access the application:**
   Open your browser and navigate to `http://localhost:8000`

2. **Login with default credentials:**
   - Username: `admin`
   - Password: `admin`

3. **Configure base directory:**
   - Go to the Models section
   - Set your ComfyUI installation path in the configuration

4. **Add API tokens (optional):**
   - Navigate to the configuration section
   - Add your HuggingFace and CivitAI tokens for authenticated downloads

### Directory Structure Setup

The application will automatically create the following directory structure in your `BASE_DIR`:

```
${BASE_DIR}/
├── models/                    # Model files organized by type
│   ├── checkpoints/          # Base diffusion models
│   ├── loras/               # LoRA models
│   ├── vae/                 # VAE models
│   ├── controlnet/          # ControlNet models
│   └── upscale_models/      # Upscaler models
├── user/default/workflows/   # Workflow JSON files
├── bundles/                 # Bundle packages
└── ComfyUI/                 # ComfyUI installation (if applicable)
    └── workflows/           # ComfyUI workflow deployment
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Change the port in main.py or kill the process
   netstat -ano | findstr :8000
   taskkill /PID <process_id> /F
   ```

2. **Permission errors:**
   - Ensure the `BASE_DIR` has write permissions
   - Run as administrator on Windows if needed

3. **Module not found errors:**
   - Verify virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **Frontend build errors:**
   - Clear npm cache: `npm cache clean --force`
   - Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

### Logs and Debugging

- Backend logs are displayed in the console where you run `python main.py`
- Frontend build logs are shown during the `npm run build` process
- API documentation is available at `http://localhost:8000/docs`

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

## 🧪 Testing & Development

### Running Tests

The project includes comprehensive test suites for all components.

#### Quick Test Scripts
```bash
# Windows - Tests des routers
run_router_tests.bat

# Windows - Tous les tests avec couverture
run_all_tests.bat

# Linux/Mac - Tests des routers
chmod +x run_router_tests.sh && ./run_router_tests.sh
```

#### Manual Testing Commands
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest back/tests/ -v

# Run specific test categories
pytest back/tests/routers/ -v      # API endpoint tests
pytest back/tests/services/ -v     # Business logic tests

# Run with code coverage
pytest back/tests/ --cov=back --cov-report=html

# Test specific functionality
pytest back/tests/ -k "comfy" -v   # ComfyUI related tests
pytest back/tests/ -k "auth" -v    # Authentication tests
```

#### Test Structure
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing with mocked dependencies
- **Service Tests**: Business logic validation
- **Router Tests**: HTTP endpoint testing

See [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) for detailed testing instructions.

### Development Setup

1. **Install development dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-asyncio pytest-cov
   ```

2. **Set up environment variables:**
   ```bash
   # Windows
   set PYTHONPATH=%PYTHONPATH%;%CD%
   
   # Linux/Mac
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

3. **Run tests before development:**
   ```bash
   pytest back/tests/ -v
   ```

4. **Code quality checks:**
   ```bash
   # Check imports and code quality
   python -m py_compile back/routers/*.py
   python -m py_compile back/services/*.py
   ```

## API Documentation

The application provides comprehensive REST API endpoints for all functionality. Each endpoint includes:
- **Request/Response Examples**: Complete API documentation
- **Error Codes**: Detailed error handling
- **Authentication**: Required token information
- **Parameters**: Complete parameter documentation

For detailed API documentation, run the application and visit `/docs` for the interactive Swagger documentation.

## Components

### ButtonDropdownComponent
A split button Vue component: left side is a normal button (main action), right side is a dropdown toggle with chevron. The dropdown content is customizable via slot. Used for actions that have a primary action and additional options (e.g., install, add, etc.).

### ComfyUIView.vue

- **Location:** `/front/src/views/ComfyUIView.vue`
- **Goal:** Provide a comprehensive interface for ComfyUI image generation with real-time preview and parameter configuration.
- **Test file:** `/front/src/views/__tests__/ComfyUIView.spec.ts`

This component serves as the main interface for ComfyUI integration, featuring:
- Collapsible parameter form (1/3 of screen)
- Real-time preview during generation
- Model and parameter selection
- WebSocket integration for live updates
- Result gallery with download functionality

### ComfyUI Store (comfyui.ts)

- **Location:** `/front/src/stores/comfyui.ts`
- **Goal:** Centralized state management for ComfyUI operations including models, generation state, and API communication.
- **Test file:** `/front/src/stores/comfyui.test.ts`

This Pinia store manages:
- Model registry and available models
- Generation parameters and workflow state
- Real-time generation status
- API communication with backend
- Error handling and server status

### ComfyUI Types (comfyui.types.ts)

- **Location:** `/front/src/stores/types/comfyui.types.ts`
- **Goal:** TypeScript interfaces and types for ComfyUI integration, ensuring type safety across the application.

Defines interfaces for:
- Generation parameters and LoRA configuration
- API responses and workflow definitions
- Store state and form validation
- Model registry and options