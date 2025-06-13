from pydantic import BaseModel
from typing import Optional

class BodegaBase(BaseModel):
    nombre: str
    direccion: str
    id_comuna: int

class BodegaCreate(BodegaBase):
    pass

class BodegaUpdate(BodegaBase):
    estado: Optional[bool] = True

class BodegaOut(BodegaBase):
    id_almacen: int
    estado: bool