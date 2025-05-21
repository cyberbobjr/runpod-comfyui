import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from api import api_router, decode_jwt, auth_router
from file_manager_api import file_router
from jsonmodels import jsonmodels_router

app = FastAPI()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Autorise le frontend Vue.js à accéder à l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)
    # Ignorer l'authentification pour le frontend et les assets statiques
    if request.url.path == "/" or request.url.path.startswith("/assets") or not request.url.path.startswith("/api"):
        return await call_next(request)
    if request.url.path.startswith("/api"):
        # Autoriser la route de login sans JWT
        if request.url.path == "/api/auth/login":
            return await call_next(request)
        auth = request.headers.get("authorization")
        if not auth or not auth.lower().startswith("bearer "):
            # Ajoute les headers CORS à la réponse 401
            return JSONResponse(
                status_code=401,
                content={"detail": "Non authentifié"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
            )
        token = auth.split(" ", 1)[1]
        user = decode_jwt(token)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token invalide ou expiré"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
            )
    return await call_next(request)

# Enregistrer les routers
app.include_router(api_router)
app.include_router(file_router)
app.include_router(auth_router)
app.include_router(jsonmodels_router)
logger.info("Tous les routers ont été enregistrés avec succès")

# Afficher les informations de démarrage
@app.on_event("startup")
async def startup_event():
    logger.info("=== Application démarrée ===")
    logger.info(f"Répertoire de travail: {os.getcwd()}")
    logger.info(f"COMFYUI_MODEL_DIR: {os.environ.get('COMFYUI_MODEL_DIR', 'Non défini')}")
    try:
        from jsonmodels import get_models_json_path
        logger.info(f"Chemin du fichier models.json: {get_models_json_path()}")
    except ImportError:
        logger.error("Impossible d'importer get_models_json_path")

# Monter d'abord les fichiers statiques pour qu'ils soient prioritaires
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

# Ensuite, ajouter les routes SPA pour tout le reste
@app.get("/")
async def serve_index():
    logger.info("Serving index.html")
    return FileResponse(os.path.join("frontend", "dist", "index.html"))

# Cette route doit être placée après les routes spécifiques mais avant le catch-all statique
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Ne pas intercepter les routes API (corrigé pour être strict)
    if full_path.startswith("api/"):
        # Laisser FastAPI gérer la 404 pour les routes API inconnues
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    logger.info(f"Serving SPA for path: {full_path}")
    return FileResponse(os.path.join("frontend", "dist", "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8082, reload=True)

