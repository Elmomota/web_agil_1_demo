#C:\Vicente\GitHub\web_agil_1_demo\app\services\piezas.py
from app.db.db_connection import get_connection
from app.models.piezas import PiezaCreate, PiezaUpdate, KitCreate, KitUpdate, KitPiezaUpdateFull
from fastapi import HTTPException
from app.utils.email import notificar_gestores_pieza
import base64


def validar_usuario_admin(id_usuario: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT estado FROM usuario WHERE id_usuario = %s AND id_tipo_usuario = 1",
        (id_usuario,)
    )
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()

    if not resultado:
        raise HTTPException(status_code=403, detail="Acceso denegado: usuario no válido, sin permisos o inexistente")
    if not resultado[0]:
        raise HTTPException(status_code=403, detail="Usuario desactivado")
    

# PIEZA CRUD

def listar_piezas(id_usuario: int):
    validar_usuario_admin(id_usuario)
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
        p.estado,
        ia.id_almacen,
        ia.cantidad
        FROM pieza p
        JOIN marca m ON p.id_marca = m.id_marca
        JOIN categoria c ON p.id_categoria = c.id_categoria
        JOIN inventario_almacen ia ON ia.id_pieza = p.id_pieza
        ORDER BY 13 DESC, 1

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
        pieza["imagenOut"] = imagen_base64
        del pieza["imagen_referencial"]
    cursor.close()
    conn.close()
    return piezas

def crear_pieza(id_usuario: int, data: PiezaCreate):
    validar_usuario_admin(id_usuario)
    conn = get_connection()
    cursor = conn.cursor()
    imagen_bytes = None
    if data.imagen:
        try:
            imagen_bytes = base64.b64decode(data.imagen)
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

def actualizar_pieza(id_usuario: int, id_pieza: int, data: PiezaUpdate):
    validar_usuario_admin(id_usuario)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT estado FROM pieza WHERE id_pieza = %s", (id_pieza,))
    pieza_existente = cursor.fetchone()
    if not pieza_existente or not pieza_existente[0]:
        raise HTTPException(status_code=404, detail="La pieza no existe o está desactivada")
    
        # 2. Obtener almacén actual
    cursor.execute("SELECT id_almacen FROM inventario_almacen WHERE id_pieza = %s", (id_pieza,))
    almacen_actual = cursor.fetchone()
    id_almacen_actual = almacen_actual[0] if almacen_actual else None

    # 3. Extraer valores del dict
    data_dict = data.dict(exclude_unset=True)
    id_almacen_nuevo = data_dict.get("id_almacen")
    # No recuperar ni procesar la cantidad
    nueva_cantidad = None  # <- se usará el stock actual si hay transferencia

    # 4. Eliminar id_almacen y cantidad del dict para no actualizar en tabla pieza
    data_dict.pop("id_almacen", None)




    campos = []
    valores = []
    for key, value in data_dict.items():
        if key != "imagen_referencial":
            campos.append(f"{key} = %s")
            valores.append(value)

        # 5. Imagen: decodificar si viene
    if "imagen_referencial" in data_dict:
        if data_dict["imagen_referencial"] is not None:
            try:
                imagen_blob = base64.b64decode(data_dict["imagen_referencial"])
                campos.append("imagen_referencial = %s")
                valores.append(imagen_blob)
            except Exception:
                raise HTTPException(status_code=400, detail="Imagen inválida")
        else:
            campos.append("imagen_referencial = %s")
            valores.append(None)
            
    # 6. Validar y setear alerta vencimiento
    if "fecha_vencimiento" in data_dict:
        campos.append("alerta_vencimiento = IF(%s IS NOT NULL AND %s < CURDATE(), TRUE, FALSE)")
        valores.extend([data_dict["fecha_vencimiento"], data_dict["fecha_vencimiento"]])

    if not campos:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    query = f"UPDATE pieza SET {', '.join(campos)} WHERE id_pieza = %s"
    valores.append(id_pieza)
    cursor.execute(query, valores)

    # 8. Si se quiere cambiar de almacén
    if id_almacen_nuevo and id_almacen_nuevo != id_almacen_actual:
        cursor.execute("SELECT estado FROM almacen WHERE id_almacen = %s", (id_almacen_nuevo,))
        almacen = cursor.fetchone()

        if not almacen:
            raise HTTPException(status_code=404, detail="El nuevo almacén no existe")
        if not almacen[0]:
            raise HTTPException(status_code=400, detail="El nuevo almacén está inactivo")

        # Verificar si ya existe el vínculo
        cursor.execute("SELECT cantidad FROM inventario_almacen WHERE id_pieza = %s", (id_pieza,))
        row = cursor.fetchone()
        cantidad_actual = row[0] if row else 0

        if not row:
            raise HTTPException(
                status_code=400,
                detail="La pieza no tiene un inventario asociado para realizar la transferencia"
            )

        # Actualizar si existe
        cursor.execute('''
            UPDATE inventario_almacen
            SET id_almacen = %s
            WHERE id_pieza = %s
        ''', (id_almacen_nuevo, id_pieza))


        observacion = f"Transferencia de almacén desde ID {id_almacen_actual} hacia ID {id_almacen_nuevo}"

        # Insertar en movimiento_inventario
        cursor.execute('''
            INSERT INTO movimiento_inventario (
                id_pieza, id_tipo_movimiento, cantidad,
                id_usuario, id_proyecto, observaciones, id_almacen
            )
            VALUES (%s, 3, %s, %s, NULL, %s, %s)
        ''', (
            id_pieza, cantidad_actual, 
            id_usuario, observacion, id_almacen_nuevo
        ))
        
        # Notificar a nuevos gestores del nuevo almacén
        cursor.execute('''
            SELECT correo, p_nombre FROM usuario
            WHERE id_almacen = %s AND id_tipo_usuario = 2 AND estado = TRUE
        ''', (id_almacen_nuevo,))
        gestores = cursor.fetchall()
        for correo, nombre in gestores:
            notificar_gestores_pieza(correo, nombre, data.nombre)

    conn.commit()
    cursor.close()
    conn.close()

def eliminar_pieza(id_usuario: int, id_pieza: int):
    validar_usuario_admin(id_usuario)
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

def listar_kits(id_usuario: int):
    validar_usuario_admin(id_usuario)
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM kit ORDER BY estado DESC, id_kit")
    kits = cursor.fetchall()
    cursor.close()
    conn.close()
    return kits

def crear_kit(id_usuario: int, data: KitCreate):
    validar_usuario_admin(id_usuario)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO kit (nombre, descripcion, estado) VALUES (%s, %s, TRUE)",
                   (data.nombre, data.descripcion))
    conn.commit()
    cursor.close()
    conn.close()

def actualizar_kit(id_usuario: int, id_kit: int, data: KitUpdate):
    validar_usuario_admin(id_usuario)
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

def eliminar_kit(id_usuario: int, id_kit: int):
    validar_usuario_admin(id_usuario)
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

def listar_kit_piezas(id_usuario: int, id_kit: int):
    validar_usuario_admin(id_usuario)
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT kp.*, p.nombre AS nombre_pieza, COALESCE(p.descripcion, '') AS descripcion_pieza
        FROM kit_pieza kp
        JOIN pieza p ON kp.id_pieza = p.id_pieza
        WHERE kp.id_kit = %s
    ''', (id_kit,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def agregar_kit_pieza(id_usuario: int, id_kit: int, id_pieza: int, cantidad: int):
    validar_usuario_admin(id_usuario)    
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

# Verificar si ya existe la combinación (id_kit, id_pieza)
    cursor.execute("SELECT 1 FROM kit_pieza WHERE id_kit = %s AND id_pieza = %s", (id_kit, id_pieza))
    if cursor.fetchone():
        raise HTTPException(
            status_code=400,
            detail="Esta pieza ya está asociada al kit. Si desea cambiar la cantidad, edítela desde la vista correspondiente."
        )
        

    cursor.execute("INSERT INTO kit_pieza (id_kit, id_pieza, cantidad) VALUES (%s, %s, %s)",
                   (id_kit, id_pieza, cantidad))
    conn.commit()
    cursor.close()
    conn.close()

def actualizar_kit_pieza(id_usuario: int, id_kit: int, id_pieza: int, cantidad: int):
    validar_usuario_admin(id_usuario)
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

    # Validar que la pieza realmente esté en el kit
    cursor.execute("SELECT 1 FROM kit_pieza WHERE id_kit = %s AND id_pieza = %s", (id_kit, id_pieza))
    existe = cursor.fetchone()
    if not existe:
        raise HTTPException(status_code=404, detail="La pieza no pertenece al kit")
    
    cursor.execute("UPDATE kit_pieza SET cantidad = %s WHERE id_kit = %s AND id_pieza = %s",
                   (cantidad, id_kit, id_pieza))
    conn.commit()
    cursor.close()
    conn.close()

def eliminar_kit_pieza(id_usuario: int, id_kit: int, id_pieza: int):
    validar_usuario_admin(id_usuario)
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
    
    # Validar que la pieza realmente esté en el kit
    cursor.execute("SELECT 1 FROM kit_pieza WHERE id_kit = %s AND id_pieza = %s", (id_kit, id_pieza))
    existe = cursor.fetchone()
    if not existe:
        raise HTTPException(status_code=404, detail="La pieza no pertenece al kit")
    
    cursor.execute("DELETE FROM kit_pieza WHERE id_kit = %s AND id_pieza = %s", (id_kit, id_pieza))
    conn.commit()
    cursor.close()
    conn.close()
