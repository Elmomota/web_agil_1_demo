from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import recuperacion
from app.routers import usuario
from app.routers import admin_user
from app.routers import piezas

import multiprocessing

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8100"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(recuperacion.router)
app.include_router(usuario.router)
app.include_router(piezas.router, prefix= "/api")
app.include_router(admin_user.router)

if __name__ == "__main__":
    multiprocessing.freeze_support()  # Importante para Windows y PyInstaller
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)