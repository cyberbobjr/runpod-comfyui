# Documentation

This directory contains the consolidated documentation for the ComfyUI Model Manager project.

## Documentation Structure

### Core Documentation Files

- **`BACKEND_DOCUMENTATION.md`** - Complete backend documentation
  - Architecture overview
  - API endpoints and services
  - Data models and utilities
  - Development guidelines
  - Testing strategies

- **`FRONTEND_DOCUMENTATION.md`** - Complete frontend documentation
  - Vue.js architecture
  - Components and state management
  - Type definitions
  - UI/UX guidelines
  - Development best practices

- **`VERSION_MANAGEMENT.md`** - Version management system
  - Semantic versioning guidelines
  - Version update procedures
  - API version information

## Documentation Maintenance

### Consolidation Process

The documentation has been consolidated from multiple separate files into these comprehensive guides:

**Previously removed files:**
- `API_CONFIG_GUIDE.md`
- `API_REFACTORING_SUMMARY.md`
- `COMFYUI_GENERATOR_GUIDE.md`
- `COMFYUI_IMPLEMENTATION_SUMMARY.md`
- `COMFY_WORKFLOW_EXAMPLES.md`
- `CORRECTIONS_SUMMARY.md`
- `FACTORY_PATTERN_GUIDE.md`
- `FACTORY_PATTERN_REFACTORING.md`
- `INPAINT_MODEL_CONDITIONING_GUIDE.md`
- `INPAINT_MODEL_CONDITIONING_IMPLEMENTATION.md`
- `REFACTORING_SUMMARY.md`
- `TESTING_GUIDE.md`
- `TODO_CORRECTIONS_SUMMARY.md`

### Guidelines for Updates

When updating documentation:

1. **Backend changes** → Update `BACKEND_DOCUMENTATION.md`
2. **Frontend changes** → Update `FRONTEND_DOCUMENTATION.md`
3. **Version changes** → Update `VERSION_MANAGEMENT.md`
4. **New features** → Add to appropriate documentation file
5. **API changes** → Update both backend and frontend docs as needed

### Documentation Standards

- Use English for all documentation
- Follow the project's coding standards for examples
- Include code examples where appropriate
- Keep documentation synchronized with actual code
- Remove outdated information during updates
- Use clear section headers and consistent formatting

## Development References

For specific development tasks, refer to:

- **API Development** → `BACKEND_DOCUMENTATION.md` → API Routers section
- **Component Development** → `FRONTEND_DOCUMENTATION.md` → Components section
- **Testing** → Both files have testing sections
- **Configuration** → Both files have configuration sections
- **Version Updates** → `VERSION_MANAGEMENT.md`

## Project Overview

This project is a comprehensive ComfyUI Model Manager with:

- **Backend**: FastAPI with Python, providing workflow generation and model management
- **Frontend**: Vue.js 3 with TypeScript, offering a modern user interface
- **Integration**: Real-time WebSocket communication for live updates
- **Features**: Model management, workflow generation, bundle handling, and authentication

For the complete project structure and features, refer to the main `README.md` file in the project root.
