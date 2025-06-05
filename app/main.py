from threading import Thread
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import recuperacion
from app.routers import usuario
from app.routers import admin_user
from app.routers import piezas
from app.routers import bodeguero
from app.routers import movimiento_inventario
from app.services.verificador import verificar_piezas_vencidas

import multiprocessing

def scheduler():
    while True:
        print("Verificando piezas vencidas...")
        verificar_piezas_vencidas()
        time.sleep(60 * 5)  # cada 5 minutos para demo

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Lifespan iniciado")
    t = Thread(target=scheduler, daemon=True)
    t.start()
    yield  # Aquí arranca la app
    print("🛑 Lifespan finalizado")


app = FastAPI(lifespan=lifespan)

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
app.include_router(admin_user.router, prefix= "/api")
app.include_router(bodeguero.router, prefix= "/api")
app.include_router(movimiento_inventario.router, prefix= "/api")







if __name__ == "__main__":
    multiprocessing.freeze_support()  # Importante para Windows y PyInstaller
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)