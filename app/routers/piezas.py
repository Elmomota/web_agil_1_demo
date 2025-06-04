#C:\Vicente\GitHub\web_agil_1_demo\app\routers\piezas.py
from fastapi import APIRouter, HTTPException
from app.models.piezas import *
from app.services import piezas

router = APIRouter(prefix="/gestion_piezas", tags=["Gestion Piezas"])

# === PIEZAS ===

@router.get("/piezas", response_model=list[PiezaOut])
def listar_piezas():
    return piezas.listar_piezas()

@router.post("/piezas")
def agregar_pieza(data: PiezaCreate):
    piezas.crear_pieza(data)
    return {"message": "Pieza agregada correctamente"}

@router.put("/piezas/{id_pieza}")
def actualizar_pieza(id_usuario: int, id_pieza: int, data: PiezaUpdate):
    piezas.actualizar_pieza(id_usuario, id_pieza, data)
    return {"message": "Pieza actualizada correctamente"}

@router.delete("/piezas/{id_pieza}")
def eliminar_pieza(id_pieza: int):
    piezas.eliminar_pieza(id_pieza)
    return {"message": "Pieza eliminada correctamente"}

# === KITS ===

@router.get("/kits", response_model=list[KitOut])
def listar_kits():
    return piezas.listar_kits()

@router.post("/kits")
def agregar_kit(data: KitCreate):
    piezas.crear_kit(data)
    return {"message": "Kit agregado correctamente"}

@router.put("/kits/{id_kit}")
def actualizar_kit(id_kit: int, data: KitUpdate):
    piezas.actualizar_kit(id_kit, data)
    return {"message": "Kit actualizado correctamente"}

@router.delete("/kits/{id_kit}")
def eliminar_kit(id_kit: int):
    piezas.eliminar_kit(id_kit)
    return {"message": "Kit eliminado correctamente"}

# === KIT-PIEZA ===

@router.get("/kit_piezas/{id_kit}", response_model=list[KitPiezaOut])
def listar_kit_piezas(id_kit: int):
    return piezas.listar_kit_piezas(id_kit)

@router.post("/kit_piezas")
def agregar_kit_pieza(data: KitPiezaCreate):
    piezas.agregar_kit_pieza(data.id_kit, data.id_pieza, data.cantidad)
    return {"message": "Pieza agregada al kit correctamente"}

@router.put("/kit_piezas")
def actualizar_kit_pieza(data: KitPiezaUpdateFull):
    piezas.actualizar_kit_pieza(data.id_kit, data.id_pieza, data.cantidad)
    return {"message": "Cantidad actualizada correctamente"}

@router.delete("/kit_piezas")
def eliminar_kit_pieza(id_kit: int, id_pieza: int):
    piezas.eliminar_kit_pieza(id_kit, id_pieza)
    return {"message": "Pieza eliminada del kit"}
