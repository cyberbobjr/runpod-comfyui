# Backend Architecture

This directory contains the backend modules for the ComfyUI Model Manager, following a clean architecture pattern.

## 🏗️ Architecture Overview

The backend has been refactored from monolithic `api_*.py` files into a clean, modular architecture:

```
back/
├── routers/           # API route definitions (FastAPI routers)
├── services/          # Business logic and core operations  
├── models/            # Pydantic models and data structures
├── tests/             # Unit tests for all modules
└── [legacy files]     # Deprecated api_*.py files (for compatibility)
```

## 📁 Directory Structure

### 🛣️ Routers (`/routers/`)
Contains all API route definitions, delegating business logic to services:

- **`main.py`** - Main API router combining all sub-routers
- **`auth_router.py`** - Authentication routes (login, password change)
- **`token_router.py`** - Token management routes (HuggingFace, CivitAI)
- **`download_router.py`** - Model download management routes
- **`model_router.py`** - Model operations routes
- **`model_groups_router.py`** - Model group management routes
- **`model_entries_router.py`** - Model entry management routes
- **`bundle_router.py`** - Bundle management routes
- **`file_manager_router.py`** - File system operations routes
- **`json_models_router.py`** - JSON model configuration routes
- **`workflow_router.py`** - Workflow management routes
- **`comfy_router.py`** - ComfyUI workflow generation and execution routes

### ⚙️ Services (`/services/`)
Contains all business logic and core operations:

- **`auth_service.py`** - Authentication and user management
- **`auth_middleware.py`** - Authentication middleware and protection
- **`token_service.py`** - External API token management
- **`download_service.py`** - Download operations and progress tracking
- **`model_service.py`** - Model file operations
- **`model_management_service.py`** - Advanced model group/entry management
- **`bundle_service.py`** - Bundle creation, installation, and management
- **`file_manager_service.py`** - File system operations with security
- **`json_models_service.py`** - JSON model configuration and validation
- **`workflow_service.py`** - Workflow file management and validation
- **`comfy_workflow_builder.py`** - ComfyUI workflow generation with Factory pattern for model loaders
  - **Factory Pattern**: Extensible model loader system for different model types
  - **BaseModelLoader**: Abstract base class for all model loaders
  - **CheckpointModelLoader**: Handles SDXL, SD1.5 checkpoint models
  - **FluxModelLoader**: Handles Flux models with separate UNet, CLIP, VAE loaders
  - **HiDreamModelLoader**: Handles HiDream models with QuadrupleCLIP support
  - **ModelLoaderFactory**: Manages registration and creation of model loaders
  - **Easy Extension**: Add new model types by implementing BaseModelLoader
- **`comfy_client.py`** - ComfyUI server communication and execution client

### 📊 Models (`/models/`)
Contains all Pydantic models for request/response validation:

- **`model_models.py`** - Model-related data structures
- **`bundle_models.py`** - Bundle-related data structures
- **`file_models.py`** - File management data structures
- **`json_models.py`** - JSON model configuration structures
- **`workflow_models.py`** - Workflow management structures

### 🧪 Tests (`/tests/`)
Contains unit tests for all modules:

- **`services/`** - Tests for service layer
- **`routers/`** - Tests for API routes
- **`test_download_manager.py`** - Unit tests for DownloadManager (mocked HTTP/HTTPS requests, file skipping, progress reporting)

### 🏛️ Core Modules

- **`download_manager.py`** - Handles model downloads with progress tracking
- **`model_manager.py`** - Manages model configurations and file paths
- **`version.py`** - Version management and information

## 🔄 Migration from Legacy API Files

All original `api_*.py` files have been refactored:

| Legacy File | New Structure |
|-------------|---------------|
| `api_auth.py` | → `routers/auth_router.py` + `services/auth_service.py` |
| `api_models.py` | → `routers/model_*_router.py` + `services/model_*_service.py` |
| `api_bundle.py` | → `routers/bundle_router.py` + `services/bundle_service.py` |
| `api_file_manager.py` | → `routers/file_manager_router.py` + `services/file_manager_service.py` |
| `api_json_models.py` | → `routers/json_models_router.py` + `services/json_models_service.py` |
| `api_workflows.py` | → `routers/workflow_router.py` + `services/workflow_service.py` |

### Backward Compatibility

Legacy `api_*.py` files are deprecated but still present for backward compatibility:
- Issue deprecation warnings when imported
- Redirect to new router implementations where possible
- Will be removed in future versions

## 🎯 Benefits of New Architecture

1. **Separation of Concerns**: Routes only handle HTTP concerns, business logic in services
2. **Testability**: Each layer can be tested independently
3. **Maintainability**: Smaller, focused modules are easier to understand and modify
4. **Reusability**: Services can be used by multiple routers or other components
5. **Type Safety**: Comprehensive Pydantic models for all data structures
6. **Extensibility**: Factory pattern enables easy addition of new model types
7. **Clean Dependencies**: Clear separation between API layer and business logic
6. **Documentation**: Each method is documented with purpose, parameters, and returns

## 🚀 Usage

Import the main router in your FastAPI application:

```python
from back.routers.main import api_router

app = FastAPI()
app.include_router(api_router)
```

## 🧪 Testing

Run tests for the new architecture:

### Quick Start (Scripts automatiques)

**Windows:**
```batch
# Tests des routers uniquement
run_router_tests.bat

# Tous les tests avec couverture
run_all_tests.bat
```

**Linux/Mac:**
```bash
# Tests des routers uniquement
chmod +x run_router_tests.sh
./run_router_tests.sh

# Tous les tests
pytest back/tests/ -v
```

### Commandes pytest détaillées

```bash
# Tous les tests
pytest back/tests/ -v

# Tests spécifiques par module
pytest back/tests/services/ -v
pytest back/tests/routers/ -v

# Test d'un fichier spécifique
pytest back/tests/routers/test_comfy_router.py -v

# Tests avec couverture de code
pytest back/tests/ --cov=back --cov-report=html

# Tests en mode debug
pytest back/tests/routers/test_comfy_router.py -v -s

# Filtrer les tests par nom
pytest back/tests/ -k "comfy" -v
```

### Configuration requise

Assurez-vous d'avoir installé les dépendances de test :
```bash
pip install pytest pytest-asyncio pytest-cov
```

Et ajouté le PYTHONPATH :
```bash
# Windows
set PYTHONPATH=%PYTHONPATH%;%CD%

# Linux/Mac
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

Voir [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) pour plus de détails.

## 📋 Standards

All new code follows these standards:

- **Documentation**: Each method documented with purpose, parameters, and returns
- **Type Hints**: Full type annotations for all functions and methods
- **Error Handling**: Proper exception handling with meaningful error messages
- **Testing**: Unit tests for all new functionality
- **Validation**: Pydantic models for all data structures

All modules use relative imports:
```python
from .model_manager import ModelManager
from .download_manager import DownloadManager
from back.routers.main import api_router
from back.services.auth_service import AuthService
```

## Usage

The main application (`main.py`) imports from the backend package:
```python
from back.routers.main import api_router
from back.services.auth_service import AuthService
from back.model_manager import ModelManager
# etc.
```
