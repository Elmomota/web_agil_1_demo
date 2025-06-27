from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.db.db_connection import get_connection

def login_usuario(correo: str, contrasena: str):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")

    try:
        cursor = conn.cursor(dictionary=True)

        # Verificar si existe el correo
        cursor.execute("SELECT id_usuario FROM usuario WHERE correo = %s AND estado = 1", (correo,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Intento 1: Validar con SHA2
        cursor.execute("""
            SELECT id_usuario, id_tipo_usuario 
            FROM usuario 
            WHERE correo = %s AND contrasena = SHA2(%s, 256) AND estado = 1
        """, (correo, contrasena))
        usuario_validado = cursor.fetchone()

        # Intento 2: Validar con contraseña en texto plano
        if not usuario_validado:
            cursor.execute("""
                SELECT id_usuario, id_tipo_usuario 
                FROM usuario 
                WHERE correo = %s AND contrasena = %s AND estado = 1
            """, (correo, contrasena))
            usuario_validado = cursor.fetchone()

        if not usuario_validado:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        return JSONResponse(content=usuario_validado)

    finally:
        cursor.close()
        conn.close()


def obtener_id_usuario_por_correo(correo: str):
    db = get_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id_usuario FROM usuario WHERE correo = %s AND estado = 1", (correo,))
        row = cursor.fetchone()
        if row:
            return {"id_usuario": row[0]}
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    finally:
        cursor.close()
        db.close()

def obtener_id_almacen_por_usuario(id_usuario: int):
    db = get_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id_almacen FROM usuario WHERE id_usuario = %s AND estado = 1", (id_usuario,))
        row = cursor.fetchone()
        if row and row[0]:
            return {"id_almacen": row[0]}
        raise HTTPException(status_code=400, detail="Usuario sin almacén asignado")
    finally:
        cursor.close()
        db.close()