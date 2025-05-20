import os
import json
import logging
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from fastapi.responses import JSONResponse
from api import protected, get_env_file_path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création du router pour les routes API du fichier models.json
jsonmodels_router = APIRouter(prefix="/api/jsonmodels")

MODELS_JSON = "models.json"

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
            empty_data = {"config": {"BASE_DIR": ""}, "groups": {}}
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
    # Correction de l'expression ternaire pour utiliser la syntaxe Python
    return {"ok": True, "message": "Entrée de modèle mise à jour avec succès" if found else "Entrée de modèle ajoutée avec succès"}

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
