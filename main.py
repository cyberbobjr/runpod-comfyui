import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api import auth_router, api_router
from api_file_manager import file_router
from api_models import models_router # Importation de notre router unifié
from api_bundle import bundle_router
from api_json_models import jsonmodels_router
from api_workflows import workflows_router
from auth import decode_jwt

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
        
        # Vérifier d'abord le header Authorization
        auth = request.headers.get("authorization")
        token = None
        
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1]
        # Si pas de header, vérifier le paramètre URL pour les téléchargements
        elif request.url.path == "/api/file/download":
            token = request.query_params.get("token")
        
        if not token:
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
app.include_router(auth_router)
app.include_router(file_router)
app.include_router(models_router) # Nouveau router unifié
app.include_router(api_router)
app.include_router(jsonmodels_router)
app.include_router(bundle_router)
app.include_router(workflows_router)

logger.info("Tous les routers ont été enregistrés avec succès")

# Afficher les informations de démarrage
@app.on_event("startup")
async def startup_event():
    logger.info("=== Application démarrée ===")
    logger.info(f"Répertoire de travail: {os.getcwd()}")
    logger.info(f"COMFYUI_MODEL_DIR: {os.environ.get('COMFYUI_MODEL_DIR', 'Non défini')}")
    try:
        from api_models import get_models_json_path
        logger.info(f"Chemin du fichier models.json: {get_models_json_path()}")
    except ImportError:
        logger.error("Impossible d'importer get_models_json_path")

# Monter d'abord les fichiers statiques pour qu'ils soient prioritaires
app.mount("/assets", StaticFiles(directory="front/dist/assets"), name="assets")

# Ensuite, ajouter les routes SPA pour tout le reste
@app.get("/")
async def serve_index():
    logger.info("Serving index.html")
    return FileResponse(os.path.join("front", "dist", "index.html"))

# Cette route doit être placée après les routes spécifiques mais avant le catch-all statique
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Ne pas intercepter les routes API
    if full_path.startswith("api/"):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    logger.info(f"Serving SPA for path: {full_path}")
    return FileResponse(os.path.join("front", "dist", "index.html"))

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8081))
    uvicorn.run(app, host=host, port=port)

