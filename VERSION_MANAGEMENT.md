# Version Management System

This document describes the unified version management system implemented for the ComfyUI Model Manager application.

## Overview

The application uses a **global unified versioning system** where both frontend and backend share the same version number. This ensures consistency and simplifies deployment.

## Version Structure

The version follows the [Semantic Versioning (SemVer)](https://semver.org/) specification:

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes, incompatible API changes
- **MINOR**: New features, backward-compatible functionality
- **PATCH**: Bug fixes, backward-compatible fixes

## Files Structure

### Core Version Files

```
/
├── version.json              # Master version file (source of truth)
├── version.py               # Python version module for backend
├── front/
│   ├── package.json         # NPM package with synchronized version
│   └── src/utils/version.js # JavaScript version module for frontend
└── scripts/
    ├── bump-version.sh      # Unix/Linux version bump script
    └── bump-version.bat     # Windows version bump script
```

### version.json (Master File)

```json
{
  "version": "2.0.0",
  "build": "20250622-1430",
  "buildDate": "2025-06-22T14:30:00Z",
  "components": {
    "api": "2.0.0",
    "ui": "2.0.0"
  },
  "description": "Configuration and Settings Management Refactoring"
}
```

## API Endpoints

### GET /api/version

Returns complete version information (publicly accessible, no authentication required):

```json
{
  "version": "2.0.0",
  "build": "20250622-1430",
  "buildDate": "2025-06-22T14:30:00Z",
  "components": {
    "api": "2.0.0",
    "ui": "2.0.0"
  },
  "description": "Configuration and Settings Management Refactoring"
}
```

## Usage

### Automatic Version Update

Use the provided script to automatically update all version files:

**Linux/macOS/WSL:**
```bash
# Patch release (bug fixes)
./scripts/bump-version.sh patch

# Minor release (new features)  
./scripts/bump-version.sh minor --message "Added new model management features"

# Major release (breaking changes)
./scripts/bump-version.sh major --message "Complete API redesign"
```

**Windows:**
```cmd
REM Basic version bump (provides manual steps)
scripts\bump-version.bat patch "Bug fixes and improvements"
```

### Manual Version Update

1. **Update `version.json`:**
   ```json
   {
     "version": "2.1.0",
     "build": "20250622-1500",
     "buildDate": "2025-06-22T15:00:00Z",
     "components": {
       "api": "2.1.0", 
       "ui": "2.1.0"
     },
     "description": "Your release description"
   }
   ```

2. **Update `version.py`:**
   ```python
   __version__ = "2.1.0"
   __build__ = "20250622-1500"
   __description__ = "Your release description"
   ```

3. **Update `front/src/utils/version.js`:**
   ```javascript
   export const version = "2.1.0";
   export const build = "20250622-1500"; 
   export const buildDate = "2025-06-22T15:00:00Z";
   export const description = "Your release description";
   ```

4. **Update `front/package.json`:**
   ```json
   {
     "version": "2.1.0"
   }
   ```

5. **Update `CHANGELOG.md`:**
   Add new entry at the top describing changes.

6. **Git Commit and Tag:**
   ```bash
   git add .
   git commit -m "chore: bump version to v2.1.0"
   git tag -a "v2.1.0" -m "Release v2.1.0"
   git push && git push --tags
   ```

## Version Display

### Backend
- **Startup logs:** Version info displayed when application starts
- **API endpoint:** `GET /api/version` returns complete version information
- **FastAPI docs:** Version appears in OpenAPI documentation

### Frontend  
- **Footer:** Version displayed in application footer
- **About modal:** Detailed version information accessible via footer
- **Console:** Version logged to browser console on startup

### API Response Headers
The application automatically adds version headers to API responses:
```
X-Version: 2.0.0
X-Build: 20250622-1430
```

## Development Workflow

### Feature Development
1. Work on feature branches
2. Use development versions: `2.1.0-dev.1`, `2.1.0-dev.2`, etc.
3. Test thoroughly before merging

### Release Process
1. **Merge to main branch**
2. **Run version script:** `./scripts/bump-version.sh [type]`
3. **Verify all files updated:** Check version.json, version.py, version.js
4. **Push with tags:** `git push && git push --tags`
5. **Deploy:** Deploy the new tagged version
6. **Update documentation:** If needed

### Hot Fixes
For critical bug fixes:
1. Create hotfix branch from latest release tag
2. Make minimal fix
3. Bump patch version: `./scripts/bump-version.sh patch`
4. Deploy immediately

## Integration Points

### Build Process
- Version information embedded in build artifacts
- Build timestamp automatically generated
- Git commit hash can be added to build info

### Deployment
- Version tags used for deployment selection
- Health checks can return version information
- Rollback procedures reference version tags

### Monitoring
- Application logs include version information
- Error reports tagged with version/build
- Performance monitoring segmented by version

## Troubleshooting

### Common Issues

**Version mismatch between components:**
```bash
# Check all version files
grep -r "version.*2.0.0" version.json version.py front/src/utils/version.js front/package.json
```

**API version endpoint not working:**
- Ensure `/api/version` is excluded from authentication
- Check that `version.json` exists and is readable
- Verify import statements in `main.py`

**Frontend version not updating:**
- Clear browser cache
- Rebuild frontend: `cd front && npm run build`
- Check version.js import in FooterComponent.vue

### Validation
Test that all components report the same version:
```bash
# Backend version
curl http://localhost:8081/api/version

# Check startup logs
grep "ComfyUI Model Manager v" logs/

# Frontend version (check browser console or footer)
```

## Future Enhancements

- **Automated CI/CD integration** with version bumping
- **Pre-release versions** (alpha, beta, rc)
- **Component-specific versioning** for microservices
- **Version compatibility matrix** for API clients
- **Automatic changelog generation** from commit messages
