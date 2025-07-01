import os
import shutil
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from back.routers.main import api_router
from back.services.auth_service import AuthService
from back.services.config_service import ConfigService
from back.services.model_manager import ModelManager
from back.version import print_version_info, get_version
from back.utils.logger import get_logger

app = FastAPI(
    title="ComfyUI Model Manager",
    description="API for managing ComfyUI models, workflows and configurations",
    version=get_version()
)

# Initialize logger
logger = get_logger(__name__)

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
        return await call_next(request)    # Ignorer l'authentification pour le frontend et les assets statiques
    if request.url.path == "/" or request.url.path.startswith("/assets") or not request.url.path.startswith("/api"):
        return await call_next(request)
    
    if request.url.path.startswith("/api"):
        # Autoriser la route de login et version sans JWT
        if request.url.path in ["/api/auth/login", "/api/version"]:
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
        
        user = AuthService.decode_jwt(token)
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

# Register the consolidated API router
app.include_router(api_router)
logger.info("Tous les routers ont été enregistrés avec succès")

# Afficher les informations de démarrage
@app.on_event("startup")
async def startup_event():
    # Print version information first
    print_version_info()
    
    logger.info("=== Application démarrée ===")
    logger.info(f"Répertoire de travail: {os.getcwd()}")
    logger.info(f"BASE_DIR: {ConfigService.get_base_dir()}")
    try:
        models_json_path = ModelManager.get_models_json_path()
        logger.info(f"Chemin du fichier models.json: {models_json_path}")
        
        # Vérifier si le fichier models.json existe à l'emplacement cible
        if not os.path.exists(models_json_path):
            # Copier le fichier models.json depuis la racine du projet
            source_models_json = os.path.join(os.getcwd(), "models.json")
            if os.path.exists(source_models_json):
                # Créer le répertoire parent si nécessaire
                os.makedirs(os.path.dirname(models_json_path), exist_ok=True)
                shutil.copy2(source_models_json, models_json_path)
                logger.info(f"Fichier models.json initialisé: copié de {source_models_json} vers {models_json_path}")
            else:
                logger.warning(f"Fichier models.json source non trouvé à la racine: {source_models_json}")
        else:
            logger.info("Fichier models.json existe déjà")
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
    print("""
WARNING: Running the server with `python main.py` does NOT support multiple workers.
For production and to avoid blocking issues during downloads, use the following command instead:

    uvicorn main:app --host 0.0.0.0 --port 8081 --workers 4

You can adjust the number of workers as needed.
""")
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8081))
    uvicorn.run(app, host=host, port=port)

