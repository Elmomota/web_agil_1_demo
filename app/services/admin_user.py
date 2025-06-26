from fastapi import HTTPException
from app.db.db_connection import get_connection
from app.models.usuario import UsuarioCreate
from app.models.usuario import UsuarioEdit
from app.models.usuario import Usuario
from app.models.usuario import UsuarioOutExtendido
from app.utils.email import enviar_correo

def crear_usuario(usuario: UsuarioCreate):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Validar si ya existe el correo
        cursor.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (usuario.correo,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Correo ya registrado")

        # Insertar usuario (CORRECTAMENTE IDENTADO)
        cursor.execute("""
            INSERT INTO usuario (
                p_nombre, s_nombre, a_paterno, a_materno, correo, contrasena, direccion,
                id_comuna, id_tipo_usuario, id_almacen, estado
            ) VALUES (%s, %s, %s, %s, %s, SHA2(%s, 256), %s, %s, %s, %s, TRUE)
        """, (
            usuario.p_nombre,
            usuario.s_nombre,
            usuario.a_paterno,
            usuario.a_materno,
            usuario.correo,
            usuario.contrasena,
            usuario.direccion,
            usuario.id_comuna,
            usuario.id_tipo_usuario,
            usuario.id_almacen
        ))

        conn.commit()

        # Enviar correo con credenciales
        cuerpo = (
            f"Bienvenido a Maestranzas Unidos.\n\n"
            f"Tu cuenta ha sido creada exitosamente.\n\n"
            f"Correo: {usuario.correo}\n"
            f"Contraseña: {usuario.contrasena}\n\n"
            f"Por favor, cambia tu contraseña después de iniciar sesión."
        )

        enviar_correo(usuario.correo, "Credenciales de acceso", cuerpo)


        return {"message": "Usuario creado. Se intentó enviar el correo."}

    except HTTPException:
        raise
    except Exception as e:
        print("Error general al crear usuario:", e)  # ✅ Muestra el error real en consola
        raise HTTPException(status_code=500, detail="Error al crear usuario")
    finally:
        cursor.close()
        conn.close()

def editar_usuario(usuario: UsuarioEdit):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id_usuario FROM usuario WHERE id_usuario = %s", (usuario.id_usuario,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        cursor.execute("""
            UPDATE usuario
            SET p_nombre = %s,
                s_nombre = %s,
                a_paterno = %s,
                a_materno = %s,
                correo = %s,
                direccion = %s,
                id_comuna = %s,
                id_tipo_usuario = %s,
                id_almacen = %s
            WHERE id_usuario = %s
        """, (
            usuario.p_nombre,
            usuario.s_nombre,
            usuario.a_paterno,
            usuario.a_materno,
            usuario.correo,
            usuario.direccion,
            usuario.id_comuna,
            usuario.id_tipo_usuario,
            usuario.id_almacen,
            usuario.id_usuario
        ))
        conn.commit()

        return {"message": "Usuario actualizado correctamente"}

    except Exception as e:
        print("ERROR SQL:", e)
        raise HTTPException(status_code=500, detail="Error al editar usuario")

    finally:
        cursor.close()
        conn.close()


def eliminar_usuario(id_usuario: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id_usuario FROM usuario WHERE id_usuario = %s AND estado = 1", (id_usuario,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado o ya está inactivo")

        cursor.execute("UPDATE usuario SET estado = 0 WHERE id_usuario = %s", (id_usuario,))
        conn.commit()

        return {"message": "Usuario desactivado correctamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al eliminar usuario")

    finally:
        cursor.close()
        conn.close()



def listar_usuarios_service() -> list[UsuarioOutExtendido]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                u.id_usuario,
                u.p_nombre,
                u.s_nombre,
                u.a_paterno,
                u.a_materno,
                u.correo,
                u.direccion,
                c.nombre AS nombre_comuna,
                tu.nombre AS nombre_tipo_usuario,
                u.id_almacen,
                u.estado
            FROM usuario u
            JOIN comuna c ON u.id_comuna = c.id_comuna
            JOIN tipo_usuario tu ON u.id_tipo_usuario = tu.id_tipo_usuario
            WHERE u.estado = TRUE
            ORDER BY u.id_usuario ASC
        """)
        rows = cursor.fetchall()

        usuarios = [
            UsuarioOutExtendido(
                id_usuario=row[0],
                p_nombre=row[1],
                s_nombre=row[2],
                a_paterno=row[3],
                a_materno=row[4],
                correo=row[5],
                direccion=row[6],
                nombre_comuna=row[7],
                nombre_tipo_usuario=row[8],
                id_almacen=row[9],
                estado=bool(row[10])
            )
            for row in rows
        ]

        return usuarios

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()

def desactivar_usuario(id_usuario: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_usuario FROM usuario WHERE id_usuario = %s", (id_usuario,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        cursor.execute("UPDATE usuario SET estado = FALSE WHERE id_usuario = %s", (id_usuario,))
        conn.commit()
        return {"message": "Usuario desactivado correctamente"}
    finally:
        cursor.close()
        conn.close()