from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List

from app.services import admin_user as admin_user_service
from app.services.admin_user import crear_usuario, editar_usuario, eliminar_usuario, listar_usuarios_service
from app.models.usuario import UsuarioCreate, UsuarioEdit, UsuarioOutExtendido

router = APIRouter(prefix="/admin/usuarios", tags=["Administración de Usuarios"])


@router.post("/crear-usuario")
def crear_usuario_endpoint(usuario: UsuarioCreate):
    return crear_usuario(usuario)

@router.put("/editar", response_model=Dict[str, str])
def editar_usuario_endpoint(usuario: UsuarioEdit):
    return editar_usuario(usuario)

@router.delete("/eliminar/{id_usuario}", response_model=Dict[str, str])
def eliminar_usuario_endpoint(id_usuario: int):
    return eliminar_usuario(id_usuario)

@router.get("/listar", response_model=List[UsuarioOutExtendido])
def listar_usuarios():
    return listar_usuarios_service()

@router.put("/desactivar", response_model=Dict[str, str])
def desactivar_usuario(id_usuario: int = Query(...)):
    return admin_user_service.desactivar_usuario(id_usuario)
