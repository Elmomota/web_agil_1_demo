from fastapi import APIRouter, Form
from app.services.usuario import login_usuario

router = APIRouter(prefix="/api", tags=["Usuario"])

@router.post("/login")
def login(correo: str = Form(...), contrasena: str = Form(...)):
    return login_usuario(correo, contrasena)
