from fastapi import APIRouter, HTTPException, Path, Query
from app.models.proyectos import PiezaAsignada, UsuarioProyectoOut, ProyectoResumen
from app.models.proyectos import (
    ProyectoCreate, 
    ProyectoActualizarEstado, 
    AsignarUsuarioProyecto, 
    EliminarUsuarioProyecto, 
    AsignarPiezaProyecto, 
    RemoverPiezaProyecto, 
    PiezaAsignada, 
    UsuarioProyectoOut)
from app.services import proyectos
from typing import List

router = APIRouter(prefix="/proyectos", tags=["Proyectos"])

@router.post("/crear")
def crear(data: ProyectoCreate):
    return proyectos.crear_proyecto(data)

@router.get("/listar", response_model=List[ProyectoResumen])
def ver_todos_proyectos():
    return proyectos.listar_proyectos()

@router.put("/estado")
def cambiar_estado(data: ProyectoActualizarEstado):
    return proyectos.cambiar_estado_proyecto(data)

@router.post("/usuario/asignar")
def asignar_usuario(data: AsignarUsuarioProyecto):
    return proyectos.asignar_usuario_a_proyecto(data)

@router.delete("/usuario/remover")
def remover_usuario(data: EliminarUsuarioProyecto):
    return proyectos.eliminar_usuario_de_proyecto(data)

@router.get("/piezas/{id_proyecto}", response_model=List[PiezaAsignada])
def ver_piezas_asignadas(id_proyecto: int = Path(..., description="ID del proyecto")):
    return proyectos.obtener_piezas_asignadas(id_proyecto)

@router.delete("/piezas/devolver")
def devolver_pieza(
    id_detalle: int = Query(..., description="ID del detalle en detalle_pieza_proyecto"),
    id_proyecto: int = Query(..., description="ID del proyecto asociado"),
    id_usuario: int = Query(..., description="ID del usuario que realiza la devolución"),
    id_almacen: int = Query(..., description="ID del almacén al que se devuelve")
):
    return proyectos.devolver_pieza_proyecto(id_detalle, id_proyecto, id_usuario, id_almacen)

@router.post("/pieza/asignar")
def asignar_pieza(data: AsignarPiezaProyecto):
    return proyectos.asignar_pieza_a_proyecto(data)

@router.delete("/pieza/remover")
def remover_pieza(data: RemoverPiezaProyecto):
    return proyectos.remover_pieza_de_proyecto(data)

@router.put("/usuario/cambiar-rol")
def cambiar_rol_usuario(id_usuario: int = Query(...), id_proyecto: int = Query(...), id_nuevo_rol: int = Query(...)):
    return proyectos.cambiar_rol_usuario_en_proyecto(id_usuario, id_proyecto, id_nuevo_rol)

@router.get("/{id_proyecto}/usuarios", response_model=List[UsuarioProyectoOut])
def usuarios_asignados(id_proyecto: int):
    return proyectos.listar_usuarios_en_proyecto(id_proyecto)