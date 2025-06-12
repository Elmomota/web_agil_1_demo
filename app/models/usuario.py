from pydantic import BaseModel
from typing import Optional

# Este modelo se usa para retornar datos al frontend (sin contraseña)
class Usuario(BaseModel):
    id_usuario: int
    nombre: str
    correo: str
    direccion: Optional[str]
    id_comuna: int
    id_tipo_usuario: int
    id_almacen: Optional[int]
    estado: bool

# Este modelo se puede usar para registro o creación si lo deseas
class UsuarioCreate(BaseModel):
    nombre: str
    correo: str
    contrasena: str
    direccion: Optional[str]
    id_comuna: int
    id_tipo_usuario: int
    id_almacen: Optional[int]

# Este modelo se usa para editar un usuario existente
class UsuarioEdit(BaseModel):
    id_usuario: int
    nombre: str
    correo: str
    direccion: Optional[str]
    id_comuna: int
    id_tipo_usuario: int
    id_almacen: Optional[int]
    estado: bool

class UsuarioOutExtendido(BaseModel):
    id_usuario: int
    nombre: str
    correo: str
    direccion: Optional[str]
    nombre_comuna: str
    nombre_tipo_usuario: str
    id_almacen: Optional[int]
    estado: bool