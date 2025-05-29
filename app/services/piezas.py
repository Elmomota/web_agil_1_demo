#C:\Vicente\GitHub\web_agil_1_demo\app\services\piezas.py
from app.db.db_connection import get_connection
from app.models.piezas import PiezaCreate, PiezaUpdate, KitCreate, KitUpdate, KitPiezaUpdateFull
from fastapi import HTTPException
from app.utils.email import notificar_gestores_pieza
import base64

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
    for pieza in piezas:
        imagen_blob = pieza["imagen_referencial"]
        imagen_base64 = None
        try:
            if imagen_blob:
                imagen_base64 = base64.b64encode(imagen_blob).decode("utf-8")
        except Exception as e:
            print("Error al convertir imagen a base64:", e)
        pieza["imagen_referencial"] = imagen_base64
    cursor.close()
    conn.close()
    return piezas

def crear_pieza(data: PiezaCreate):
    conn = get_connection()
    cursor = conn.cursor()
    imagen_bytes = None
    if data.imagen_referencial:
        try:
            imagen_bytes = base64.b64decode(data.imagen_referencial)
        except Exception as e:
            print("Error al decodificar imagen base64:", e)

    query = '''
        INSERT INTO pieza (nombre, id_marca, descripcion, numero_serie,
                           imagen_referencial, stock_minimo, id_categoria,
                           fecha_vencimiento, alerta_vencimiento, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                IF(%s IS NOT NULL AND %s < CURDATE(), TRUE, FALSE), TRUE)
    '''
    cursor.execute(query, (
        data.nombre, data.id_marca, data.descripcion, data.numero_serie,
        imagen_bytes, data.stock_minimo, data.id_categoria,
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
    cursor.execute("SELECT estado FROM pieza WHERE id_pieza = %s", (id_pieza,))
    pieza_existente = cursor.fetchone()
    if not pieza_existente or not pieza_existente[0]:
        raise HTTPException(status_code=404, detail="La pieza no existe o está desactivada")
    
        # 2. Obtener almacén actual
    cursor.execute("SELECT id_almacen FROM inventario_almacen WHERE id_pieza = %s", (id_pieza,))
    almacen_actual = cursor.fetchone()
    id_almacen_actual = almacen_actual["id_almacen"] if almacen_actual else None

    campos = []
    valores = []
    for key, value in data.dict(exclude_unset=True).items():
        campos.append(f"{key} = %s")
        valores.append(value)

        # 3. Imagen: decodificar si viene
    data_dict = data.dict(exclude_unset=True)
    if "imagen_referencial" in data_dict:
        try:
            imagen_blob = base64.b64decode(data_dict["imagen_referencial"])
            campos.append("imagen_referencial = %s")
            valores.append(imagen_blob)
        except Exception:
            raise HTTPException(status_code=400, detail="Imagen inválida")
            
    # 4. Validar y setear alerta vencimiento
    if "fecha_vencimiento" in data_dict:
        campos.append("alerta_vencimiento = IF(%s IS NOT NULL AND %s < CURDATE(), TRUE, FALSE)")
        valores.extend([data_dict["fecha_vencimiento"], data_dict["fecha_vencimiento"]])

    

    if not campos:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    query = f"UPDATE pieza SET {', '.join(campos)} WHERE id_pieza = %s"
    valores.append(id_pieza)
    cursor.execute(query, valores)

    # 7. Si se quiere cambiar de almacén:
    id_almacen_nuevo = data_dict.get("id_almacen")
    nueva_cantidad = data_dict.get("cantidad", 0)
    # Validar que el nuevo id_almacen existe y esté activo
    if id_almacen_nuevo and id_almacen_nuevo != id_almacen_actual:
        cursor.execute("SELECT estado FROM almacen WHERE id_almacen = %s", (id_almacen_nuevo,))
        almacen = cursor.fetchone()
        if not almacen:
            raise HTTPException(status_code=404, detail="El nuevo almacén no existe")
        if not almacen[0]:
            raise HTTPException(status_code=400, detail="El nuevo almacén está inactivo")

        # Eliminar vínculo anterior
        cursor.execute("DELETE FROM inventario_almacen WHERE id_pieza = %s", (id_pieza,))
        # Insertar nuevo vínculo
        cursor.execute('''
            INSERT INTO inventario_almacen (id_almacen, id_pieza, cantidad)
            VALUES (%s, %s, %s)
        ''', (id_almacen_nuevo, id_pieza, nueva_cantidad))

        # Notificar a nuevos gestores
        cursor.execute('''
            SELECT correo, p_nombre FROM usuario
            WHERE id_almacen = %s AND id_tipo_usuario = 2 AND estado = TRUE
        ''', (id_almacen_nuevo,))
        gestores = cursor.fetchall()
        nombre_pieza = data_dict.get("nombre", "una pieza actualizada")

        for gestor in gestores:
            notificar_gestores_pieza(gestor["correo"], gestor["p_nombre"], nombre_pieza)
    conn.commit()
    cursor.close()
    conn.close()

def eliminar_pieza(id_pieza: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT estado FROM pieza WHERE id_pieza = %s", (id_pieza,))
    pieza = cursor.fetchone()
    if not pieza:
        raise HTTPException(status_code=404, detail="La pieza no existe")
    if not pieza[0]:
        raise HTTPException(status_code=400, detail="La pieza ya está desactivada")
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
    cursor.execute("SELECT estado FROM kit WHERE id_kit = %s", (id_kit,))
    kit = cursor.fetchone()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit no encontrado")
    if not kit[0]:
        raise HTTPException(status_code=400, detail="Kit desactivado. No se puede modificar.")
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
    cursor.execute("SELECT estado FROM kit WHERE id_kit = %s", (id_kit,))
    kit = cursor.fetchone()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit no encontrado")
    if not kit[0]:
        raise HTTPException(status_code=400, detail="Kit desactivado. No se puede modificar.")
    
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

        # Validar estado de kit
    cursor.execute("SELECT estado FROM kit WHERE id_kit = %s", (id_kit,))
    kit = cursor.fetchone()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit no encontrado")
    if not kit[0]:
        raise HTTPException(status_code=400, detail="Kit inactivo")
        

    cursor.execute("INSERT INTO kit_pieza (id_kit, id_pieza, cantidad) VALUES (%s, %s, %s)",
                   (id_kit, id_pieza, cantidad))
    conn.commit()
    cursor.close()
    conn.close()

def actualizar_kit_pieza(id_kit: int, id_pieza: int, cantidad: int):
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor que cero")
    conn = get_connection()
    cursor = conn.cursor()
            # Validar estado de kit
    cursor.execute("SELECT estado FROM kit WHERE id_kit = %s", (id_kit,))
    kit = cursor.fetchone()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit no encontrado")
    if not kit[0]:
        raise HTTPException(status_code=400, detail="Kit inactivo")

    # Validar estado de pieza
    cursor.execute("SELECT estado FROM pieza WHERE id_pieza = %s", (id_pieza,))
    pieza = cursor.fetchone()
    if not pieza:
        raise HTTPException(status_code=404, detail="Pieza no encontrada")
    if not pieza[0]:
        raise HTTPException(status_code=400, detail="Pieza inactiva")
    
    cursor.execute("UPDATE kit_pieza SET cantidad = %s WHERE id_kit = %s AND id_pieza = %s",
                   (cantidad, id_kit, id_pieza))
    conn.commit()
    cursor.close()
    conn.close()

def eliminar_kit_pieza(id_kit: int, id_pieza: int):
    conn = get_connection()
    cursor = conn.cursor()
        # Validar estado de kit
    cursor.execute("SELECT estado FROM kit WHERE id_kit = %s", (id_kit,))
    kit = cursor.fetchone()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit no encontrado")
    if not kit[0]:
        raise HTTPException(status_code=400, detail="Kit inactivo")



    # Validar estado de pieza
    cursor.execute("SELECT estado FROM pieza WHERE id_pieza = %s", (id_pieza,))
    pieza = cursor.fetchone()
    if not pieza:
        raise HTTPException(status_code=404, detail="Pieza no encontrada")
    if not pieza[0]:
        raise HTTPException(status_code=400, detail="Pieza inactiva")
    cursor.execute("DELETE FROM kit_pieza WHERE id_kit = %s AND id_pieza = %s", (id_kit, id_pieza))
    conn.commit()
    cursor.close()
    conn.close()
