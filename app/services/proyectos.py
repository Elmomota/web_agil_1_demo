from app.db.db_connection import get_connection
from app.models.proyectos import ProyectoCreate, ProyectoActualizarEstado, AsignarUsuarioProyecto, EliminarUsuarioProyecto, AsignarPiezaProyecto, RemoverPiezaProyecto, PiezaAsignada
from fastapi import HTTPException
from datetime import date

def crear_proyecto(data: ProyectoCreate):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO proyecto (nombre, descripcion, fecha_inicio, fecha_fin, id_estado, id_usuario_responsable)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            data.nombre,
            data.descripcion,
            date.today(),
            data.fecha_fin,
            data.id_estado,
            data.id_usuario_responsable
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Proyecto creado correctamente"}

    except Exception as e:
        print("Error al crear proyecto:", e)
        raise HTTPException(status_code=500, detail="Error al crear proyecto")
    
def listar_proyectos():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT p.id_proyecto, p.nombre, p.descripcion, p.fecha_inicio, p.fecha_fin, ep.nombre AS estado
            FROM proyecto p
            JOIN estado_proyecto ep ON p.id_estado = ep.id_estado
            ORDER BY p.fecha_inicio DESC
        """)

        resultado = cursor.fetchall()
        conn.close()
        return resultado

    except Exception as e:
        print("Error al listar proyectos:", e)
        raise HTTPException(status_code=500, detail="Error al consultar proyectos")

def obtener_piezas_asignadas(id_proyecto: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
              dpp.id_pieza,
              p.nombre AS nombre_pieza,
              dpp.cantidad,
              dpp.fecha_asignacion,
              k.nombre AS nombre_kit
            FROM detalle_pieza_proyecto dpp
            JOIN pieza p ON dpp.id_pieza = p.id_pieza
            LEFT JOIN kit k ON dpp.id_kit = k.id_kit
            WHERE dpp.id_proyecto = %s
            ORDER BY dpp.fecha_asignacion DESC
        """, (id_proyecto,))

        resultado = cursor.fetchall()
        conn.close()
        return resultado

    except Exception as e:
        print("Error al obtener piezas del proyecto:", e)
        raise HTTPException(status_code=500, detail="Error interno al consultar piezas asignadas")

def devolver_pieza_proyecto(id_detalle: int, id_proyecto: int, id_usuario: int, id_almacen: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Obtener datos del detalle
        cursor.execute("""
            SELECT id_pieza, cantidad FROM detalle_pieza_proyecto
            WHERE id_detalle = %s AND id_proyecto = %s
        """, (id_detalle, id_proyecto))
        detalle = cursor.fetchone()

        if not detalle:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")

        id_pieza = detalle['id_pieza']
        cantidad = detalle['cantidad']

        # 2. Eliminar asignación
        cursor.execute("""
            DELETE FROM detalle_pieza_proyecto
            WHERE id_detalle = %s AND id_proyecto = %s
        """, (id_detalle, id_proyecto))

        # 3. Sumar cantidad al inventario
        cursor.execute("""
            UPDATE inventario_almacen SET cantidad = cantidad + %s
            WHERE id_pieza = %s AND id_almacen = %s
        """, (cantidad, id_pieza, id_almacen))

        # 4. Registrar movimiento tipo devolucion (asumimos tipo_movimiento = 4)
        cursor.execute("""
            INSERT INTO movimiento_inventario (id_pieza, id_tipo_movimiento, cantidad, id_usuario, id_proyecto, observaciones, id_almacen)
            VALUES (%s, 4, %s, %s, %s, 'Devolución desde proyecto', %s)
        """, (id_pieza, cantidad, id_usuario, id_proyecto, id_almacen))

        conn.commit()
        conn.close()

        return {"mensaje": "Pieza devuelta al almacén correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        print("Error al devolver pieza:", e)
        raise HTTPException(status_code=500, detail="Error interno al devolver pieza")



def cambiar_estado_proyecto(data: ProyectoActualizarEstado):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        UPDATE proyecto
        SET id_estado = %s
        WHERE id_proyecto = %s
        """

        cursor.execute(query, (data.id_estado, data.id_proyecto))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")

        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Estado del proyecto actualizado correctamente"}

    except Exception as e:
        print("Error al cambiar estado de proyecto:", e)
        raise HTTPException(status_code=500, detail="Error al cambiar estado del proyecto")

def asignar_usuario_a_proyecto(data: AsignarUsuarioProyecto):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO usuario_proyecto (id_usuario, id_proyecto, id_rol_proyecto)
        VALUES (%s, %s, %s)
        """

        cursor.execute(query, (data.id_usuario, data.id_proyecto, data.id_rol_proyecto))
        conn.commit()
        cursor.close()
        conn.close()

        return {"mensaje": "Usuario asignado al proyecto correctamente"}

    except Exception as e:
        print("Error al asignar usuario:", e)
        raise HTTPException(status_code=500, detail="Error al asignar usuario al proyecto")


def eliminar_usuario_de_proyecto(data: EliminarUsuarioProyecto):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        DELETE FROM usuario_proyecto
        WHERE id_usuario = %s AND id_proyecto = %s
        """

        cursor.execute(query, (data.id_usuario, data.id_proyecto))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no estaba asignado al proyecto")

        conn.commit()
        cursor.close()
        conn.close()

        return {"mensaje": "Usuario removido del proyecto"}

    except Exception as e:
        print("Error al remover usuario del proyecto:", e)
        raise HTTPException(status_code=500, detail="Error al remover usuario del proyecto")


def asignar_pieza_a_proyecto(data: AsignarPiezaProyecto):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO detalle_pieza_proyecto (id_detalle, id_proyecto, id_pieza, id_kit, cantidad)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            data.id_detalle,
            data.id_proyecto,
            data.id_pieza,
            data.id_kit,
            data.cantidad
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Pieza asignada al proyecto correctamente"}

    except Exception as e:
        print("Error al asignar pieza al proyecto:", e)
        raise HTTPException(status_code=500, detail="Error al asignar pieza al proyecto")


def remover_pieza_de_proyecto(data: RemoverPiezaProyecto):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        DELETE FROM detalle_pieza_proyecto
        WHERE id_detalle = %s AND id_proyecto = %s
        """

        cursor.execute(query, (data.id_detalle, data.id_proyecto))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pieza no asignada a ese proyecto")

        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Pieza removida del proyecto correctamente"}

    except Exception as e:
        print("Error al remover pieza del proyecto:", e)
        raise HTTPException(status_code=500, detail="Error al remover pieza del proyecto")




def cambiar_rol_usuario_en_proyecto(id_usuario: int, id_proyecto: int, id_nuevo_rol: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE usuario_proyecto
            SET id_rol_proyecto = %s
            WHERE id_usuario = %s AND id_proyecto = %s
        """, (id_nuevo_rol, id_usuario, id_proyecto))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")

        conn.commit()
        conn.close()

        return {"mensaje": "Rol actualizado correctamente"}

    except Exception as e:
        print("Error al cambiar rol del usuario:", e)
        raise HTTPException(status_code=500, detail="Error al actualizar rol del usuario")

def listar_usuarios_en_proyecto(id_proyecto: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT u.id_usuario, CONCAT(u.p_nombre, ' ', u.a_paterno) AS nombre_usuario,
                   u.correo, r.nombre AS rol
            FROM usuario_proyecto up
            JOIN usuario u ON up.id_usuario = u.id_usuario
            JOIN tipo_rol_proyecto r ON up.id_rol_proyecto = r.id_rol_proyecto
            WHERE up.id_proyecto = %s
        """, (id_proyecto,))

        resultado = cursor.fetchall()
        conn.close()
        return resultado

    except Exception as e:
        print("Error al listar usuarios de proyecto:", e)
        raise HTTPException(status_code=500, detail="Error interno al consultar usuarios del proyecto")

