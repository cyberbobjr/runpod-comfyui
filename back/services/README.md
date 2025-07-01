# Services Architecture Documentation

## Overview
This document outlines the service architecture following the Single Responsibility Principle (SRP) and identifies the responsibilities of each service.

## Service Responsibilities

### Core Services

#### ConfigService
**Responsibility:** Configuration management and validation
- Loading and saving user configuration files
- Managing configuration paths and directories  
- Configuration validation and defaults
- Environment variable resolution

#### ModelManager
**Responsibility:** Model configuration management and basic file operations
- Loading and caching models.json configuration
- Path resolution and file system operations
- Model existence validation
- Git repository cloning
- Basic model installation workflows

#### DownloadManager  
**Responsibility:** Download execution and progress management
- Progress tracking for concurrent downloads
- HTTP/HTTPS file downloads with authentication
- Git repository cloning operations
- Download cancellation and cleanup
- Cleanup of finished downloads

### High-Level Services

#### ModelService
**Responsibility:** User-facing model information queries
- Simple model listing with basic status
- Model existence checking
- Basic model metadata operations
- User-friendly model queries

#### ModelManagementService
**Responsibility:** Complex model management operations and state coordination
- Complete model data with download progress integration
- Model group management and manipulation
- Advanced model entry operations (add/edit/delete)
- Model installation coordination
- Model status aggregation with download progress

#### DownloadService
**Responsibility:** User-facing download coordination and API
- Download initiation with authentication
- Download progress monitoring
- Download cancellation and cleanup
- Token management integration
- Clean API facade over DownloadManager

#### BundleService
**Responsibility:** Bundle operations and workflow coordination
- Bundle creation, installation, and export
- Bundle metadata management
- Hardware profile filtering
- Bundle validation and schema enforcement
- Bundle lifecycle management (install/uninstall)

### Specialized Services

#### AuthService
**Responsibility:** User authentication and authorization
- User credential management (create, verify, update)
- Password hashing and validation
- JWT token generation and validation
- User session management
- Authentication state persistence

#### TokenService
**Responsibility:** External API token management
- HuggingFace token management
- CivitAI token management
- Environment file operations (.env)
- Token validation and persistence
- Secure token storage and retrieval

#### WorkflowService
**Responsibility:** Workflow file operations and validation
- Workflow file listing and metadata extraction
- Workflow upload and download operations
- Workflow validation and JSON parsing
- Workflow file management (create, delete, copy)
- ComfyUI workflow integration

#### FileManagerService
**Responsibility:** Secure file system operations and file management
- Directory listing and navigation with security checks
- File operations (copy, move, delete, rename)
- File upload and download handling
- Model file registration and tracking
- File system integrity and security validation

#### JsonModelsService
**Responsibility:** JSON model configuration management and validation
- Model configuration normalization and validation
- Path normalization and resolution
- Model group ordering and organization
- Model existence checking and status tracking
- Configuration file structure management

## Service Dependencies

```
High-Level Services
├── ModelService → ModelManager
├── ModelManagementService → ModelManager, DownloadManager
├── DownloadService → DownloadManager, TokenService
└── BundleService → ModelManager, DownloadManager

Core Services
├── ModelManager → ConfigService
├── DownloadManager → ModelManager
└── ConfigService (no dependencies)

Specialized Services
├── AuthService → ConfigService
├── TokenService → ConfigService
├── WorkflowService → ConfigService, ModelManager
├── FileManagerService → ConfigService, ModelManager
└── JsonModelsService → ConfigService, ModelManager
```

## Architectural Principles

### Single Responsibility Principle (SRP)
Each service has a single, well-defined responsibility and should not be modified for more than one reason.

### Dependency Direction
- High-level services depend on core services
- Core services have minimal dependencies
- Specialized services depend on core services but not on each other

### Separation of Concerns
- **ModelManager**: Low-level model operations
- **DownloadManager**: Low-level download mechanics
- **ModelService/ModelManagementService**: High-level model coordination
- **DownloadService**: High-level download coordination
- **BundleService**: High-level bundle orchestration

## Identified Issues and Recommendations

### Potential Redundancies
1. **ModelService vs ModelManagementService**: Consider consolidating or clearly separating use cases
2. **DownloadService vs DownloadManager**: DownloadService acts as a facade - ensure clear API boundaries

### Import Corrections Made
- All services now import from relative paths within the services directory
- Removed circular import issues
- Consolidated duplicate files between `back/` and `back/services/`

### Future Improvements
1. Consider extracting Pydantic models from `models.py` to a separate `models/` directory
2. Add interface definitions for better service contracts
3. Consider dependency injection for better testability
4. Add service-level error handling and logging standards
