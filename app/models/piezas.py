from pydantic import BaseModel
from typing import Optional


#MODELOES DE LA TABLA PIEZA
class PiezaBase(BaseModel):
    nombre: Optional[str]
    id_marca: Optional[int]
    descripcion: Optional[str]
    numero_serie: Optional[str]
    imagen_referencial: Optional[bytes]
    stock_minimo: Optional[int]
    id_categoria: Optional[int]
    fecha_vencimiento: Optional[str] # formato YYYY-MM-DD

class PiezaCreate(PiezaBase):
    nombre: str
    id_marca: int
    stock_minimo: int
    id_categoria: int
    id_almacen: int  # NUEVO
    cantidad: Optional[int] = 0  # NUEVO

class PiezaUpdate(PiezaBase):
    pass # todos los campos opcionales

class PiezaOut(BaseModel):
    id_pieza: int
    nombre: str
    id_marca: int
    marca: str
    id_categoria: int
    categoria: str
    descripcion: Optional[str]
    numero_serie: Optional[str]
    imagen_referencial: Optional[bytes]
    stock_minimo: int
    fecha_vencimiento: Optional[str]
    alerta_vencimiento: bool
    estado: bool


#MODELOS DE LA TABLA KIT

class KitBase(BaseModel):
    nombre: Optional[str]
    descripcion: Optional[str]

class KitCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class KitUpdate(KitBase):
    pass

class KitOut(BaseModel):
    id_kit: int
    nombre: str
    descripcion: Optional[str]
    estado: bool


#MODELOS DE KIT_PIEZA

class KitPiezaBase(BaseModel):
    id_kit: int
    id_pieza: int
    cantidad: int

class KitPiezaUpdate(BaseModel):
    cantidad: int


class KitPiezaCreate(BaseModel):
    id_kit: int
    id_pieza: int
    cantidad: int

class KitPiezaOut(BaseModel):
    id_kit: int
    id_pieza: int
    cantidad: int
    nombre_pieza: str
    descripcion_pieza: Optional[str] = ''