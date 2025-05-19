import os
import shutil
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional
from datetime import datetime
from api import protected  # Utilise la même protection JWT

file_router = APIRouter(prefix="/file")

def safe_join(base, *paths):
    # Empêche les accès hors du dossier autorisé
    base = os.path.abspath(base)
    path = os.path.abspath(os.path.join(base, *paths))
    if not path.startswith(base):
        raise HTTPException(status_code=403, detail="Accès interdit")
    return path

BASE_DIR = os.environ.get("COMFYUI_MODEL_DIR", ".")

@file_router.get("/list_dirs")
def list_dirs(path: Optional[str] = "", user=Depends(protected)):
    abs_path = safe_join(BASE_DIR, path)
    if not os.path.isdir(abs_path):
        raise HTTPException(status_code=400, detail="Not a directory")
    dirs = [d for d in os.listdir(abs_path) if os.path.isdir(os.path.join(abs_path, d))]
    return {"dirs": dirs}

@file_router.get("/list_files")
def list_files(path: Optional[str] = "", user=Depends(protected)):
    abs_path = safe_join(BASE_DIR, path)
    if not os.path.isdir(abs_path):
        raise HTTPException(status_code=400, detail="Not a directory")
    files = [f for f in os.listdir(abs_path) if os.path.isfile(os.path.join(abs_path, f))]
    return {"files": files}

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
def delete_file(path: str = Body(...), user=Depends(protected)):
    abs_path = safe_join(BASE_DIR, path)
    if os.path.isfile(abs_path):
        os.remove(abs_path)
        return {"ok": True}
    elif os.path.isdir(abs_path):
        shutil.rmtree(abs_path)
        return {"ok": True}
    else:
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
