from fastapi import APIRouter, Query
from app.services import alertas
from app.models.alertas import PiezaVencidaOut, PiezaStockBajoOut

router = APIRouter(prefix="/api/alertas", tags=["Alertas de Inventario"])

@router.get("/piezas-vencidas", response_model=list[PiezaVencidaOut])
def get_piezas_vencidas(id_almacen: int = Query(...)):
    return alertas.listar_piezas_vencidas_por_almacen(id_almacen)

@router.get("/stock-bajo", response_model=list[PiezaStockBajoOut])
def get_piezas_stock_bajo(id_almacen: int = Query(...)):
    return alertas.listar_piezas_stock_bajo_por_almacen(id_almacen)
