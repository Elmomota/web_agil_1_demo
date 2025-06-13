from fastapi import APIRouter, HTTPException, Path
from app.services import bodega
from app.models.bodega import BodegaCreate, BodegaUpdate

router = APIRouter(prefix="/bodegas", tags=["Bodegas"])

@router.get("/listar")
def listar():
    return bodega.listar_bodegas()

@router.post("/crear")
def crear(b: BodegaCreate):
    return bodega.agregar_bodega(b)

@router.put("/editar/{id_almacen}")
def editar(id_almacen: int, b: BodegaUpdate):
    return bodega.editar_bodega(id_almacen, b)

@router.delete("/eliminar/{id_almacen}")
def eliminar(id_almacen: int):
    return bodega.eliminar_bodega(id_almacen)