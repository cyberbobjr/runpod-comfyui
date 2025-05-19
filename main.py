import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from api import api_router, decode_jwt
from file_manager_api import file_router

app = FastAPI()

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
    if request.url.path == "/" or not request.url.path.startswith("/api"):
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
app.include_router(file_router)

@app.get("/")
async def serve_index():
    print("Serve index.html")
    return FileResponse(os.path.join("frontend", "dist", "index.html"))

app.mount("/", StaticFiles(directory="frontend/dist"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8081, reload=True)

