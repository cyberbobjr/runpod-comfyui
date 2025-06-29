import os
import shutil
import json
from fastapi import APIRouter, HTTPException, Depends, Body, UploadFile, File, Form
import logging
from fastapi.responses import FileResponse
from typing import  Optional, Dict, Any
from datetime import datetime
from api import protected  # Utilise la même protection JWT
from model_utils import ModelManager

# Variable globale pour activer/désactiver le débogage
DEBUG = True

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_router = APIRouter(prefix="/api/file")

def safe_join(base, *paths):
    # Empêche les accès hors du dossier autorisé
    base = os.path.abspath(base)
    path = os.path.abspath(os.path.join(base, *paths))
    if not path.startswith(base):
        raise HTTPException(status_code=403, detail="Accès interdit")
    return path

def get_base_dir():
    """Utilise la méthode centralisée pour obtenir le BASE_DIR."""
    return ModelManager.get_base_dir()

BASE_DIR = get_base_dir()

# Fonction pour trouver le fichier models.json, en cherchant récursivement si nécessaire
def find_models_json():
    """Utilise la méthode centralisée pour trouver models.json."""
    return ModelManager.get_models_json_path()

# Fonction utilitaire pour obtenir la liste des modèles enregistrés avec leurs chemins normalisés et leurs tailles
def get_registered_models() -> Dict[str, Any]:
    registered_files = {}
    
    # Trouver le fichier models.json
    models_path = find_models_json()
    
    if not models_path or not os.path.isfile(models_path):
        if DEBUG:
            print(f"[DEBUG] No models.json file found")
        return registered_files
    
    try:
        if DEBUG:
            print(f"[DEBUG] Reading models.json from: {models_path}")
        
        models_data = ModelManager.load_models_json()
        base_dir = ModelManager.get_base_dir()
        
        # Récupérer la configuration BASE_DIR du fichier models.json s'il existe
        # config_base_dir = None
        # if "config" in models_data and "BASE_DIR" in models_data["config"]:
        #     config_base_dir = models_data["config"]["BASE_DIR"]
        #     if DEBUG:
        #         print(f"[DEBUG] models.json CONFIG BASE_DIR: {config_base_dir}")
        
        # Parcourir la structure du fichier models.json qui est organisé en groupes
        if "groups" in models_data:
            for group_name, models in models_data["groups"].items():
                if DEBUG:
                    print(f"[DEBUG] Processing group: {group_name}, models count: {len(models)}")
                
                for model in models:
                    if "dest" in model:
                        dest_path = model["dest"]
                        # Récupérer la taille déclarée si elle existe
                        declared_size = model.get("size", None)
                        # Récupérer le lien source si disponible
                        source_url = model.get("src", None)
                        
                        if DEBUG:
                            print(f"[DEBUG] Original dest path: {dest_path}, declared size: {declared_size}, source: {source_url}")
                        
                        # Extraire le chemin relatif après ${BASE_DIR}
                        if "${BASE_DIR}" in dest_path:
                            # Capturer tout ce qui vient après ${BASE_DIR}/
                            rel_path = dest_path.replace("${BASE_DIR}/", "").replace("${BASE_DIR}\\", "")
                            # Normaliser le chemin (remplacer \ par /)
                            norm_path = rel_path.replace("\\", "/")
                            
                            # Stocker le chemin et la taille déclarée
                            registered_files[norm_path] = {
                                "is_registered": True,
                                "declared_size": declared_size,
                                "source_url": source_url
                            }
                            
                            # Pour adapter à différentes structures de chemins, stocker aussi une variante sans préfixe "models/"
                            if norm_path.startswith("models/"):
                                alt_path = norm_path[7:]  # enlever "models/"
                                registered_files[alt_path] = {
                                    "is_registered": True,
                                    "declared_size": declared_size,
                                    "source_url": source_url
                                }
                            
                            # Stocker aussi la version avec slashes inversés pour la compatibilité Windows
                            win_path = rel_path.replace("/", "\\")
                            registered_files[win_path] = {
                                "is_registered": True,
                                "declared_size": declared_size,
                                "source_url": source_url
                            }
                            
                            if DEBUG:
                                print(f"[DEBUG] Added model path: {norm_path}")
                
        if DEBUG:
            print(f"[DEBUG] Total registered models: {len(registered_files)}")
            print(f"[DEBUG] Sample registered paths: {list(registered_files.keys())[:5]}...")
            
    except (json.JSONDecodeError, IOError) as e:
        if DEBUG:
            print(f"[DEBUG] Error reading models.json: {str(e)}")
    
    return registered_files

@file_router.get("/list_dirs")
def list_dirs(path: Optional[str] = "", user=Depends(protected)):
    abs_path = safe_join(BASE_DIR, path)
    if not os.path.isdir(abs_path):
        raise HTTPException(status_code=400, detail="Not a directory")
    try:
        dirs = [d for d in os.listdir(abs_path) if os.path.isdir(os.path.join(abs_path, d))]
        if DEBUG:
            print(f"[DEBUG] Directories in {abs_path}: {dirs}")
        # Use "name" instead of "label"
        return [
            {
                "name": d,
                "path": path + "/" + d if path else d,
                "children": None  # lazy loading
            }
            for d in dirs
        ]
    except Exception as e:
        if DEBUG:
            print(f"[DEBUG] Error listing directories in {abs_path}: {e}")
        raise HTTPException(status_code=500, detail="Error listing directories")

@file_router.get("/list_all_dirs")
def list_all_dirs(user=Depends(protected)):
    """Return the complete directory structure in a hierarchical format"""
    def scan_dir(current_path=""):
        abs_path = safe_join(get_base_dir(), current_path)
        logger.debug(f"list_all_dirs: {abs_path}")
        if not os.path.isdir(abs_path):
            return []
            
        result = []
        try:
            dirs = [d for d in os.listdir(abs_path) if os.path.isdir(os.path.join(abs_path, d))]
            for d in dirs:
                dir_path = os.path.join(current_path, d) if current_path else d
                children = scan_dir(dir_path)
                result.append({
                    "name": d,  # Use "name" instead of "label"
                    "path": dir_path,
                    "children": children
                })
        except (PermissionError, OSError) as e:
            # Skip directories we can't access
            pass
        
        return result
    
    return scan_dir()

@file_router.get("/list_files")
def list_files(path: Optional[str] = "", user=Depends(protected)):
    abs_path = safe_join(BASE_DIR, path)
    if not os.path.isdir(abs_path):
        raise HTTPException(status_code=400, detail="Not a directory")
    
    if DEBUG:
        print(f"[DEBUG] list_files - Current path: {path}, Absolute path: {abs_path}")
    
    # Récupérer le dictionnaire des modèles enregistrés
    registered_models = get_registered_models()
    
    # Liste des fichiers avec un indicateur si le fichier est enregistré
    files_list = []
    for f in os.listdir(abs_path):
        file_path = os.path.join(abs_path, f)
        if os.path.isfile(file_path):
            # Récupérer la taille actuelle du fichier
            actual_size = os.path.getsize(file_path)
            
            # Variables pour suivre le statut du fichier
            is_registered = False
            is_corrupted = False
            expected_size = None
            source_url = None
            
            # Plusieurs façons de normaliser le chemin pour augmenter les chances de correspondance
            normalized_path1 = path.replace("\\", "/")
            if normalized_path1 and not normalized_path1.endswith("/"):
                normalized_path1 += "/"
            file_rel_path1 = normalized_path1 + f
            
            # Variante sans le préfixe "models/"
            normalized_path2 = normalized_path1
            if normalized_path2.startswith("models/"):
                normalized_path2 = normalized_path2[7:]  # enlever "models/"
            file_rel_path2 = normalized_path2 + f
            
            # Variante avec slashes inversés pour Windows
            normalized_path3 = path.replace("/", "\\")
            if normalized_path3 and not normalized_path3.endswith("\\"):
                normalized_path3 += "\\"
            file_rel_path3 = normalized_path3 + f
            
            # Vérifier toutes les variantes pour trouver les métadonnées du fichier
            file_metadata = None
            if file_rel_path1 in registered_models:
                file_metadata = registered_models[file_rel_path1]
            elif file_rel_path2 in registered_models:
                file_metadata = registered_models[file_rel_path2]
            elif file_rel_path3 in registered_models:
                file_metadata = registered_models[file_rel_path3]
            
            # Déterminer si le fichier est enregistré et s'il est corrompu
            if file_metadata:
                is_registered = file_metadata.get("is_registered", False)
                declared_size = file_metadata.get("declared_size", None)
                source_url = file_metadata.get("source_url", None)
                
                if declared_size is not None:
                    expected_size = declared_size
                    # Tolérer une petite différence de taille (0.1%)
                    size_difference_percentage = abs(actual_size - declared_size) / declared_size * 100
                    is_corrupted = size_difference_percentage > 0.1
                    
                    if DEBUG and is_corrupted:
                        print(f"[DEBUG] Corrupted file detected: {f}")
                        print(f"[DEBUG] Expected size: {declared_size}, Actual size: {actual_size}")
                        print(f"[DEBUG] Difference: {size_difference_percentage:.2f}%")
            
            if DEBUG:
                print(f"[DEBUG] Checking file: {file_rel_path1}, Registered: {is_registered}, Corrupted: {is_corrupted}")
            
            files_list.append({
                "name": f,
                "is_registered": is_registered,
                "is_corrupted": is_corrupted,
                "expected_size": expected_size,
                "actual_size": actual_size,
                "source_url": source_url
            })
    
    return {"files": files_list}

@file_router.post("/copy")
def copy_file(src: str = Body(...), dst: str = Body(...), user=Depends(protected)):
    abs_src = safe_join(BASE_DIR, src)
    abs_dst = safe_join(BASE_DIR, dst)
    if not os.path.isfile(abs_src):
        raise HTTPException(status_code=404, detail="Source file not found")
    dst_dir = os.path.dirname(abs_dst)
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy2(abs_src, abs_dst)
    return {"ok": True}

@file_router.post("/delete")
def delete_file(data: Dict[str, str] = Body(...), user=Depends(protected)):
    path = data.get("path", "")
    if not path:
        raise HTTPException(status_code=400, detail="Path parameter is required")
    
    abs_path = safe_join(BASE_DIR, path)
    if DEBUG:
        print(f"[DEBUG] Requested path: {path}")
        print(f"[DEBUG] Absolute path: {abs_path}")
    
    if os.path.isfile(abs_path):
        os.remove(abs_path)
        return {"ok": True}
    elif os.path.isdir(abs_path):
        shutil.rmtree(abs_path)
        return {"ok": True}
    else:
        if DEBUG:
            print(f"[DEBUG] Path not found: {abs_path}")
        raise HTTPException(status_code=404, detail="File or directory not found")

@file_router.post("/rename")
def rename_file(src: str = Body(...), dst: str = Body(...), user=Depends(protected)):
    abs_src = safe_join(BASE_DIR, src)
    abs_dst = safe_join(BASE_DIR, dst)
    if not os.path.exists(abs_src):
        raise HTTPException(status_code=404, detail="Source not found")
    dst_dir = os.path.dirname(abs_dst)
    os.makedirs(dst_dir, exist_ok=True)
    os.rename(abs_src, abs_dst)
    return {"ok": True}

@file_router.get("/properties")
def file_properties(path: str, user=Depends(protected)):
    abs_path = safe_join(BASE_DIR, path)
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="File not found")
    stat = os.stat(abs_path)
    return {
        "size": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "is_dir": os.path.isdir(abs_path),
        "is_file": os.path.isfile(abs_path),
        "name": os.path.basename(abs_path),
        "path": os.path.relpath(abs_path, BASE_DIR)
    }

@file_router.get("/download")
def download_file(path: str, token: Optional[str] = None, user=Depends(protected)):
    abs_path = safe_join(BASE_DIR, path)
    if not os.path.isfile(abs_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    filename = os.path.basename(abs_path)
    
    return FileResponse(
        abs_path, 
        filename=filename,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        }
    )

@file_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    path: str = Form(...),
    user=Depends(protected)
):
    # Vérifier que le chemin cible est valide
    abs_dir = safe_join(BASE_DIR, path)
    if not os.path.isdir(abs_dir):
        os.makedirs(abs_dir, exist_ok=True)
    
    # Créer le chemin complet du fichier
    abs_path = os.path.join(abs_dir, file.filename)
    
    # Sauvegarder le fichier
    try:
        with open(abs_path, "wb") as buffer:
            # Lire et écrire le fichier par morceaux (pour gérer les gros fichiers)
            chunk_size = 1024 * 1024  # 1MB
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                buffer.write(chunk)
        
        return {"filename": file.filename, "path": os.path.relpath(abs_path, BASE_DIR)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@file_router.get("/models_info")
def get_models_info(user=Depends(protected)):
    """Retourne les informations de tous les modèles enregistrés dans models.json"""
    models_path = os.path.join(BASE_DIR, "models.json")
    
    # Si le fichier n'existe pas, retourner une liste vide
    if not os.path.isfile(models_path):
        return {"models": [], "paths": []}
    
    try:
        with open(models_path, "r", encoding="utf-8") as f:
            models_data = json.load(f)
        
        # Extraire juste les chemins des fichiers pour une vérification facile côté client
        file_paths = []
        for model in models_data:
            if "path" in model:
                # Normaliser le chemin pour la comparaison
                normalized_path = model["path"].replace("\\", "/")
                if normalized_path.startswith("./"):
                    normalized_path = normalized_path[2:]
                file_paths.append(normalized_path)
        
        return {
            "models": models_data,
            "paths": file_paths
        }
    except (json.JSONDecodeError, IOError) as e:
        raise HTTPException(status_code=500, detail=f"Error reading models.json: {str(e)}")

@file_router.post("/create_dir")
def create_directory(data: Dict[str, str] = Body(...), user=Depends(protected)):
    path = data.get("path", "")
    if not path:
        raise HTTPException(status_code=400, detail="Path parameter is required")
    
    abs_path = safe_join(BASE_DIR, path)
    try:
        os.makedirs(abs_path, exist_ok=False)
        return {"ok": True}
    except FileExistsError:
        raise HTTPException(status_code=400, detail="Directory already exists")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to create directory: {str(e)}")
