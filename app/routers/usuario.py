#app\routers\usuario.py

from fastapi import APIRouter, Form, Query
from app.services.usuario import login_usuario, obtener_id_usuario_por_correo, obtener_id_almacen_por_usuario

router = APIRouter(prefix="/api", tags=["Usuario"])

@router.post("/login")
def login(correo: str = Form(...), contrasena: str = Form(...)):
    return login_usuario(correo, contrasena)


@router.get("/usuario-id")
def get_id_usuario(correo: str = Query(...)):
    return obtener_id_usuario_por_correo(correo)

@router.get("/usuario-almacen")
def get_id_almacen(id_usuario: int = Query(...)):
    return obtener_id_almacen_por_usuario(id_usuario)