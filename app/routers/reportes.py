from fastapi import APIRouter, HTTPException, Body
from pydantic import EmailStr
from app.services import reportes
from app.models.reportes import ReporteGeneral

router = APIRouter(prefix="/reportes", tags=["Reportes"])

# ────────────────────────────────────────────────
# 🧩 FASE 1: VISUALIZACIÓN - Reportes JSON (GET)
# ────────────────────────────────────────────────

@router.get("/general", response_model=ReporteGeneral)
def obtener_reporte_general():
    """
    Retorna un JSON con todos los reportes (estado, stock bajo, tendencias)
    """
    try:
        return reportes.obtener_reporte_general()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte general: {str(e)}")

@router.get("/estado-inventario")
def obtener_estado():
    """
    Retorna el estado actual del inventario
    """
    return reportes.obtener_estado_inventario()

@router.get("/stock-bajo")
def obtener_stock_bajo():
    """
    Retorna solo piezas con stock bajo
    """
    return reportes.obtener_stock_bajo()

@router.get("/tendencias-consumo")
def obtener_tendencias():
    """
    Retorna piezas más utilizadas (por cantidad total y frecuencia)
    """
    return reportes.obtener_tendencias_consumo()

# ────────────────────────────────────────────────
# ✉️ FASE 3: ENVÍO - Reportes por correo (POST)
# ────────────────────────────────────────────────

@router.post("/general/enviar")
def enviar_reporte_general(destinatario: EmailStr = Body(...)):
    """
    Genera el Excel completo y lo envía por correo
    """
    return reportes.generar_y_enviar_reporte_general(destinatario)

@router.post("/estado-inventario/enviar")
def enviar_reporte_estado(destinatario: EmailStr = Body(...)):
    """
    Genera el Excel de estado actual y lo envía por correo
    """
    return reportes.generar_y_enviar_reporte_estado(destinatario)

@router.post("/stock-bajo/enviar")
def enviar_reporte_stock_bajo(destinatario: EmailStr = Body(...)):
    """
    Genera el Excel de piezas con stock bajo y lo envía por correo
    """
    return reportes.generar_y_enviar_reporte_stock_bajo(destinatario)

@router.post("/tendencias-consumo/enviar")
def enviar_reporte_tendencias(destinatario: EmailStr = Body(...)):
    """
    Genera el Excel de tendencias de consumo y lo envía por correo
    """
    return reportes.generar_y_enviar_reporte_tendencias(destinatario)
