from app.db.db_connection import get_connection
from fastapi import HTTPException
from app.models.bodega import BodegaCreate, BodegaUpdate

def listar_bodegas():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                a.id_almacen,
                a.nombre,
                a.direccion,
                a.id_comuna,
                c.nombre AS nombre_comuna,
                r.id_region,
                r.nombre AS nombre_region,
                a.estado
            FROM almacen a
            JOIN comuna c ON a.id_comuna = c.id_comuna
            JOIN region r ON c.id_region = r.id_region
        """)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def agregar_bodega(bodega: BodegaCreate):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO almacen (nombre, direccion, id_comuna, estado)
            VALUES (%s, %s, %s, TRUE)
        """, (bodega.nombre, bodega.direccion, bodega.id_comuna))
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Bodega creada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def editar_bodega(id_almacen: int, bodega: BodegaUpdate):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE almacen SET nombre=%s, direccion=%s, id_comuna=%s, estado=%s
            WHERE id_almacen = %s
        """, (bodega.nombre, bodega.direccion, bodega.id_comuna, bodega.estado, id_almacen))
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Bodega actualizada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def eliminar_bodega(id_almacen: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE almacen SET estado = FALSE WHERE id_almacen = %s", (id_almacen,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Bodega eliminada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
