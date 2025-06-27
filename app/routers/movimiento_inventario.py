#app\routers\movimiento_inventario.py
from fastapi import APIRouter, Query
from typing import Optional
from app.services import movimiento_inventario as service
from app.models.movimiento_inventario import MovimientoInventarioOut
from datetime import date

router = APIRouter(prefix="/movimientos", tags=["Movimientos de Inventario"])

@router.get("/sucursal/{id_almacen}", response_model=list[MovimientoInventarioOut])
def listar_por_sucursal(
    id_almacen: int,
    id_movimiento: Optional[int] = Query(None),
    fecha: Optional[date] = Query(None),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    id_pieza: Optional[int] = Query(None),
    id_usuario: Optional[int] = Query(None),
    id_proyecto: Optional[int] = Query(None)
):
    return service.listar_movimientos_por_sucursal(
        id_almacen=id_almacen,
        id_movimiento=id_movimiento,
        fecha=fecha,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        id_pieza=id_pieza,
        id_usuario=id_usuario,
        id_proyecto=id_proyecto
    )

@router.get("/empresa", response_model=list[MovimientoInventarioOut])
def listar_general(
    id_movimiento: Optional[int] = Query(None),
    fecha: Optional[date] = Query(None),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    id_pieza: Optional[int] = Query(None),
    id_usuario: Optional[int] = Query(None),
    id_proyecto: Optional[int] = Query(None),
    id_almacen: Optional[int] = Query(None)
):
    return service.listar_movimientos_generales(
        id_movimiento=id_movimiento,
        fecha=fecha,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        id_pieza=id_pieza,
        id_usuario=id_usuario,
        id_proyecto=id_proyecto,
        id_almacen=id_almacen
    )
