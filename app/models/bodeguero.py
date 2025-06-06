from pydantic import BaseModel
from typing import Optional
from datetime import date

class PiezaInventario(BaseModel):
    id_pieza: int
    nombre: str
    descripcion: str
    numero_serie: Optional[str]
    stock_minimo: int
    fecha_vencimiento: Optional[date]
    alerta_vencimiento: bool
    estado: bool
    id_categoria: int
    id_marca: int
    nombre_marca: str
    desc_marca: Optional[str]
    nombre_categoria: str
    desc_categoria: Optional[str]
    cantidad: int

class StockUpdate(BaseModel):
    id_pieza: int
    cantidad: int
    id_tipo_movimiento: int
    observaciones: Optional[str] = None
