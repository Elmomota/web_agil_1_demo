from fastapi import APIRouter, Query
from app.services import bodeguero
from app.models import bodeguero as schema

router = APIRouter(prefix="/bodega", tags=["Bodega"])

@router.get("/inventario/{id_usuario}", response_model=list[schema.PiezaInventario])
def listar_inventario(
    id_usuario: int,
    search: str = Query(None, description="Búsqueda por nombre o descripción"),
    id_categoria: int = Query(None, description="Filtrar por ID de categoría")
):
    return bodeguero.obtener_inventario_usuario(id_usuario, search, id_categoria)


@router.get("/allinventario/", response_model=list[schema.PiezaInventario])
def listar_allinventario(
    search: str = Query(None, description="Búsqueda por nombre o descripción"),
    id_categoria: int = Query(None, description="Filtrar por ID de categoría")):
        return bodeguero.obtener_todo_inventario(search, id_categoria)



@router.put("/actualizar-stock/{id_usuario}")
def modificar_stock(id_usuario: int, data: schema.StockUpdate):
    return bodeguero.actualizar_stock(id_usuario, data)



