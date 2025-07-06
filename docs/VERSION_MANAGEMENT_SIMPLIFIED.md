# Version Management

## Overview

The application uses a unified versioning system following [Semantic Versioning (SemVer)](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes, incompatible API changes
- **MINOR**: New features, backward-compatible functionality
- **PATCH**: Bug fixes, backward-compatible fixes

## Version Files

- `version.json` - Master version file (source of truth)
- `version.py` - Python version module for backend
- `front/package.json` - NPM package with synchronized version

## Current Version Structure

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

## API Endpoint

### GET /api/version
Returns complete version information (publicly accessible):

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

## Version Update Process

### Automatic (Linux/macOS/WSL)
```bash
# Patch release (bug fixes)
./scripts/bump-version.sh patch

# Minor release (new features)
./scripts/bump-version.sh minor

# Major release (breaking changes)
./scripts/bump-version.sh major
```

### Manual Update
1. Update `version.json`
2. Update `version.py` 
3. Update `front/package.json`
4. Commit changes with version tag
