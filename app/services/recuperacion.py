import random
import smtplib
import traceback
from datetime import datetime, timedelta
from email.message import EmailMessage
from fastapi import HTTPException
from app.db.db_connection import get_connection
from pydantic import EmailStr
from app.core.config import settings  # Asegúrate de tener tus settings bien cargados


def enviar_codigo_recuperacion(correo: EmailStr):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id_usuario FROM usuario WHERE correo = %s AND estado = 1", (correo,))
        usuario = cursor.fetchone()
        if not usuario[0]:
            raise HTTPException(status_code=404, detail="Correo no asociado a ninguna cuenta o correo eliminado por Administracion")

        cursor.execute("DELETE FROM codigos_recuperacion WHERE correo = %s", (correo,))

        codigo = f"{random.randint(100000, 999999)}"
        expiracion = datetime.now() + timedelta(minutes=5)

        cursor.execute(
            "INSERT INTO codigos_recuperacion (correo, codigo, expiracion) VALUES (%s, %s, %s)",
            (correo, codigo, expiracion)
        )
        conn.commit()
        cursor.close()
        conn.close()

        msg = EmailMessage()
        msg['Subject'] = 'Código de recuperación'
        msg['From'] = settings.MAIL_USER
        msg['To'] = correo
        msg.set_content(f"Tu código de recuperación es: {codigo}. Tienes 5 minutos para ingresarlo.")

        with smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT) as server:
            server.starttls()
            server.login(settings.MAIL_USER, settings.MAIL_PASS)
            server.send_message(msg)

        return {"message": "Código enviado correctamente"}
    
    except Exception as e:
        print("Error general:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error al enviar el código")

   
        

def verificar_codigo_recuperacion(correo: EmailStr, codigo: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM codigos_recuperacion 
            WHERE correo = %s AND codigo = %s 
            ORDER BY id DESC LIMIT 1
        """, (correo, codigo,))

        registro = cursor.fetchone()
        cursor.close()
        conn.close()
        if datetime.now() > registro[3]: #la cuarta columna del registro es la de la expiracion
            raise HTTPException(status_code=410, detail="El código ha expirado")
        
        if not registro:
            raise HTTPException(status_code=400, detail="Código inválido")
        return {"message": "Código válido"}
    
    except Exception as e:
        print("Error en verificación:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error al verificar el código")

        

def actualizar_contrasena(correo: EmailStr, nueva_contrasena: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id_usuario FROM usuario WHERE correo = %s AND estado = 1", (correo,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Correo no encontrado")

        cursor.execute("""
            UPDATE usuario 
            SET contrasena = SHA2(%s, 256) 
            WHERE correo = %s AND estado = 1
        """, (nueva_contrasena, correo))
        conn.commit()

        return {"message": "Contraseña actualizada correctamente"}
    
    except Exception as e:
        print("Error al actualizar contraseña:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error del servidor")

    finally:
        cursor.close()
        conn.close()
