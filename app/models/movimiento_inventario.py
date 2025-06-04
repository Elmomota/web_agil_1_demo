from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MovimientoInventarioOut(BaseModel):
    id_movimiento: int
    nombre_pieza: str
    nombre_tipo_movimiento: str
    cantidad: int
    fecha: datetime
    nombre_usuario: str
    nombre_proyecto: Optional[str]
    nombre_almacen: str
    observaciones: Optional[str]
