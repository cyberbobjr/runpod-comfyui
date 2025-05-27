import os
import json
import logging
from fastapi import APIRouter, HTTPException, Depends, Body, File, UploadFile
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from fastapi.responses import JSONResponse, FileResponse
import shutil
from api import protected, get_env_file_path
from model_utils import ModelManager

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création du router pour les routes API du fichier models.json
jsonmodels_router = APIRouter(prefix="/api/jsonmodels")

MODELS_JSON = "models.json"
WORKFLOW_DIR = None  # Sera récupéré dynamiquement

def get_models_json_path():
    """Retourne le chemin complet du fichier models.json en essayant plusieurs emplacements possibles."""
    return ModelManager.get_models_json_path()

def load_models_json():
    """Charge le fichier models.json complet avec gestion des erreurs améliorée."""
    return ModelManager.load_models_json()

def save_models_json(data):
    """Sauvegarde le fichier models.json complet avec gestion des erreurs améliorée."""
    return ModelManager.save_models_json(data)

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
    
    # Si base_dir n'est pas fourni, utiliser le BASE_DIR centralisé
    if not base_dir:
        base_dir = ModelManager.get_base_dir()
    
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

def model_exists_on_disk(entry, base_dir):
    """
    Détermine si le modèle (fichier) existe sur le disque.
    """
    if not base_dir:
        base_dir = ModelManager.get_base_dir()
    return ModelManager.model_exists_on_disk(entry, base_dir)

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

@jsonmodels_router.get("/", response_model=Dict[str, Any])
def get_models_data(user=Depends(protected)):
    """Récupère l'intégralité du fichier models.json et ajoute le champ 'exists' pour chaque modèle."""
    data = load_models_json()
    base_dir = ModelManager.get_base_dir()
    # Ajout du champ 'exists' pour chaque modèle dans chaque groupe
    groups = data.get("groups", {})
    for group_name, entries in groups.items():
        for entry in entries:
            entry["exists"] = model_exists_on_disk(entry, base_dir)
    return data

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
