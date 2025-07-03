import os
import json
import traceback
import uuid
import zipfile
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from .download_manager import DownloadManager
from .config_service import ConfigService
from ..models.bundle_models import Bundle, BundleCreate, BundleUpdate
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Constants
BUNDLES_DIR = "bundles"
INSTALLED_BUNDLES_FILE = "installed_bundles.json"
WORKFLOW_DIR = "workflows"


class BundleService:
    """
    Bundle management service following Single Responsibility Principle.
    
    **Purpose:** Handles high-level bundle operations including:
    - Bundle creation, installation, and export
    - Bundle metadata management
    - Hardware profile filtering
    - Bundle validation and schema enforcement
    - Bundle lifecycle management (install/uninstall)
    
    **SRP Responsibility:** Bundle operations and workflow coordination.
    This class should orchestrate operations but delegate specific tasks to
    specialized services (ModelManager for model ops, DownloadManager for downloads).
    """
    
    @staticmethod
    def get_bundles_directory() -> str:
        """
        Get the bundles directory path.
        
        **Description:** Returns the path to the bundles directory.
        **Parameters:** None
        **Returns:** str containing the bundles directory path
        """
        base_dir = ConfigService.get_base_dir()
        return os.path.join(base_dir, BUNDLES_DIR)
    
    @staticmethod
    def get_workflows_directory() -> str:
        """
        Get the workflows directory path.
        
        **Description:** Returns the path to the workflows directory.
        **Parameters:** None
        **Returns:** str containing the workflows directory path
        """
        return ConfigService.get_workflows_dir()
    
    @staticmethod
    def get_installed_bundles_file() -> str:
        """
        Get the installed bundles file path.
        
        **Description:** Returns the path to the installed bundles tracking file.
        **Parameters:** None
        **Returns:** str containing the installed bundles file path
        """
        base_dir = ConfigService.get_base_dir()
        return os.path.join(base_dir, "bundles", INSTALLED_BUNDLES_FILE)
    
    def get_all_bundles(self) -> List[Bundle]:
        """
        Get all available bundles.
        
        **Description:** Retrieves all bundle definitions from ZIP files in the bundles directory.
        **Parameters:** None
        **Returns:** List of Bundle objects
        """
        bundles_dir = self.get_bundles_directory()
        bundles = []
        
        if not os.path.exists(bundles_dir):
            return bundles
        
        for filename in os.listdir(bundles_dir):
            if filename.endswith(".zip"):
                bundle_path = os.path.join(bundles_dir, filename)
                try:
                    bundle_data = self._read_bundle_from_zip(bundle_path)
                    if bundle_data:
                        # Convert dict to Bundle object
                        bundle = Bundle(**bundle_data)
                        bundles.append(bundle)
                except Exception as e:
                    logger.error(f"Error loading bundle {filename}: {e}")
        
        return bundles
    
    def get_bundle(self, bundle_id: str) -> Bundle:
        """
        Get a specific bundle by ID.
        
        **Description:** Retrieves a bundle definition by searching through ZIP files in the bundles directory.
        **Parameters:**
        - `bundle_id` (str): Bundle identifier
        **Returns:** Bundle object
        **Raises:** FileNotFoundError if bundle not found
        """
        bundles_dir = self.get_bundles_directory()
        
        if not os.path.exists(bundles_dir):
            raise FileNotFoundError(f"Bundle {bundle_id} not found")
        
        # Search through all ZIP files to find the bundle with matching ID
        for filename in os.listdir(bundles_dir):
            if filename.endswith(".zip"):
                bundle_path = os.path.join(bundles_dir, filename)
                try:
                    bundle_data = self._read_bundle_from_zip(bundle_path)
                    if bundle_data and bundle_data.get("id") == bundle_id:
                        return Bundle(**bundle_data)
                except Exception as e:
                    logger.error(f"Error reading bundle from {filename}: {e}")
                    continue
        
        raise FileNotFoundError(f"Bundle {bundle_id} not found")
    
    def create_bundle(self, bundle_data: BundleCreate) -> Bundle:
        """
        Create a new bundle.
        
        **Description:** Creates a new bundle ZIP file with generated ID, timestamps, and workflows.
        **Parameters:**
        - `bundle_data` (BundleCreate): Bundle data to create
        **Returns:** Created Bundle object
        """
        # Check if bundle with same name exists
        bundles = self.get_all_bundles()
        for bundle in bundles:
            if bundle.name == bundle_data.name:
                raise ValueError(f"Bundle with name '{bundle_data.name}' already exists")
        
        bundle_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        bundle_dict = {
            "id": bundle_id,
            "name": bundle_data.name,
            "description": bundle_data.description,
            "version": bundle_data.version,
            "author": bundle_data.author,
            "website": bundle_data.website,
            "workflows": bundle_data.workflows,
            "hardware_profiles": {k: v.dict() for k, v in bundle_data.hardware_profiles.items()},
            "workflow_params": bundle_data.workflow_params,
            "created_at": now,
            "updated_at": now
        }
        
        bundles_dir = self.get_bundles_directory()
        os.makedirs(bundles_dir, exist_ok=True)
        
        # Create ZIP file instead of JSON
        bundle_zip_path = os.path.join(bundles_dir, f"{bundle_id}.zip")
        workflows_dir = self.get_workflows_directory()
        
        with zipfile.ZipFile(bundle_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add bundle definition JSON
            bundle_json = json.dumps(bundle_dict, indent=2)
            zipf.writestr(f"{bundle_id}.json", bundle_json)
            
            # Add workflows if they exist
            for workflow_file in bundle_data.workflows:
                workflow_path = os.path.join(workflows_dir, workflow_file)
                if os.path.exists(workflow_path):
                    zipf.write(workflow_path, f"workflows/{workflow_file}")
                else:
                    logger.warning(f"Workflow file {workflow_file} not found in {workflows_dir}")
        
        return Bundle(**bundle_dict)
    
    def update_bundle(self, bundle_id: str, bundle_data: BundleUpdate) -> Bundle:
        """
        Update an existing bundle.
        
        **Description:** Updates a bundle ZIP file with new data while preserving ID and created_at.
        **Parameters:**
        - `bundle_id` (str): Bundle identifier
        - `bundle_data` (BundleUpdate): Update data
        **Returns:** Updated Bundle object
        **Raises:** FileNotFoundError if bundle not found
        """
        existing_bundle = self.get_bundle(bundle_id)
        
        # Update fields
        updated_dict = existing_bundle.dict()
        if bundle_data.name is not None:
            updated_dict["name"] = bundle_data.name
        if bundle_data.description is not None:
            updated_dict["description"] = bundle_data.description
        if bundle_data.version is not None:
            updated_dict["version"] = bundle_data.version
        if bundle_data.author is not None:
            updated_dict["author"] = bundle_data.author
        if bundle_data.website is not None:
            updated_dict["website"] = bundle_data.website
        if bundle_data.workflows is not None:
            updated_dict["workflows"] = bundle_data.workflows
        if bundle_data.hardware_profiles is not None:
            updated_dict["hardware_profiles"] = {k: v.dict() for k, v in bundle_data.hardware_profiles.items()}
        if bundle_data.workflow_params is not None:
            updated_dict["workflow_params"] = bundle_data.workflow_params
        
        updated_dict["updated_at"] = datetime.now().isoformat()
        
        bundles_dir = self.get_bundles_directory()
        bundle_zip_path = os.path.join(bundles_dir, f"{bundle_id}.zip")
        workflows_dir = self.get_workflows_directory()
        
        # Create new ZIP file with updated content
        temp_zip_path = f"{bundle_zip_path}.tmp"
        
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add updated bundle definition JSON
            bundle_json = json.dumps(updated_dict, indent=2)
            zipf.writestr(f"{bundle_id}.json", bundle_json)
            
            # Add workflows (use updated list if provided, otherwise keep existing)
            workflows_to_add = bundle_data.workflows if bundle_data.workflows is not None else existing_bundle.workflows
            for workflow_file in workflows_to_add:
                workflow_path = os.path.join(workflows_dir, workflow_file)
                if os.path.exists(workflow_path):
                    zipf.write(workflow_path, f"workflows/{workflow_file}")
                else:
                    logger.warning(f"Workflow file {workflow_file} not found in {workflows_dir}")
        
        # Replace original with updated ZIP
        if os.path.exists(bundle_zip_path):
            os.remove(bundle_zip_path)
        os.rename(temp_zip_path, bundle_zip_path)
        
        return Bundle(**updated_dict)
    
    def delete_bundle(self, bundle_id: str) -> None:
        """
        Delete a bundle.
        
        **Description:** Removes a bundle ZIP file from the system.
        **Parameters:**
        - `bundle_id` (str): Bundle identifier
        **Returns:** None
        **Raises:** FileNotFoundError if bundle not found
        """
        bundles_dir = self.get_bundles_directory()
        bundle_path = os.path.join(bundles_dir, f"{bundle_id}.zip")
        
        if not os.path.exists(bundle_path):
            raise FileNotFoundError(f"Bundle {bundle_id} not found")
        
        os.remove(bundle_path)
        logger.info(f"Bundle {bundle_id} deleted successfully")

    def import_bundle_from_zip(self, upload_file) -> str:
        """
        Import a bundle from uploaded ZIP file.
        
        **Description:** Imports a bundle ZIP file into the bundles directory without installing it.
        **Parameters:**
        - `upload_file` (UploadFile): Uploaded ZIP file
        **Returns:** Bundle ID of imported bundle
        **Raises:** ValueError for invalid files or bundle conflicts
        """
        if not upload_file.filename.endswith('.zip'):
            raise ValueError("File must be a ZIP archive")
        
        # Save uploaded file temporarily to read bundle data
        temp_path = f"/tmp/{upload_file.filename}"
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
            
            # Read bundle data from ZIP to get bundle ID and validate
            bundle_data = self._read_bundle_from_zip(temp_path)
            if not bundle_data:
                raise ValueError("Invalid bundle ZIP file - no bundle definition found")
            
            bundle_id = bundle_data.get("id")
            if not bundle_id:
                raise ValueError("Bundle definition missing required 'id' field")
            
            # Check if bundle already exists
            try:
                existing_bundle = self.get_bundle(bundle_id)
                raise ValueError(f"Bundle with ID '{bundle_id}' already exists")
            except FileNotFoundError:
                # Bundle doesn't exist, we can proceed
                pass
            
            # Copy ZIP file to bundles directory
            bundles_dir = self.get_bundles_directory()
            os.makedirs(bundles_dir, exist_ok=True)
            
            bundle_zip_path = os.path.join(bundles_dir, f"{bundle_id}.zip")
            shutil.copy2(temp_path, bundle_zip_path)
            
            logger.info(f"Bundle {bundle_id} imported successfully")
            return bundle_id
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def get_bundle_download_path(self, bundle_id: str) -> str:
        """
        Get download path for a bundle ZIP file.
        
        **Description:** Returns the path to the bundle ZIP file for download.
        **Parameters:**
        - `bundle_id` (str): Bundle identifier
        **Returns:** Path to the bundle ZIP file
        **Raises:** FileNotFoundError if bundle not found
        """
        bundle = self.get_bundle(bundle_id)
        
        bundles_dir = self.get_bundles_directory()
        zip_path = os.path.join(bundles_dir, f"{bundle_id}.zip")
        
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"Bundle ZIP file {bundle_id} not found")
        
        return zip_path

    def duplicate_bundle(self, bundle_id: str, new_name: str) -> str:
        """
        Duplicate an existing bundle.
        
        **Description:** Creates a copy of a bundle ZIP file with a new name.
        **Parameters:**
        - `bundle_id` (str): Source bundle identifier
        - `new_name` (str): Name for the new bundle
        **Returns:** New bundle ID
        **Raises:** FileNotFoundError if source bundle not found, ValueError if name exists
        """
        # Get source bundle
        source_bundle = self.get_bundle(bundle_id)
        
        # Check if new name already exists
        bundles = self.get_all_bundles()
        for bundle in bundles:
            if bundle.name == new_name:
                raise ValueError(f"Bundle with name '{new_name}' already exists")
        
        # Create new bundle
        new_bundle_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        new_bundle_dict = source_bundle.dict()
        new_bundle_dict.update({
            "id": new_bundle_id,
            "name": new_name,
            "created_at": now,
            "updated_at": now
        })
        
        # Copy ZIP file with new content
        bundles_dir = self.get_bundles_directory()
        source_zip_path = os.path.join(bundles_dir, f"{bundle_id}.zip")
        new_zip_path = os.path.join(bundles_dir, f"{new_bundle_id}.zip")
        
        with zipfile.ZipFile(source_zip_path, 'r') as source_zip:
            with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                # Copy workflows
                for item in source_zip.infolist():
                    if item.filename.startswith('workflows/'):
                        data = source_zip.read(item.filename)
                        new_zip.writestr(item.filename, data)
                
                # Add updated bundle definition
                bundle_json = json.dumps(new_bundle_dict, indent=2)
                new_zip.writestr(f"{new_bundle_id}.json", bundle_json)
        
        return new_bundle_id

    def install_bundle(self, bundle_id: str, profile: str) -> Dict[str, List[str]]:
        """
        Install a bundle with specified profile.
        
        **Description:** Installs all models and workflows for a bundle profile.
        **Parameters:**
        - `bundle_id` (str): Bundle identifier
        - `profile` (str): Hardware profile to install
        **Returns:** Dictionary with installation results
        **Raises:** FileNotFoundError if bundle not found, ValueError if profile not found
        """
        bundle = self.get_bundle(bundle_id)

        if bundle.hardware_profiles is None or profile not in bundle.hardware_profiles:
            raise ValueError(f"Profile '{profile}' not found in bundle")

        profile_data = bundle.hardware_profiles[profile]
        installed_models = []
        failed_models = []

        # Install models
        if profile_data and hasattr(profile_data, "models") and profile_data.models:
            for model in profile_data.models:
                try:
                    # Convert model to dict if needed
                    if hasattr(model, "dict") and callable(model.dict):
                        model_entry = model.dict()
                    elif isinstance(model, dict):
                        model_entry = model
                    else:
                        model_entry = vars(model)
                    base_dir = ConfigService.get_base_dir()
                    from .token_service import TokenService
                    tokens = TokenService.get_tokens()
                    hf_token = tokens.get("hf_token")
                    civitai_token = tokens.get("civitai_token")
                    DownloadManager.download_model(model_entry, base_dir, hf_token=hf_token, civitai_token=civitai_token, background=True)
                    dest = model_entry.get("dest", model_entry.get("git", ""))
                    installed_models.append(dest)
                except Exception as e:
                    logger.error(f"Failed to install model {model}: {e}")
                    logger.error(traceback.format_exc())
                    if 'model_entry' in locals():
                        dest = model_entry.get("dest", model_entry.get("git", ""))
                    else:
                        dest = getattr(model, "dest", None)
                        if dest is None and isinstance(model, dict):
                            dest = model.get("dest", model.get("git", ""))
                        elif dest is None:
                            dest = getattr(model, "git", "")
                    failed_models.append(dest)

        # Track installation
        installation_status = {
            "status": "completed" if not failed_models else "partial",
            "installed_models": installed_models,
            "failed_models": failed_models
        }

        self._track_installed_bundle(bundle_id, profile, installation_status)

        return {
            "installed": installed_models,
            "failed": failed_models
        }

    def uninstall_bundle(self, bundle_id: str, profile: str) -> None:
        """
        Uninstall a specific hardware profile from a bundle and remove its models from disk if not used elsewhere.

        **Description:** Removes a hardware profile from the installed bundle tracking. Deletes models from disk if they are not used by any other installed bundle/profile. If all profiles are uninstalled, the bundle is fully removed from installed bundles.
        **Parameters:**
        - `bundle_id` (str): Bundle identifier
        - `profile` (str): Hardware profile to uninstall
        **Returns:** None
        **Raises:** FileNotFoundError if bundle or profile not installed
        """
        from .model_manager import ModelManager
        installed_file = self.get_installed_bundles_file()
        if not os.path.exists(installed_file):
            raise FileNotFoundError(f"Bundle {bundle_id} is not installed")

        with open(installed_file, "r", encoding="utf-8") as f:
            installed_bundles = json.load(f)

        if bundle_id not in installed_bundles:
            raise FileNotFoundError(f"Bundle {bundle_id} is not installed")

        bundle_entry = installed_bundles[bundle_id]
        if 'profile' in bundle_entry:
            # Convert to multi-profile format
            bundle_entry = {bundle_entry['profile']: bundle_entry}
            installed_bundles[bundle_id] = bundle_entry

        if profile not in bundle_entry:
            raise FileNotFoundError(f"Profile {profile} not found for bundle {bundle_id}")

        # Get the models to remove for this profile
        try:
            bundle = self.get_bundle(bundle_id)
            profile_data = bundle.hardware_profiles[profile] if hasattr(bundle, 'hardware_profiles') else bundle["hardware_profiles"][profile]
            models_to_remove = [m.dest for m in profile_data.models if hasattr(m, 'dest')] if hasattr(profile_data, 'models') else [m.get('dest') for m in profile_data["models"]]
        except Exception as e:
            logger.error(f"Could not determine models to remove for bundle {bundle_id} profile {profile}: {e}")
            models_to_remove = []

        # Build a set of all models still in use by other installed profiles
        used_models = set()
        for b_id, profiles in installed_bundles.items():
            # Convert legacy
            if 'profile' in profiles:
                profiles = {profiles['profile']: profiles}
            for prof_name in profiles:
                if b_id == bundle_id and prof_name == profile:
                    continue  # skip the one being uninstalled
                try:
                    b = self.get_bundle(b_id)
                    prof_data = b.hardware_profiles[prof_name] if hasattr(b, 'hardware_profiles') else b["hardware_profiles"][prof_name]
                    prof_models = [m.dest for m in prof_data.models if hasattr(m, 'dest')] if hasattr(prof_data, 'models') else [m.get('dest') for m in prof_data["models"]]
                    used_models.update([d for d in prof_models if d])
                except Exception as e:
                    logger.warning(f"Could not check models for bundle {b_id} profile {prof_name}: {e}")
                    continue

        # Remove models from disk if not used elsewhere
        base_dir = ConfigService.get_base_dir()
        for model_path in models_to_remove:
            if model_path and model_path not in used_models:
                abs_path = ModelManager.resolve_path(model_path, base_dir)
                try:
                    if abs_path and os.path.exists(abs_path):
                        os.remove(abs_path)
                        logger.info(f"Removed model file: {abs_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove model file {abs_path}: {e}")

        # Remove the profile from installed tracking
        del bundle_entry[profile]
        if not bundle_entry:
            del installed_bundles[bundle_id]

        with open(installed_file, "w", encoding="utf-8") as f:
            json.dump(installed_bundles, f, indent=2)

    def get_installed_bundles(self) -> List[Dict[str, Any]]:
        """
        Get list of installed bundles.

        **Description:** Returns information about all installed bundles and profiles (list format).
        **Parameters:** None
        **Returns:** List of installed bundle information (installation)
        """
        installed_file = self.get_installed_bundles_file()

        if not os.path.exists(installed_file):
            return []

        try:
            with open(installed_file, "r", encoding="utf-8") as f:
                installed_bundles = json.load(f)

            if not isinstance(installed_bundles, list):
                logger.warning("Installed bundles file is not a list, returning empty list.")
                return []

            result = []
            for entry in installed_bundles:
                bundle_id = entry.get("bundle_id")
                try:
                    result.append(entry)
                except FileNotFoundError:
                    logger.warning(f"Installed bundle {bundle_id} not found in bundles directory")
            return result
        except Exception as e:
            logger.error(f"Error reading installed bundles: {e}")
            return []
    
    @staticmethod
    def export_bundle(bundle_id: str, include_models: bool = False) -> Optional[str]:
        """
        Export a bundle to a ZIP file.
        
        **Description:** Creates an export ZIP file containing bundle definition and optionally model files.
        **Parameters:**
        - `bundle_id` (str): Bundle identifier
        - `include_models` (bool): Whether to include model files
        **Returns:** Path to the exported ZIP file or None if failed
        """
        try:
            bundle_service = BundleService()
            bundle = bundle_service.get_bundle(bundle_id)
        except FileNotFoundError:
            return None
        
        bundles_dir = BundleService.get_bundles_directory()
        source_zip_path = os.path.join(bundles_dir, f"{bundle_id}.zip")
        export_path = os.path.join(bundles_dir, f"{bundle_id}_export.zip")
        
        try:
            with zipfile.ZipFile(source_zip_path, 'r') as source_zip:
                with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as export_zip:
                    # Copy all content from source bundle
                    for item in source_zip.infolist():
                        data = source_zip.read(item.filename)
                        export_zip.writestr(item.filename, data)
                    
                    # Add models if requested
                    if include_models:
                        base_dir = ConfigService.get_base_dir()
                        for profile_data in bundle.hardware_profiles.values():
                            for model in profile_data.models:
                                model_path = model.dest
                                if model_path:
                                    full_path = model_path.replace("${BASE_DIR}", base_dir)
                                    if os.path.exists(full_path):
                                        export_zip.write(full_path, f"models/{os.path.basename(full_path)}")
            
            return export_path
        except Exception as e:
            logger.error(f"Error exporting bundle {bundle_id}: {e}")
            return None

    @staticmethod
    def import_bundle(zip_path: str, overwrite: bool = False) -> Optional[Dict[str, Any]]:
        """
        Import a bundle from a ZIP file.
        
        **Description:** Extracts and imports a bundle from a ZIP file into the bundles directory.
        **Parameters:**
        - `zip_path` (str): Path to the ZIP file
        - `overwrite` (bool): Whether to overwrite existing bundle
        **Returns:** Imported bundle dictionary or None if failed
        """
        try:
            # Read bundle data from ZIP
            bundle_data = BundleService._read_bundle_from_zip(zip_path)
            if not bundle_data:
                raise ValueError("No bundle definition found in ZIP")
            
            bundle_id = bundle_data.get("id")
            if not bundle_id:
                raise ValueError("Bundle definition missing required 'id' field")
            
            # Check if bundle already exists
            bundles_dir = BundleService.get_bundles_directory()
            bundle_zip_path = os.path.join(bundles_dir, f"{bundle_id}.zip")
            
            if os.path.exists(bundle_zip_path) and not overwrite:
                raise ValueError("Bundle already exists and overwrite is False")
            
            # Copy ZIP file to bundles directory
            os.makedirs(bundles_dir, exist_ok=True)
            shutil.copy2(zip_path, bundle_zip_path)
            
            logger.info(f"Bundle {bundle_id} imported successfully")
            return bundle_data
            
        except Exception as e:
            logger.error(f"Error importing bundle from {zip_path}: {e}")
            return None

    @staticmethod
    def _track_installed_bundle(bundle_id: str, profile: str, installation_status: Dict[str, Any]) -> None:
        """
        Track an installed bundle as a list of installed bundles/profiles.

        **Description:** Records bundle installation information as a list of dicts, each with bundle_id and profile.
        **Parameters:**
        - `bundle_id` (str): Bundle identifier
        - `profile` (str): Hardware profile used
        - `installation_status` (Dict[str, Any]): Installation result
        **Returns:** None
        """
        installed_file = BundleService.get_installed_bundles_file()
        installed_bundles = []
        if os.path.exists(installed_file):
            try:
                with open(installed_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, list):
                        installed_bundles = loaded
                    else:
                        logger.warning(f"Installed bundles file is not a list, resetting: {type(loaded)}")
                        installed_bundles = []
            except Exception as e:
                logger.warning(f"Could not read installed bundles file: {e}")
                installed_bundles = []

        # Prepare the new profile installation info
        profile_info = {
            "bundle_id": bundle_id,
            "profile": profile,
            "installed_at": datetime.now().isoformat(),
            "status": installation_status["status"],
            "installed_models": installation_status["installed_models"],
            "failed_models": installation_status["failed_models"]
        }

        # Remove any existing entry for this bundle_id/profile
        installed_bundles = [entry for entry in installed_bundles if not (entry.get("bundle_id") == bundle_id and entry.get("profile") == profile)]
        installed_bundles.append(profile_info)

        os.makedirs(os.path.dirname(installed_file) or ".", exist_ok=True)
        with open(installed_file, "w", encoding="utf-8") as f:
            json.dump(installed_bundles, f, indent=2)

    @staticmethod
    def _read_bundle_from_zip(zip_path: str) -> Optional[Dict[str, Any]]:
        """
        Read bundle information from a ZIP file.
        
        **Description:** Extracts and returns bundle definition from a ZIP file without extracting it.
        **Parameters:**
        - `zip_path` (str): Path to the ZIP file containing the bundle
        **Returns:** Dictionary containing bundle data or None if failed
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # Find bundle JSON file (should be at root level)
                bundle_files = [f for f in zipf.namelist() if f.endswith('.json') and '/' not in f]
                if not bundle_files:
                    logger.warning(f"No bundle definition found in ZIP: {zip_path}")
                    return None
                
                bundle_file = bundle_files[0]
                bundle_data = json.loads(zipf.read(bundle_file).decode('utf-8'))
                return bundle_data
        except Exception as e:
            logger.error(f"Error reading bundle from ZIP {zip_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading bundle from ZIP {zip_path}: {e}")
            return None
