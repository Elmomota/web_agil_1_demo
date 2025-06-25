#app\services\auxiliares.py

from app.db.db_connection import get_connection
from fastapi import HTTPException


def fetch_all(sql: str, params: tuple = None):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def obtener_tipos_usuario():
    return fetch_all("SELECT id_tipo_usuario, nombre FROM tipo_usuario")

def obtener_regiones():
    return fetch_all("SELECT id_region, nombre FROM region")

def obtener_comunas_por_region(id_region: int):
    return fetch_all("SELECT id_comuna, nombre FROM comuna WHERE id_region = %s", (id_region,))

def obtener_tipos_movimiento():
    return fetch_all("SELECT id_tipo_movimiento, nombre FROM tipo_movimiento")

def obtener_categorias():
    return fetch_all("SELECT id_categoria, nombre FROM categoria WHERE estado = TRUE")

def obtener_marcas():
    return fetch_all("SELECT id_marca, nombre FROM marca WHERE estado = TRUE")

def obtener_estados_proyecto():
    return fetch_all("SELECT id_estado, nombre FROM estado_proyecto")

def obtener_roles_proyecto():
    return fetch_all("SELECT id_rol_proyecto, nombre FROM tipo_rol_proyecto")

def obtener_almacenes():
    return fetch_all("""
        SELECT 
            a.id_almacen, 
            a.nombre, 
            a.direccion,
            c.nombre AS nombre_comuna, 
            r.nombre AS nombre_region
        FROM almacen a
        JOIN comuna c ON a.id_comuna = c.id_comuna
        JOIN region r ON c.id_region = r.id_region
        WHERE a.estado = TRUE
    """)

def obtener_piezas_disponibles():
    return fetch_all("SELECT id_pieza, nombre FROM pieza WHERE estado = TRUE")