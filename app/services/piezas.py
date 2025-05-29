from app.db.db_connection import get_connection
from app.models.piezas import PiezaCreate, PiezaUpdate, KitCreate, KitUpdate, KitPiezaUpdate
from fastapi import HTTPException
from app.utils.email import notificar_gestores_pieza
# PIEZA CRUD

def listar_piezas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = '''
        SELECT
        p.id_pieza,
        p.nombre,
        m.id_marca,
        m.nombre AS marca,
        c.id_categoria,
        c.nombre AS categoria,
        p.descripcion,
        p.numero_serie,
        p.imagen_referencial,
        p.stock_minimo,
        p.fecha_vencimiento,
        p.alerta_vencimiento,
        p.estado
        FROM pieza p
        JOIN marca m ON p.id_marca = m.id_marca
        JOIN categoria c ON p.id_categoria = c.id_categoria

    '''
    cursor.execute(query)
    piezas = cursor.fetchall()
    cursor.close()
    conn.close()
    return piezas

def crear_pieza(data: PiezaCreate):
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        INSERT INTO pieza (nombre, id_marca, descripcion, numero_serie,
                           imagen_referencial, stock_minimo, id_categoria,
                           fecha_vencimiento, alerta_vencimiento, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                IF(%s IS NOT NULL AND %s < CURDATE(), TRUE, FALSE), TRUE)
    '''
    cursor.execute(query, (
        data.nombre, data.id_marca, data.descripcion, data.numero_serie,
        data.imagen_referencial, data.stock_minimo, data.id_categoria,
        data.fecha_vencimiento, data.fecha_vencimiento, data.fecha_vencimiento
    ))

    pieza_id = cursor.lastrowid

    # 2. Insertar en inventario_almacen
    cursor.execute('''
        INSERT INTO inventario_almacen (id_almacen, id_pieza, cantidad)
        VALUES (%s, %s, %s)
    ''', (data.id_almacen, pieza_id, data.cantidad or 0))

    conn.commit()

    # 3. Notificar gestores del almacén
    cursor.execute('''
        SELECT correo, p_nombre FROM usuario
        WHERE id_almacen = %s AND id_tipo_usuario = 2 AND estado = TRUE
    ''', (data.id_almacen,))
    gestores = cursor.fetchall()

    for correo, nombre in gestores:
        notificar_gestores_pieza(correo, nombre, data.nombre)

    cursor.close()
    conn.close()

def actualizar_pieza(id_pieza: int, data: PiezaUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    campos = []
    valores = []
    for key, value in data.dict(exclude_unset=True).items():
        campos.append(f"{key} = %s")
        valores.append(value)

    if 'fecha_vencimiento' in data.dict():
        campos.append("alerta_vencimiento = IF(%s IS NOT NULL AND %s < CURDATE(), TRUE, FALSE)")
        valores.extend([data.fecha_vencimiento, data.fecha_vencimiento])

    if not campos:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    query = f"UPDATE pieza SET {', '.join(campos)} WHERE id_pieza = %s"
    valores.append(id_pieza)
    cursor.execute(query, valores)
    conn.commit()
    cursor.close()
    conn.close()

def eliminar_pieza(id_pieza: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE pieza SET estado = FALSE WHERE id_pieza = %s", (id_pieza,))
    conn.commit()
    cursor.close()
    conn.close()

# KIT CRUD

def listar_kits():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM kit")
    kits = cursor.fetchall()
    cursor.close()
    conn.close()
    return kits

def crear_kit(data: KitCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO kit (nombre, descripcion, estado) VALUES (%s, %s, TRUE)",
                   (data.nombre, data.descripcion))
    conn.commit()
    cursor.close()
    conn.close()

def actualizar_kit(id_kit: int, data: KitUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    campos = []
    valores = []
    for key, value in data.dict(exclude_unset=True).items():
        campos.append(f"{key} = %s")
        valores.append(value)

    if not campos:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    query = f"UPDATE kit SET {', '.join(campos)} WHERE id_kit = %s"
    valores.append(id_kit)
    cursor.execute(query, valores)
    conn.commit()
    cursor.close()
    conn.close()

def eliminar_kit(id_kit: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE kit SET estado = FALSE WHERE id_kit = %s", (id_kit,))
    conn.commit()
    cursor.close()
    conn.close()

# KIT-PIEZA CRUD

def listar_kit_piezas(id_kit: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = '''
        SELECT kp.*, p.nombre AS nombre_pieza, COALESCE(p.descripcion, '') AS descripcion_pieza
        FROM kit_pieza kp
        JOIN pieza p ON kp.id_pieza = p.id_pieza
        WHERE kp.id_kit = %s
    '''
    cursor.execute(query, (id_kit,))
    detalles = cursor.fetchall()
    cursor.close()
    conn.close()
    return detalles

def agregar_kit_pieza(id_kit: int, id_pieza: int, cantidad: int):
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor que cero")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO kit_pieza (id_kit, id_pieza, cantidad) VALUES (%s, %s, %s)",
                   (id_kit, id_pieza, cantidad))
    conn.commit()
    cursor.close()
    conn.close()

def actualizar_kit_pieza(id_kit: int, id_pieza: int, data: KitPiezaUpdate):
    if data.cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor que cero")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE kit_pieza SET cantidad = %s WHERE id_kit = %s AND id_pieza = %s",
                   (data.cantidad, id_kit, id_pieza))
    conn.commit()
    cursor.close()
    conn.close()

def eliminar_kit_pieza(id_kit: int, id_pieza: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kit_pieza WHERE id_kit = %s AND id_pieza = %s", (id_kit, id_pieza))
    conn.commit()
    cursor.close()
    conn.close()
