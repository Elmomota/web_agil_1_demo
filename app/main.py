from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import recuperacion
from app.routers import usuario
from app.routers import admin_user


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
app.include_router(admin_user.router)
