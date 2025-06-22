@echo off
REM Script de mise à jour de version pour Windows
REM Usage: scripts\bump-version.bat [major|minor|patch] ["Custom message"]

setlocal enabledelayedexpansion

if "%1"=="" (
    echo Usage: %0 [major^|minor^|patch] ["Custom message"]
    echo.
    echo Examples:
    echo   %0 patch
    echo   %0 minor "New feature release"
    echo   %0 major "Breaking changes"
    exit /b 1
)

set VERSION_TYPE=%1
set CUSTOM_MESSAGE=%~2

REM Vérifier le type de version
if not "%VERSION_TYPE%"=="major" if not "%VERSION_TYPE%"=="minor" if not "%VERSION_TYPE%"=="patch" (
    echo Error: Invalid version type. Use 'major', 'minor', or 'patch'
    exit /b 1
)

REM Aller au répertoire racine
cd /d "%~dp0\.."

REM Vérifier que version.json existe
if not exist "version.json" (
    echo Error: version.json not found
    exit /b 1
)

REM Lire la version actuelle (version simplifiée)
for /f "tokens=2 delims=:" %%a in ('findstr /c:"\"version\"" version.json') do (
    set CURRENT_VERSION=%%a
    set CURRENT_VERSION=!CURRENT_VERSION: =!
    set CURRENT_VERSION=!CURRENT_VERSION:"=!
    set CURRENT_VERSION=!CURRENT_VERSION:,=!
)

echo Current version: !CURRENT_VERSION!

REM Décomposer la version (version simplifiée)
for /f "tokens=1,2,3 delims=." %%a in ("!CURRENT_VERSION!") do (
    set MAJOR=%%a
    set MINOR=%%b
    set PATCH=%%c
)

REM Incrémenter selon le type
if "%VERSION_TYPE%"=="major" (
    set /a MAJOR+=1
    set MINOR=0
    set PATCH=0
)
if "%VERSION_TYPE%"=="minor" (
    set /a MINOR+=1
    set PATCH=0
)
if "%VERSION_TYPE%"=="patch" (
    set /a PATCH+=1
)

set NEW_VERSION=!MAJOR!.!MINOR!.!PATCH!
echo New version: !NEW_VERSION!

REM Générer timestamp
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set DATE_PART=%%c%%a%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIME_PART=%%a%%b
set BUILD_TIMESTAMP=!DATE_PART!-!TIME_PART!

REM Description par défaut
if "%CUSTOM_MESSAGE%"=="" (
    if "%VERSION_TYPE%"=="major" set CUSTOM_MESSAGE=Major release with breaking changes
    if "%VERSION_TYPE%"=="minor" set CUSTOM_MESSAGE=Minor release with new features
    if "%VERSION_TYPE%"=="patch" set CUSTOM_MESSAGE=Patch release with bug fixes
)

echo Build: !BUILD_TIMESTAMP!
echo Description: !CUSTOM_MESSAGE!
echo.

set /p CONFIRM="Continue with version update? (y/N): "
if /i not "!CONFIRM!"=="y" (
    echo Version update cancelled
    exit /b 0
)

REM Note: Ce script Windows est une version simplifiée
REM Pour une version complète, utilisez le script bash dans WSL ou Git Bash
echo.
echo This is a simplified Windows version.
echo For full functionality, use the bash script with WSL or Git Bash:
echo   bash scripts/bump-version.sh %VERSION_TYPE% --message "%CUSTOM_MESSAGE%"
echo.
echo Manual steps needed:
echo 1. Update version.json with version "!NEW_VERSION!"
echo 2. Update version.py
echo 3. Update front/src/utils/version.js
echo 4. Update CHANGELOG.md
echo 5. Commit and tag the changes

pause
