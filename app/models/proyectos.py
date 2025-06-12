from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class ProyectoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str]
    id_estado: int
    id_usuario_responsable: int
    fecha_fin: Optional[date]


class ProyectoActualizarEstado(BaseModel):
    id_proyecto: int
    id_estado: int



class AsignarUsuarioProyecto(BaseModel):
    id_usuario: int
    id_proyecto: int
    id_rol_proyecto: int

class EliminarUsuarioProyecto(BaseModel):
    id_usuario: int
    id_proyecto: int

class AsignarPiezaProyecto(BaseModel):
    id_detalle: int
    id_proyecto: int
    id_pieza: int
    cantidad: int
    id_kit: Optional[int] = None

class RemoverPiezaProyecto(BaseModel):
    id_detalle: int
    id_proyecto: int

class PiezaAsignada(BaseModel):
    id_pieza: int
    nombre_pieza: str
    cantidad: int
    fecha_asignacion: datetime
    nombre_kit: Optional[str] = None

class PiezaAsignada(BaseModel):
    id_pieza: int
    nombre_pieza: str
    cantidad: int
    fecha_asignacion: datetime
    nombre_kit: Optional[str] = None

class UsuarioProyectoOut(BaseModel):
    id_usuario: int
    nombre_usuario: str
    correo: str
    rol: str

class ProyectoResumen(BaseModel):
    id_proyecto: int
    nombre: str
    descripcion: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    estado: str