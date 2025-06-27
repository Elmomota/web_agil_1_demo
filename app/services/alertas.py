from app.db.db_connection import get_connection

def listar_piezas_vencidas_por_almacen(id_almacen: int):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                p.id_pieza, p.nombre, p.fecha_vencimiento,
                a.nombre AS nombre_almacen
            FROM pieza p
            JOIN inventario_almacen ia ON p.id_pieza = ia.id_pieza
            JOIN almacen a ON ia.id_almacen = a.id_almacen
            WHERE p.alerta_vencimiento = 1 AND p.estado = 0
            AND ia.id_almacen = %s
        """, (id_almacen,))
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()

def listar_piezas_stock_bajo_por_almacen(id_almacen: int):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                p.id_pieza, p.nombre, ia.cantidad, p.stock_minimo,
                a.nombre AS nombre_almacen
            FROM inventario_almacen ia
            JOIN pieza p ON ia.id_pieza = p.id_pieza
            JOIN almacen a ON ia.id_almacen = a.id_almacen
            WHERE ia.cantidad <= p.stock_minimo AND p.estado = 1
            AND ia.id_almacen = %s
        """, (id_almacen,))
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()
