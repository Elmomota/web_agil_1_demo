from fastapi import HTTPException
from app.db.db_connection import get_connection
from app.models.bodeguero import StockUpdate

def obtener_inventario_usuario(id_usuario: int, search: str = None, id_categoria: int = None):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    try:

        cursor.execute("SELECT id_tipo_usuario, id_almacen FROM usuario WHERE id_usuario = %s AND estado = 1", (id_usuario,))
        usuario = cursor.fetchone()

        if not usuario or usuario["id_tipo_usuario"] != 2:
            raise HTTPException(status_code=403, detail="Acceso denegado")

        id_almacen = usuario["id_almacen"]
        if not id_almacen:
            raise HTTPException(status_code=400, detail="Usuario sin almacén asignado")

        query = """
            SELECT 
                p.id_pieza, p.nombre, p.descripcion, p.numero_serie,
                p.stock_minimo, p.fecha_vencimiento, p.alerta_vencimiento,
                p.estado, p.id_categoria, p.id_marca,
                m.nombre AS nombre_marca, m.descripcion AS desc_marca,
                c.nombre AS nombre_categoria, c.descripcion AS desc_categoria,
                ia.cantidad
            FROM inventario_almacen ia
            JOIN pieza p ON ia.id_pieza = p.id_pieza
            JOIN marca m ON p.id_marca = m.id_marca
            JOIN categoria c ON p.id_categoria = c.id_categoria
            WHERE ia.id_almacen = %s and p.estado = 1
        """

        params = [id_almacen]

        if search:
            query += " AND (p.nombre LIKE %s OR p.descripcion LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term])

        if id_categoria:
            query += " AND p.id_categoria = %s"
            params.append(id_categoria)

        cursor.execute(query, tuple(params))
        
        return cursor.fetchall()

    except Exception as e:
        db.rollback()
        raise e

    finally:
        cursor.close()
        db.close()



def obtener_todo_inventario( search: str = None, id_categoria: int = None):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    try:


        query = """
            SELECT 
                p.id_pieza, p.nombre, p.descripcion, p.numero_serie,
                p.stock_minimo, p.fecha_vencimiento, p.alerta_vencimiento,
                p.estado, p.id_categoria, p.id_marca,
                m.nombre AS nombre_marca, m.descripcion AS desc_marca,
                c.nombre AS nombre_categoria, c.descripcion AS desc_categoria,
                ia.cantidad
            FROM inventario_almacen ia
            JOIN pieza p ON ia.id_pieza = p.id_pieza
            JOIN marca m ON p.id_marca = m.id_marca
            JOIN categoria c ON p.id_categoria = c.id_categoria
        """

        params = []

        if search:
            query += " AND (p.nombre LIKE %s OR p.descripcion LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term])

        if id_categoria:
            query += " AND p.id_categoria = %s"
            params.append(id_categoria)

        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    
    except Exception as e:
        db.rollback()
        raise e

    finally:
        cursor.close()
        db.close()


def actualizar_stock(id_usuario: int, data: StockUpdate):
    db = get_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id_tipo_usuario, id_almacen FROM usuario WHERE id_usuario = %s AND estado = 1", (id_usuario,))
        user = cursor.fetchone()

        if not user or user[0] != 2:
            raise HTTPException(status_code=403, detail="Acceso denegado. Solo para Gestores de Inventario")

        id_almacen = user[1]
        if not id_almacen:
            raise HTTPException(status_code=400, detail="Usuario sin almacén asignado")

        # Validar tipo de movimiento permitido
        if data.id_tipo_movimiento not in [1, 2, 6]:
            raise HTTPException(status_code=400, detail="Tipo de movimiento no permitido para este usuario")

        # Verificar stock actual
        cursor.execute("SELECT cantidad FROM inventario_almacen WHERE id_almacen = %s AND id_pieza = %s", (id_almacen, data.id_pieza))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Pieza no encontrada en el almacén")

        stock_actual = result[0]
        nueva_cantidad = data.cantidad

        if data.id_tipo_movimiento == 1 and nueva_cantidad <= stock_actual:
            raise HTTPException(status_code=400, detail="Cantidad debe ser mayor al stock actual para movimiento tipo ENTRADA")
        if data.id_tipo_movimiento == 2 and nueva_cantidad >= stock_actual:
            raise HTTPException(status_code=400, detail="Cantidad debe ser menor al stock actual para movimiento tipo SALIDA")
        if data.id_tipo_movimiento == 6 and nueva_cantidad == stock_actual:
            raise HTTPException(status_code=400, detail="Cantidad debe ser distinta al stock actual para movimiento tipo CORRECCION")

        # Actualizar inventario
        cursor.execute("""
            UPDATE inventario_almacen SET cantidad = %s
            WHERE id_almacen = %s AND id_pieza = %s
        """, (nueva_cantidad, id_almacen, data.id_pieza))

        # Registrar movimiento
        cursor.execute("""
            INSERT INTO movimiento_inventario (id_pieza, id_tipo_movimiento, cantidad, id_usuario, id_almacen, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data.id_pieza, data.id_tipo_movimiento, nueva_cantidad, id_usuario, id_almacen, data.observaciones))

        db.commit()
        return {"mensaje": "Stock actualizado correctamente"}

    except Exception as e:
        db.rollback()
        raise e

    finally:
        cursor.close()
        db.close()