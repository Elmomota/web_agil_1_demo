from pydantic import BaseModel
from typing import List, Optional

class InventarioItem(BaseModel):
    id_pieza: int
    nombre: str
    descripcion: Optional[str]
    stock_minimo: int
    stock_actual: int
    almacen: str
    categoria: str
    estado_stock: str

class StockBajoItem(BaseModel):
    id_pieza: int
    nombre: str
    stock_actual: int
    stock_minimo: int
    almacen: str
    categoria: str

class TendenciaItem(BaseModel):
    id_pieza: int
    nombre: str
    descripcion: Optional[str]
    veces_utilizada: int
    total_usada: int
    categoria: str

class ReporteGeneral(BaseModel):
    estado_inventario: List[InventarioItem]
    stock_bajo: List[StockBajoItem]
    tendencias_consumo: List[TendenciaItem]
