from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.db.db_connection import get_connection

def login_usuario(correo: str, contrasena: str):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_usuario FROM usuario WHERE correo = %s AND estado = 1", (correo,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        cursor.execute("""
            SELECT id_usuario,id_tipo_usuario 
            FROM usuario 
            WHERE correo = %s AND contrasena = SHA2(%s, 256) AND estado = 1
        """, (correo, contrasena,))
        usuario_validado = cursor.fetchone()

        if not usuario_validado:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        return JSONResponse(content=usuario_validado)

    finally:
        cursor.close()
        conn.close()
