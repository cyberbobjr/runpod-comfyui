# Changelog

## [v2.2.0] - 2025-07-01

### Minor Release
- Minor release with new features
- Build: 20250701-1551



All notable changes to this project will be documented in this file.

## [v2.0.0] - Configuration and Settings Management Refactoring

### 🚀 Major Features

#### Configuration Management Overhaul
- **NEW:** Cascading BASE_DIR configuration system with priority order:
  1. `BASE_DIR` environment variable (highest priority)
  2. Custom `config.json` file (user-created, git-resistant)
  3. `models.json` config.BASE_DIR value (project default)
  4. `COMFYUI_MODEL_DIR` environment variable
  5. Current directory (fallback)

#### Settings Page Redesign
- **NEW:** Comprehensive settings page (`SettingsComponent.vue`) replacing the old password change component
- **NEW:** Organized accordion-based interface for better UX
- **NEW:** BASE_DIR management moved from JSON editor to dedicated settings
- **NEW:** API token management (HuggingFace & CivitAI) in settings
- **NEW:** Password change functionality with enhanced security

#### Reusable UI Components
- **NEW:** `AccordionComponent.vue` - Reusable accordion component with icons and visual linking
- Applied accordion component across JSON editor and settings for consistent UI

### 🔧 Backend Improvements

#### API Enhancements
- **UPDATED:** `/api/jsonmodels/config` endpoint now provides source information
- **UPDATED:** Configuration API now saves to user-specific `config.json` instead of `models.json`
- **IMPROVED:** BASE_DIR resolution logic in `ModelManager` class
- **NEW:** User configuration management methods in `ModelManager`
- **REMOVED:** Duplicate config routes from `/api/models/` (consolidated to `/api/jsonmodels/`)

#### Code Organization
- **IMPROVED:** Better separation of concerns between API modules
- **UPDATED:** Centralized BASE_DIR management in `model_utils.py`
- **ENHANCED:** Error handling and logging throughout backend
- **STANDARDIZED:** English comments and documentation throughout codebase

### 🎨 Frontend Improvements

#### Component Refactoring
- **REFACTORED:** `JsonEditorComponent.vue` - Removed BASE_DIR management, replaced custom accordions
- **DELETED:** `ChangePasswordComponent.vue` (functionality moved to settings)
- **NEW:** `SettingsComponent.vue` - Comprehensive settings management
- **NEW:** `AccordionComponent.vue` - Reusable accordion with enhanced visual design

#### UI/UX Enhancements
- **STANDARDIZED:** All action buttons now use `btn-primary` class consistently
- **IMPROVED:** Visual linking between accordion headers and content
- **ENHANCED:** Form validation and error handling in settings
- **UPDATED:** Router configuration to use new settings component

#### API Integration
- **UPDATED:** API base URL corrected from 8082 to 8081
- **IMPROVED:** Token management with read/write functionality
- **ENHANCED:** Configuration loading and error handling

### 📚 Documentation & Development

#### New Documentation
- **NEW:** `CONFIG_DOCUMENTATION.md` - Comprehensive configuration guide
- **NEW:** `config.json.example` - Example configuration file
- **NEW:** GitHub instructions for coding standards:
  - `generalcoding.instructions.md`
  - `python.instructions.md`
  - `vuejs.instructions.md`

#### Development Tools
- **NEW:** `start_dev.sh` - Development server startup script
- **NEW:** `prompt_generator.py` - Star Wars character prompt generator
- **IMPROVED:** `start.sh` - Cleaned up production startup script

#### Configuration Files
- **UPDATED:** `.gitignore` - Added `config.json` to prevent user config overwrite
- **IMPROVED:** Log rotation and system integration in startup scripts

### 🔒 Security & Stability

#### Security Improvements
- **ENHANCED:** User configuration stored separately from git-tracked files
- **IMPROVED:** Token management with secure storage and validation
- **ENHANCED:** Password change validation and error handling

#### Stability Improvements
- **IMPROVED:** Caching mechanism for configuration with TTL
- **ENHANCED:** Error handling throughout the application
- **STANDARDIZED:** API response formats and error messages

### 🔄 Migration & Compatibility

#### Backward Compatibility
- **MAINTAINED:** Existing `models.json` configuration continues to work
- **PRESERVED:** All existing API endpoints remain functional
- **ENSURED:** Smooth migration path for existing users

#### Migration Notes
- Existing BASE_DIR settings in `models.json` are automatically detected
- Users can create `config.json` to override defaults without git conflicts
- No breaking changes to existing functionality

### 📋 Technical Details

#### Changed Files
**Backend:**
- `api.py` - Removed duplicate functions, improved BASE_DIR handling
- `api_file_manager.py` - Updated to use centralized ModelManager methods
- `api_json_models.py` - Enhanced config endpoint with source tracking
- `api_models.py` - Removed duplicate config routes, improved organization
- `model_utils.py` - Major enhancement with cascading config and user management

**Frontend:**
- `front/src/components/BundleManagerComponent.vue` - Minor UI improvements
- `front/src/components/JsonEditorComponent.vue` - Removed BASE_DIR, added accordions
- `front/src/router/index.js` - Updated settings route
- `front/src/services/api.js` - Fixed port configuration

**New Files:**
- `front/src/components/SettingsComponent.vue`
- `front/src/components/common/AccordionComponent.vue`
- `CONFIG_DOCUMENTATION.md`
- `config.json.example`
- `.github/instructions/*.md`
- `start_dev.sh`
- `prompt_generator.py`

**Removed Files:**
- `front/src/components/ChangePasswordComponent.vue`

### 🎯 Future Considerations

This refactoring provides a solid foundation for:
- Additional configuration options
- Enhanced user management
- Improved API organization
- Better development workflows
- Scalable UI component system

---

**Full Diff Summary:**
- Files modified: 12
- Files added: 8
- Files deleted: 1
- Total changes: 21 files affected

**Key Benefits:**
- Git-resistant user configuration
- Improved UI/UX consistency
- Better code organization
- Enhanced security
- Comprehensive documentation
