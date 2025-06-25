#app\routers\auxiliares.py
from fastapi import APIRouter
from app.services import auxiliares

router = APIRouter(prefix="/combobox", tags=["Comboboxes"])

@router.get("/tipos-usuario")
def get_tipos_usuario():
    return auxiliares.obtener_tipos_usuario()

@router.get("/regiones")
def get_regiones():
    return auxiliares.obtener_regiones()

@router.get("/comunas")
def get_comunas(region_id: int):
    return auxiliares.obtener_comunas_por_region(region_id)

@router.get("/movimientos")
def get_tipos_movimiento():
    return auxiliares.obtener_tipos_movimiento()

@router.get("/categorias")
def get_categorias():
    return auxiliares.obtener_categorias()

@router.get("/marcas")
def get_marcas():
    return auxiliares.obtener_marcas()

@router.get("/estados-proyecto")
def get_estados_proyecto():
    return auxiliares.obtener_estados_proyecto()

@router.get("/roles-proyecto")
def get_roles_proyecto():
    return auxiliares.obtener_roles_proyecto()

@router.get("/almacenes")
def get_almacenes():
    return auxiliares.obtener_almacenes()


@router.get("/piezas")
def get_piezas():
    return auxiliares.obtener_piezas_disponibles()
