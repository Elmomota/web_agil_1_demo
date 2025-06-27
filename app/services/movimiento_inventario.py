#app\services\movimiento_inventario.py
from fastapi import HTTPException
from app.db.db_connection import get_connection as get_db

def listar_movimientos_por_sucursal(id_almacen: int, **filters):
    return _listar_movimientos(where_clause="mi.id_almacen = %s", where_params=[id_almacen], **filters)

def listar_movimientos_generales(**filters):
    return _listar_movimientos(where_clause="1=1", where_params=[], **filters)

def _listar_movimientos(where_clause, where_params, **filters):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Filtros dinámicos
        if filters.get("id_movimiento"):
            where_clause += " AND mi.id_movimiento = %s"
            where_params.append(filters["id_movimiento"])

        if filters.get("fecha"):
            where_clause += " AND DATE(mi.fecha) = %s"
            where_params.append(filters["fecha"])

        if filters.get("fecha_inicio") and filters.get("fecha_fin"):
            where_clause += " AND DATE(mi.fecha) BETWEEN %s AND %s"
            where_params.extend([filters["fecha_inicio"], filters["fecha_fin"]])

        if filters.get("id_pieza"):
            where_clause += " AND mi.id_pieza = %s"
            where_params.append(filters["id_pieza"])

        if filters.get("id_usuario"):
            where_clause += " AND mi.id_usuario = %s"
            where_params.append(filters["id_usuario"])

        if filters.get("id_proyecto"):
            where_clause += " AND mi.id_proyecto = %s"
            where_params.append(filters["id_proyecto"])

        if filters.get("id_almacen") and where_clause != "mi.id_almacen = %s":
            where_clause += " AND mi.id_almacen = %s"
            where_params.append(filters["id_almacen"])

        query = f"""
            SELECT 
                mi.id_movimiento,
                p.nombre AS nombre_pieza,
                tm.nombre AS nombre_tipo_movimiento,
                mi.cantidad,
                mi.fecha,
                CONCAT(u.p_nombre, ' ', IFNULL(u.s_nombre, ''), ' ', u.a_paterno, ' ', IFNULL(u.a_materno, '')) AS nombre_usuario,
                pr.nombre AS nombre_proyecto,
                a.nombre AS nombre_almacen,
                mi.observaciones
            FROM movimiento_inventario mi
            JOIN pieza p ON mi.id_pieza = p.id_pieza
            JOIN tipo_movimiento tm ON mi.id_tipo_movimiento = tm.id_tipo_movimiento
            JOIN usuario u ON mi.id_usuario = u.id_usuario
            LEFT JOIN proyecto pr ON mi.id_proyecto = pr.id_proyecto
            JOIN almacen a ON mi.id_almacen = a.id_almacen
            WHERE {where_clause}
            ORDER BY mi.fecha DESC
        """

        cursor.execute(query, tuple(where_params))
        return cursor.fetchall()
    
    except Exception as e:
        db.rollback()
        raise e

    finally:
        cursor.close()
        db.close()
