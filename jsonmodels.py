import os
import json
import logging
from fastapi import APIRouter, HTTPException, Depends, Body, File, UploadFile
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from fastapi.responses import JSONResponse, FileResponse
import shutil
from api import protected, get_env_file_path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création du router pour les routes API du fichier models.json
jsonmodels_router = APIRouter(prefix="/api/jsonmodels")

MODELS_JSON = "models.json"
WORKFLOW_DIR = "workflows"
INSTALLED_BUNDLES_FILE = "installed_bundles.json"

def get_models_json_path():
    """Retourne le chemin complet du fichier models.json en essayant plusieurs emplacements possibles."""
    # Stratégie 1: Répertoire défini par COMFYUI_MODEL_DIR
    base_dir = os.environ.get("COMFYUI_MODEL_DIR", ".")
    path = os.path.join(base_dir, MODELS_JSON)
    logger.info(f"Recherche models.json - Stratégie 1: {path}")
    if os.path.exists(path):
        logger.info(f"Trouvé models.json à {path}")
        return path
    
    # Stratégie 2: Répertoire courant de l'application
    current_dir = os.path.abspath(os.getcwd())
    path = os.path.join(current_dir, MODELS_JSON)
    logger.info(f"Recherche models.json - Stratégie 2: {path}")
    if os.path.exists(path):
        logger.info(f"Trouvé models.json à {path}")
        return path
    
    # Stratégie 3: Répertoire du script actuel
    script_dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(script_dir, MODELS_JSON)
    logger.info(f"Recherche models.json - Stratégie 3: {path}")
    if os.path.exists(path):
        logger.info(f"Trouvé models.json à {path}")
        return path
    
    # Stratégie 4: Répertoire parent du script actuel
    parent_dir = os.path.abspath(os.path.join(script_dir, ".."))
    path = os.path.join(parent_dir, MODELS_JSON)
    logger.info(f"Recherche models.json - Stratégie 4: {path}")
    if os.path.exists(path):
        logger.info(f"Trouvé models.json à {path}")
        return path
    
    # Tous les essais ont échoué, retournons simplement le chemin par défaut
    # et laissons la fonction load_models_json gérer l'erreur
    logger.warning(f"Aucun fichier models.json trouvé, utilisation du chemin par défaut: {os.path.join(base_dir, MODELS_JSON)}")
    return os.path.join(base_dir, MODELS_JSON)

def load_models_json():
    """Charge le fichier models.json complet avec gestion des erreurs améliorée."""
    models_path = get_models_json_path()
    logger.info(f"Tentative de chargement du fichier: {models_path}")
    
    if not os.path.exists(models_path):
        # Afficher tous les fichiers dans le répertoire courant pour aider au débogage
        try:
            parent_dir = os.path.dirname(models_path) or "."
            files = os.listdir(parent_dir)
            logger.error(f"Le fichier {models_path} n'existe pas. Contenu de {parent_dir}: {files}")
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du répertoire: {str(e)}")
        
        # Si le fichier n'existe pas, créer un fichier vide avec une structure de base
        try:
            logger.info(f"Création d'un fichier models.json vide à {models_path}")
            os.makedirs(os.path.dirname(models_path) or ".", exist_ok=True)
            empty_data = {"config": {"BASE_DIR": ""}, "groups": {}, "bundles": {}}
            with open(models_path, "w", encoding="utf-8") as f:
                json.dump(empty_data, f, indent=2)
            return empty_data
        except Exception as e:
            logger.error(f"Impossible de créer un fichier models.json vide: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Impossible de trouver ou créer le fichier models.json: {str(e)}"
            )
    
    try:
        with open(models_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Assurer que la structure de base existe
            if "bundles" not in data:
                data["bundles"] = {}
            logger.info(f"Fichier models.json chargé avec succès depuis {models_path}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de décodage JSON: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail=f"Erreur de décodage JSON: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de la lecture du fichier: {str(e)}"
        )

def save_models_json(data):
    """Sauvegarde le fichier models.json complet avec gestion des erreurs améliorée."""
    models_path = get_models_json_path()
    logger.info(f"Tentative de sauvegarde du fichier: {models_path}")
    
    try:
        # Assurer que le répertoire existe
        os.makedirs(os.path.dirname(models_path) or ".", exist_ok=True)
        
        with open(models_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Fichier models.json sauvegardé avec succès à {models_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de la sauvegarde du fichier: {str(e)}"
        )

def normalize_path(path, base_dir=None):
    """
    Normalise un chemin pour:
    1. Remplacer tous les séparateurs Windows en séparateurs Unix (/)
    2. Le rendre relatif à ${BASE_DIR} si nécessaire tout en respectant la structure de répertoires
    """
    if not path:
        return path
    
    # Convertir tous les backslashes en forward slashes
    path = path.replace('\\', '/')
    
    # Si le chemin contient déjà ${BASE_DIR}, on ne le modifie pas
    if "${BASE_DIR}" in path:
        return path
    
    # Si base_dir n'est pas fourni, on ne peut pas rendre le chemin relatif
    if not base_dir:
        return path
    
    # Normaliser base_dir (forward slashes et pas de trailing slash)
    base_dir = base_dir.replace('\\', '/').rstrip('/')
    
    # Déterminer si le chemin est déjà relatif à base_dir
    is_absolute = os.path.isabs(path)
    
    if is_absolute:
        # Si le chemin est absolu, vérifier s'il est dans base_dir
        if path.startswith(base_dir):
            # Extraire la partie relative
            relative_path = path[len(base_dir):].lstrip('/')
            return f"${{BASE_DIR}}/{relative_path}"
        else:
            # Le chemin absolu n'est pas dans base_dir, on ne peut pas le rendre relatif
            logger.warning(f"Le chemin '{path}' n'est pas dans '{base_dir}', impossible de le rendre relatif")
            return path
    else:
        # Pour les chemins relatifs, vérifier s'ils commencent par un sous-répertoire de base_dir
        
        # Extraire le dernier répertoire de base_dir comme marqueur potentiel
        # Par exemple, si base_dir est '/path/to/models', le marqueur est 'models'
        base_dir_parts = base_dir.split('/')
        base_dir_marker = base_dir_parts[-1] if base_dir_parts else None
        
        if base_dir_marker and path.startswith(f"{base_dir_marker}/"):
            # Le chemin commence déjà par le nom du répertoire de base, on considère qu'il est relatif à parent(base_dir)
            return f"${{BASE_DIR}}/{path[len(base_dir_marker)+1:]}"
        elif any(part == base_dir_marker for part in path.split('/')):
            # Si une partie du chemin est le marqueur, on extrait depuis cette partie
            parts = path.split('/')
            if base_dir_marker in parts:
                idx = parts.index(base_dir_marker)
                return f"${{BASE_DIR}}/{'/'.join(parts[idx+1:])}"
        
        # Aucun pattern reconnu, on ajoute simplement ${BASE_DIR}/ en préfixe
        return f"${{BASE_DIR}}/{path}"

class ModelEntry(BaseModel):
    url: Optional[str] = None
    dest: Optional[str] = None
    git: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[List[str]] = []
    src: Optional[str] = None
    hash: Optional[str] = None
    size: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    system_requirements: Optional[Dict[str, Any]] = None

class ModelEntryRequest(BaseModel):
    group: str
    entry: ModelEntry

class ModelGroupRequest(BaseModel):
    group: str

class UpdateModelGroupRequest(BaseModel):
    old_group: str
    new_group: str

class ConfigUpdateRequest(BaseModel):
    base_dir: str

class ModelFilters(BaseModel):
    include_tags: List[str] = Field(default_factory=list)
    exclude_tags: List[str] = Field(default_factory=list)

class HardwareProfile(BaseModel):
    description: str
    model_filters: ModelFilters

class Bundle(BaseModel):
    description: str
    workflows: List[str]  # Changed from workflow: str
    models: List[str]
    hardware_profiles: Dict[str, HardwareProfile] = Field(default_factory=dict)
    workflow_params: Optional[Dict[str, Any]] = None

class BundleRequest(BaseModel):
    name: str
    bundle: Bundle

class BundleInstallRequest(BaseModel):
    bundle: str
    profile: str

@jsonmodels_router.get("/", response_model=Dict[str, Any])
def get_models_data(user=Depends(protected)):
    """Récupère l'intégralité du fichier models.json."""
    return load_models_json()

@jsonmodels_router.get("/config", response_model=Dict[str, str])
def get_config(user=Depends(protected)):
    """Récupère la configuration du fichier models.json."""
    data = load_models_json()
    return data.get("config", {})

@jsonmodels_router.post("/config")
def update_config(config: ConfigUpdateRequest, user=Depends(protected)):
    """Met à jour la configuration du fichier models.json."""
    data = load_models_json()
    data["config"] = {"BASE_DIR": config.base_dir}
    save_models_json(data)
    return {"ok": True, "message": "Configuration mise à jour"}

@jsonmodels_router.get("/groups", response_model=List[str])
def get_groups(user=Depends(protected)):
    """Récupère la liste des groupes de modèles."""
    data = load_models_json()
    return list(data.get("groups", {}).keys())

@jsonmodels_router.post("/groups")
def create_group(group_request: ModelGroupRequest, user=Depends(protected)):
    """Crée un nouveau groupe de modèles."""
    data = load_models_json()
    if "groups" not in data:
        data["groups"] = {}
    
    if group_request.group in data["groups"]:
        raise HTTPException(status_code=400, detail=f"Le groupe '{group_request.group}' existe déjà")
    
    data["groups"][group_request.group] = []
    save_models_json(data)
    return {"ok": True, "message": f"Groupe '{group_request.group}' créé"}

@jsonmodels_router.put("/groups")
def update_group_name(update_request: UpdateModelGroupRequest, user=Depends(protected)):
    """Renomme un groupe de modèles."""
    data = load_models_json()
    
    if "groups" not in data:
        raise HTTPException(status_code=404, detail="Aucun groupe trouvé")
    
    if update_request.old_group not in data["groups"]:
        raise HTTPException(status_code=404, detail=f"Le groupe '{update_request.old_group}' n'existe pas")
    
    if update_request.new_group in data["groups"]:
        raise HTTPException(status_code=400, detail=f"Le groupe '{update_request.new_group}' existe déjà")
    
    # Copier le contenu et supprimer l'ancien groupe
    data["groups"][update_request.new_group] = data["groups"][update_request.old_group]
    del data["groups"][update_request.old_group]
    
    # Mettre aussi à jour les références dans les bundles
    if "bundles" in data:
        for bundle_name, bundle in data["bundles"].items():
            if "models" in bundle and update_request.old_group in bundle["models"]:
                # Remplacer l'ancien nom de groupe par le nouveau
                index = bundle["models"].index(update_request.old_group)
                bundle["models"][index] = update_request.new_group
    
    save_models_json(data)
    return {"ok": True, "message": f"Groupe renommé de '{update_request.old_group}' à '{update_request.new_group}'"}

@jsonmodels_router.delete("/groups")
def delete_group(group_request: ModelGroupRequest, user=Depends(protected)):
    """Supprime un groupe de modèles."""
    data = load_models_json()
    
    if "groups" not in data:
        raise HTTPException(status_code=404, detail="Aucun groupe trouvé")
    
    if group_request.group not in data["groups"]:
        raise HTTPException(status_code=404, detail=f"Le groupe '{group_request.group}' n'existe pas")
    
    # Vérifier si le groupe est utilisé dans des bundles
    group_used_in_bundles = []
    if "bundles" in data:
        for bundle_name, bundle in data["bundles"].items():
            if "models" in bundle and group_request.group in bundle["models"]:
                group_used_in_bundles.append(bundle_name)
    
    if group_used_in_bundles:
        raise HTTPException(
            status_code=400, 
            detail=f"Le groupe '{group_request.group}' est utilisé dans les bundles suivants: {', '.join(group_used_in_bundles)}"
        )
    
    del data["groups"][group_request.group]
    save_models_json(data)
    return {"ok": True, "message": f"Groupe '{group_request.group}' supprimé"}

@jsonmodels_router.get("/group/{group_name}", response_model=List[ModelEntry])
def get_group_models(group_name: str, user=Depends(protected)):
    """Récupère tous les modèles d'un groupe spécifique."""
    data = load_models_json()
    
    if "groups" not in data:
        raise HTTPException(status_code=404, detail="Aucun groupe trouvé")
    
    if group_name not in data["groups"]:
        raise HTTPException(status_code=404, detail=f"Le groupe '{group_name}' n'existe pas")
    
    return data["groups"][group_name]

@jsonmodels_router.post("/entry")
def add_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """Ajoute une nouvelle entrée de modèle dans un groupe."""
    data = load_models_json()
    
    if "groups" not in data:
        data["groups"] = {}
    
    if entry_request.group not in data["groups"]:
        data["groups"][entry_request.group] = []
    
    # Vérification de la présence d'une URL ou git
    if not entry_request.entry.url and not entry_request.entry.git:
        raise HTTPException(status_code=400, detail="L'entrée doit contenir soit une URL soit un dépôt git")
    
    # Récupérer le BASE_DIR pour la normalisation des chemins
    base_dir = data.get("config", {}).get("BASE_DIR", "")
    
    # Normaliser le chemin de destination si présent
    if entry_request.entry.dest:
        entry_request.entry.dest = normalize_path(entry_request.entry.dest, base_dir)
    
    # Vérification si le modèle existe déjà dans le groupe par sa destination
    if entry_request.entry.dest:
        for existing_entry in data["groups"][entry_request.group]:
            if existing_entry.get("dest") == entry_request.entry.dest:
                raise HTTPException(status_code=409, detail=f"Un modèle avec cette destination existe déjà dans le groupe '{entry_request.group}'")
    
    # Ajout du modèle au groupe
    data["groups"][entry_request.group].append(entry_request.entry.dict(exclude_none=True))
    save_models_json(data)
    
    return {"ok": True, "message": "Entrée de modèle ajoutée avec succès"}

@jsonmodels_router.put("/entry")
def update_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """Met à jour une entrée de modèle existante."""
    data = load_models_json()
    
    # S'assurer que la structure de groupes existe
    if "groups" not in data:
        data["groups"] = {}
    
    # Récupérer le BASE_DIR pour la normalisation des chemins
    base_dir = data.get("config", {}).get("BASE_DIR", "")
    
    # Normaliser le chemin de destination si présent
    if entry_request.entry.dest:
        entry_request.entry.dest = normalize_path(entry_request.entry.dest, base_dir)
    
    # Créer automatiquement le groupe s'il n'existe pas
    if entry_request.group not in data["groups"]:
        logger.info(f"Création automatique du groupe manquant: {entry_request.group}")
        data["groups"][entry_request.group] = []
    
    # Identifiant pour la recherche
    model_id = entry_request.entry.dest or entry_request.entry.git
    if not model_id:
        raise HTTPException(status_code=400, detail="L'entrée doit contenir soit une destination soit un dépôt git pour l'identification")
    
    # Recherche de l'entrée à mettre à jour
    found = False
    for i, entry in enumerate(data["groups"][entry_request.group]):
        entry_id = entry.get("dest") or entry.get("git")
        if entry_id == model_id:
            data["groups"][entry_request.group][i] = entry_request.entry.dict(exclude_none=True)
            found = True
            break
    
    # Si le modèle n'existe pas, l'ajouter au groupe
    if not found:
        logger.info(f"Modèle non trouvé, ajout automatique au groupe {entry_request.group}")
        data["groups"][entry_request.group].append(entry_request.entry.dict(exclude_none=True))
    
    save_models_json(data)
    message = "Entrée de modèle mise à jour avec succès" if found else "Entrée de modèle ajoutée avec succès"
    return {"ok": True, "message": message}

@jsonmodels_router.delete("/entry")
def delete_model_entry(entry_request: ModelEntryRequest, user=Depends(protected)):
    """Supprime une entrée de modèle existante."""
    data = load_models_json()
    
    if "groups" not in data or entry_request.group not in data["groups"]:
        raise HTTPException(status_code=404, detail=f"Le groupe '{entry_request.group}' n'existe pas")
    
    # Identifiant pour la recherche
    model_id = entry_request.entry.dest or entry_request.entry.git
    if not model_id:
        raise HTTPException(status_code=400, detail="L'entrée doit contenir soit une destination soit un dépôt git pour l'identification")
    
    # Recherche de l'entrée à supprimer
    original_length = len(data["groups"][entry_request.group])
    data["groups"][entry_request.group] = [
        entry for entry in data["groups"][entry_request.group] 
        if (entry.get("dest") or entry.get("git")) != model_id
    ]
    
    if len(data["groups"][entry_request.group]) == original_length:
        raise HTTPException(status_code=404, detail=f"Entrée non trouvée dans le groupe '{entry_request.group}'")
    
    save_models_json(data)
    return {"ok": True, "message": "Entrée de modèle supprimée avec succès"}

@jsonmodels_router.get("/bundles", response_model=Dict[str, Bundle])
def get_bundles(user=Depends(protected)):
    """Récupère tous les bundles disponibles."""
    data = load_models_json()
    return data.get("bundles", {})

@jsonmodels_router.post("/bundle")
def create_bundle(bundle_request: BundleRequest, user=Depends(protected)):
    """Crée un nouveau bundle."""
    data = load_models_json()
    
    if "bundles" not in data:
        data["bundles"] = {}
    
    if bundle_request.name in data["bundles"]:
        raise HTTPException(status_code=400, detail=f"Le bundle '{bundle_request.name}' existe déjà")
    
    # Vérifier que les groupes de modèles référencés existent
    for model_group in bundle_request.bundle.models:
        if model_group not in data.get("groups", {}):
            raise HTTPException(
                status_code=400, 
                detail=f"Le groupe de modèles '{model_group}' référencé dans le bundle n'existe pas"
            )
    
    # Vérifier si le fichier de workflow existe
    workflow_path = os.path.join(WORKFLOW_DIR, bundle_request.bundle.workflow)
    if not os.path.exists(workflow_path):
        logger.warning(f"Le fichier de workflow '{workflow_path}' n'existe pas")
        # C'est juste un avertissement, pas une erreur, car le fichier pourrait être ajouté plus tard
    
    data["bundles"][bundle_request.name] = bundle_request.bundle.dict(exclude_none=True)
    save_models_json(data)
    return {"ok": True, "message": f"Bundle '{bundle_request.name}' créé"}

@jsonmodels_router.put("/bundle")
def update_bundle(bundle_request: BundleRequest, user=Depends(protected)):
    """Met à jour un bundle existant."""
    data = load_models_json()
    
    if "bundles" not in data:
        data["bundles"] = {}
    
    # Vérifier que les groupes de modèles référencés existent
    for model_group in bundle_request.bundle.models:
        if model_group not in data.get("groups", {}):
            raise HTTPException(
                status_code=400, 
                detail=f"Le groupe de modèles '{model_group}' référencé dans le bundle n'existe pas"
            )
    
    was_updated = bundle_request.name in data["bundles"]
    data["bundles"][bundle_request.name] = bundle_request.bundle.dict(exclude_none=True)
    save_models_json(data)
    
    message = f"Bundle '{bundle_request.name}' " + ("mis à jour" if was_updated else "créé")
    return {"ok": True, "message": message}

@jsonmodels_router.delete("/bundle")
def delete_bundle(bundle_name: str = Body(..., embed=True), user=Depends(protected)):
    """Supprime un bundle."""
    data = load_models_json()
    
    if "bundles" not in data or bundle_name not in data["bundles"]:
        raise HTTPException(status_code=404, detail=f"Bundle '{bundle_name}' introuvable")
    
    del data["bundles"][bundle_name]
    save_models_json(data)
    
    return {"ok": True, "message": f"Bundle '{bundle_name}' supprimé"}

@jsonmodels_router.post("/workflow")
async def upload_workflow(
    workflow_file: UploadFile = File(...),
    user=Depends(protected)
):
    """Upload a workflow file to the workflow directory."""
    # Create workflow directory if it doesn't exist
    os.makedirs(WORKFLOW_DIR, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(WORKFLOW_DIR, workflow_file.filename)
    
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(workflow_file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload workflow: {str(e)}")
    
    return {"ok": True, "message": f"Workflow '{workflow_file.filename}' uploaded successfully"}

@jsonmodels_router.get("/workflows", response_model=List[str])
def list_workflows(user=Depends(protected)):
    """List all available workflow files."""
    if not os.path.exists(WORKFLOW_DIR):
        return []
    
    try:
        files = os.listdir(WORKFLOW_DIR)
        return [f for f in files if f.endswith('.json')]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")

@jsonmodels_router.delete("/workflow/{filename}")
def delete_workflow(filename: str, user=Depends(protected)):
    """Delete a workflow file."""
    file_path = os.path.join(WORKFLOW_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Workflow '{filename}' not found")
    
    try:
        os.remove(file_path)
        return {"ok": True, "message": f"Workflow '{filename}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")

def get_installed_bundles_path():
    """Retourne le chemin du fichier de suivi des bundles installés."""
    base_dir = os.environ.get("COMFYUI_MODEL_DIR", ".")
    return os.path.join(base_dir, INSTALLED_BUNDLES_FILE)

def load_installed_bundles():
    """Charge la liste des bundles installés."""
    path = get_installed_bundles_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_installed_bundles(bundles):
    """Sauvegarde la liste des bundles installés."""
    path = get_installed_bundles_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bundles, f, indent=2)

@jsonmodels_router.get("/installed-bundles", response_model=List[str])
def get_installed_bundles(user=Depends(protected)):
    """Get list of installed bundles."""
    bundles = load_installed_bundles()
    # Retourne juste le nom du bundle (et profil) sous forme "bundle:profile"
    return [f"{b['bundle']}:{b['profile']}" for b in bundles]

@jsonmodels_router.post("/install-bundle")
def install_bundle(request: BundleInstallRequest, user=Depends(protected)):
    """Install a bundle with specific hardware profile."""
    data = load_models_json()
    
    if "bundles" not in data or request.bundle not in data["bundles"]:
        raise HTTPException(status_code=404, detail=f"Bundle '{request.bundle}' not found")
    
    bundle = data["bundles"][request.bundle]
    
    if "hardware_profiles" not in bundle or request.profile not in bundle["hardware_profiles"]:
        raise HTTPException(status_code=404, detail=f"Hardware profile '{request.profile}' not found in bundle")
    
    # TODO: Implement the actual installation logic
    # This would involve:
    # 1. Finding all models that match the bundle and profile
    # 2. Downloading the missing models
    # 3. Recording the installation
    
    # For now, we'll just return a success message
    # Enregistrer l'installation
    bundles = load_installed_bundles()
    # Éviter les doublons
    if not any(b["bundle"] == request.bundle and b["profile"] == request.profile for b in bundles):
        bundles.append({"bundle": request.bundle, "profile": request.profile})
        save_installed_bundles(bundles)
    return {"ok": True, "message": f"Bundle '{request.bundle}' with profile '{request.profile}' installed successfully"}

@jsonmodels_router.post("/uninstall-bundle")
def uninstall_bundle(request: BundleInstallRequest, user=Depends(protected)):
    """Uninstall a bundle with specific hardware profile and remove unused files."""
    data = load_models_json()
    bundles = load_installed_bundles()
    # Trouver le bundle à désinstaller
    if "bundles" not in data or request.bundle not in data["bundles"]:
        raise HTTPException(status_code=404, detail=f"Bundle '{request.bundle}' not found")
    bundle = data["bundles"][request.bundle]
    # Retirer l'installation
    bundles = [b for b in bundles if not (b["bundle"] == request.bundle and b["profile"] == request.profile)]
    save_installed_bundles(bundles)

    # 1. Identifier tous les bundles installés restants
    installed_bundle_names = set((b["bundle"], b["profile"]) for b in bundles)
    # 2. Collecter tous les modèles et workflows utilisés par les autres bundles installés
    used_models = set()
    used_workflows = set()
    for b in bundles:
        bdata = data["bundles"].get(b["bundle"])
        if not bdata:
            continue
        # Ajout des modèles
        for group in bdata.get("models", []):
            group_entries = data.get("groups", {}).get(group, [])
            for entry in group_entries:
                if entry.get("dest"):
                    used_models.add(entry["dest"])
        # Ajout des workflows
        for wf in bdata.get("workflows", []):
            used_workflows.add(wf)

    # 3. Pour le bundle à désinstaller, supprimer les fichiers non utilisés ailleurs
    # Modèles
    for group in bundle.get("models", []):
        group_entries = data.get("groups", {}).get(group, [])
        for entry in group_entries:
            dest = entry.get("dest")
            if dest and dest not in used_models:
                # Résoudre le chemin réel
                base_dir = data.get("config", {}).get("BASE_DIR", "")
                if dest.startswith("${BASE_DIR}/"):
                    rel_path = dest.replace("${BASE_DIR}/", "")
                    file_path = os.path.join(base_dir, rel_path)
                else:
                    file_path = dest
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.info(f"Fichier modèle supprimé: {file_path}")
                    except Exception as e:
                        logger.warning(f"Impossible de supprimer le fichier modèle {file_path}: {e}")
    # Workflows
    for wf in bundle.get("workflows", []):
        if wf not in used_workflows:
            wf_path = os.path.join(WORKFLOW_DIR, wf)
            if os.path.exists(wf_path):
                try:
                    os.remove(wf_path)
                    logger.info(f"Fichier workflow supprimé: {wf_path}")
                except Exception as e:
                    logger.warning(f"Impossible de supprimer le workflow {wf_path}: {e}")

    return {"ok": True, "message": f"Bundle '{request.bundle}' with profile '{request.profile}' uninstalled successfully"}

@jsonmodels_router.get("/workflow/{filename}")
def download_workflow(filename: str, download: bool = False, user=Depends(protected)):
    """Get a workflow file."""
    file_path = os.path.join(WORKFLOW_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Workflow '{filename}' not found")
    
    if download:
        # Envoie le fichier en tant que fichier à télécharger
        return FileResponse(
            file_path,
            media_type="application/json",
            filename=filename
        )
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return JSONResponse(
                content=json.loads(content)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read workflow: {str(e)}")
