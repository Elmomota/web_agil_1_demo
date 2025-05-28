from fastapi import APIRouter, Form, HTTPException
from app.services.recuperacion import (
    enviar_codigo_recuperacion,
    verificar_codigo_recuperacion,
    actualizar_contrasena
)

router = APIRouter(prefix="/api/user", tags=["Recuperación de Cuenta"])

@router.post("/send-recovery-code")
def send_recovery_code(correo: str = Form(...)):
    return enviar_codigo_recuperacion(correo)

@router.post("/verify-recovery-code")
def verify_code(correo: str = Form(...), codigo: str = Form(...)):
    return verificar_codigo_recuperacion(correo, codigo)

@router.post("/reset-password")
def reset_password(correo: str = Form(...), nueva_contrasena: str = Form(...)):
    return actualizar_contrasena(correo, nueva_contrasena)
