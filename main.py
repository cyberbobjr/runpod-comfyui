import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api import api_router, decode_jwt  # <-- Import du router API et decode_jwt

app = FastAPI()

# Autorise le frontend Vue.js à accéder à l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend/dist/assets"), name="static")

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)
    if request.url.path.startswith("/static") or request.url.path == "/" or not request.url.path.startswith("/api"):
        return await call_next(request)
    if request.url.path.startswith("/api"):
        if request.url.path == "/api/login":
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

app.include_router(api_router)

@app.get("/")
def serve_vue():
    return FileResponse(os.path.join("frontend", "dist", "index.html"))

@app.get("/{full_path:path}")
def serve_vue_spa(full_path: str):
    # Ne servir index.html que pour les routes qui ne commencent PAS par /api ou /static
    if full_path.startswith("api") or full_path.startswith("static"):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    return FileResponse(os.path.join("frontend", "dist", "index.html"))

