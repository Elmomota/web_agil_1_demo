from pydantic import BaseModel
from typing import Optional
from datetime import date

class PiezaVencidaOut(BaseModel):
    id_pieza: int
    nombre: str
    fecha_vencimiento: date
    nombre_almacen: str

class PiezaStockBajoOut(BaseModel):
    id_pieza: int
    nombre: str
    cantidad: int
    stock_minimo: int
    nombre_almacen: str
