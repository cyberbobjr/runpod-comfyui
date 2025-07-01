#!/bin/bash

# Script de mise à jour de version pour l'application ComfyUI Model Manager
# Usage: ./scripts/bump-version.sh [major|minor|patch] [--message "Custom message"]

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    echo "Usage: $0 [major|minor|patch] [--message \"Custom message\"]"
    echo ""
    echo "Options:"
    echo "  major     Increment major version (X.0.0)"
    echo "  minor     Increment minor version (x.Y.0)"
    echo "  patch     Increment patch version (x.y.Z)"
    echo "  --message Custom message for the version (optional)"
    echo ""
    echo "Examples:"
    echo "  $0 patch"
    echo "  $0 minor --message \"New feature release\""
    echo "  $0 major --message \"Breaking changes\""
}

# Vérifier les arguments
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

VERSION_TYPE=$1
CUSTOM_MESSAGE=""

# Parser les arguments
shift
while [[ $# -gt 0 ]]; do
    case $1 in
        --message)
            CUSTOM_MESSAGE="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown argument: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Valider le type de version
if [ "$VERSION_TYPE" != "major" ] && [ "$VERSION_TYPE" != "minor" ] && [ "$VERSION_TYPE" != "patch" ]; then
    echo -e "${RED}Error: Invalid version type. Use 'major', 'minor', or 'patch'${NC}"
    show_help
    exit 1
fi

# Aller au répertoire racine du projet
cd "$(dirname "$0")/.."

# Vérifier que les fichiers nécessaires existent
if [ ! -f "version.json" ]; then
    echo -e "${RED}Error: version.json not found${NC}"
    exit 1
fi

# Lire la version actuelle
CURRENT_VERSION=$(cat version.json | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])")
echo -e "${BLUE}Current version: ${CURRENT_VERSION}${NC}"

# Décomposer la version
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Incrémenter selon le type
case $VERSION_TYPE in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
echo -e "${GREEN}New version: ${NEW_VERSION}${NC}"

# Générer le build timestamp
BUILD_TIMESTAMP=$(date -u +"%Y%m%d-%H%M")
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Déterminer le message de description
if [ -n "$CUSTOM_MESSAGE" ]; then
    DESCRIPTION="$CUSTOM_MESSAGE"
else
    case $VERSION_TYPE in
        major)
            DESCRIPTION="Major release with breaking changes"
            ;;
        minor)
            DESCRIPTION="Minor release with new features"
            ;;
        patch)
            DESCRIPTION="Patch release with bug fixes"
            ;;
    esac
fi

echo -e "${YELLOW}Build: ${BUILD_TIMESTAMP}${NC}"
echo -e "${YELLOW}Description: ${DESCRIPTION}${NC}"

# Demander confirmation
echo ""
read -p "Continue with version update? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Version update cancelled${NC}"
    exit 0
fi

# Mettre à jour version.json
echo -e "${BLUE}Updating version.json...${NC}"
cat > version.json << EOF
{
  "version": "${NEW_VERSION}",
  "build": "${BUILD_TIMESTAMP}",
  "buildDate": "${BUILD_DATE}",
  "components": {
    "api": "${NEW_VERSION}",
    "ui": "${NEW_VERSION}"
  },
  "description": "${DESCRIPTION}"
}
EOF

# Mettre à jour version.py
echo -e "${BLUE}Updating version.py...${NC}"
sed -i.bak "s/__version__ = \".*\"/__version__ = \"${NEW_VERSION}\"/" back/version.py
sed -i.bak "s/__build__ = \".*\"/__build__ = \"${BUILD_TIMESTAMP}\"/" back/version.py
sed -i.bak "s/__description__ = \".*\"/__description__ = \"${DESCRIPTION}\"/" back/version.py
rm back/version.py.bak

# Mettre à jour version.js frontend
echo -e "${BLUE}Updating frontend version.js...${NC}"
sed -i.bak "s/export const version = \".*\"/export const version = \"${NEW_VERSION}\"/" front/src/utils/version.js
sed -i.bak "s/export const build = \".*\"/export const build = \"${BUILD_TIMESTAMP}\"/" front/src/utils/version.js
sed -i.bak "s/export const buildDate = \".*\"/export const buildDate = \"${BUILD_DATE}\"/" front/src/utils/version.js
sed -i.bak "s/export const description = \".*\"/export const description = \"${DESCRIPTION}\"/" front/src/utils/version.js
rm front/src/utils/version.js.bak

# Mettre à jour package.json si il existe
if [ -f "front/package.json" ]; then
    echo -e "${BLUE}Updating frontend package.json...${NC}"
    sed -i.bak "s/\"version\": \".*\"/\"version\": \"${NEW_VERSION}\"/" front/package.json
    rm front/package.json.bak
fi

# Mettre à jour CHANGELOG.md
echo -e "${BLUE}Updating CHANGELOG.md...${NC}"
CHANGELOG_ENTRY="## [v${NEW_VERSION}] - $(date +"%Y-%m-%d")

### ${VERSION_TYPE^} Release
- ${DESCRIPTION}
- Build: ${BUILD_TIMESTAMP}

"

# Insérer la nouvelle entrée après la première ligne du changelog
if [ -f "CHANGELOG.md" ]; then
    # Créer un fichier temporaire avec la nouvelle entrée
    echo "$CHANGELOG_ENTRY" > temp_changelog.md
    tail -n +2 CHANGELOG.md >> temp_changelog.md
    # Garder la première ligne (titre)
    head -n 1 CHANGELOG.md > new_changelog.md
    echo "" >> new_changelog.md
    cat temp_changelog.md >> new_changelog.md
    mv new_changelog.md CHANGELOG.md
    rm temp_changelog.md
fi

# Commit Git si c'est un repository Git

# Build frontend before tagging
if [ -d "front" ] && [ -f "front/package.json" ]; then
    echo -e "${BLUE}Building frontend...${NC}"
    (cd front && npm run build)
    if [ $? -ne 0 ]; then
        echo -e "${RED}Frontend build failed. Aborting version bump.${NC}"
        exit 1
    fi
fi

if [ -d ".git" ]; then
    echo -e "${BLUE}Creating Git commit...${NC}"
    git add version.json version.py front/src/utils/version.js CHANGELOG.md
    if [ -f "front/package.json" ]; then
        git add front/package.json
    fi
    
    git commit -m "chore: bump version to v${NEW_VERSION}

- ${DESCRIPTION}
- Build: ${BUILD_TIMESTAMP}
- Type: ${VERSION_TYPE} release"

    # Créer un tag
    echo -e "${BLUE}Creating Git tag...${NC}"
    git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}

${DESCRIPTION}

Build: ${BUILD_TIMESTAMP}
Date: ${BUILD_DATE}"

    echo -e "${GREEN}Git tag v${NEW_VERSION} created${NC}"
    echo -e "${YELLOW}Don't forget to push with: git push && git push --tags${NC}"
else
    echo -e "${YELLOW}Not a Git repository, skipping Git operations${NC}"
fi

echo ""
echo -e "${GREEN}✅ Version successfully updated to v${NEW_VERSION}${NC}"
echo -e "${GREEN}✅ Build: ${BUILD_TIMESTAMP}${NC}"
echo -e "${GREEN}✅ All files updated${NC}"

if [ -d ".git" ]; then
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  git push && git push --tags"
    echo "  Deploy the new version"
fi
