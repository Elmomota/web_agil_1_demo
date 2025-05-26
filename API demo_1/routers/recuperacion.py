# routers/recuperacion.py
from fastapi import APIRouter, Form, HTTPException
import mysql.connector
from datetime import datetime, timedelta
from email.message import EmailMessage
import smtplib
import random
import os
import traceback
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

router = APIRouter(prefix="/api/user", tags=["Recuperación de Cuenta"])

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'demo_1'
}

@router.post("/send-recovery-code")
def send_recovery_code(correo: str = Form(...)):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()
        if not usuario:
            raise HTTPException(status_code=404, detail="Correo no asociado a ninguna cuenta")

        cursor.execute("DELETE FROM codigos_recuperacion WHERE correo = %s", (correo,))

        codigo = f"{random.randint(100000, 999999)}"
        expiracion = datetime.now() + timedelta(minutes=5)

        cursor.execute(
            "INSERT INTO codigos_recuperacion (correo, codigo, expiracion) VALUES (%s, %s, %s)",
            (correo, codigo, expiracion)
        )
        conn.commit()

        msg = EmailMessage()
        msg['Subject'] = 'Código de recuperación'
        msg['From'] = os.environ.get("MAIL_USER")
        msg['To'] = correo
        msg.set_content(f"Tu código de recuperación es: {codigo}. Tienes 5 minutos para ingresarlo.")

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(os.environ.get("MAIL_USER"), os.environ.get("MAIL_PASS"))
                server.send_message(msg)
        except Exception as e:
            print("Error SMTP:", traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"No se pudo enviar el correo: {str(e)}")

        return {"message": "Código enviado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        print("Error general:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error del servidor")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# ✅ NUEVO ENDPOINT: Verificar código de recuperación
@router.post("/verify-recovery-code")
def verificar_codigo(correo: str = Form(...), codigo: str = Form(...)):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM codigos_recuperacion 
            WHERE correo = %s AND codigo = %s 
            ORDER BY id DESC LIMIT 1
        """, (correo, codigo))

        registro = cursor.fetchone()
        if not registro:
            raise HTTPException(status_code=400, detail="Código inválido")

        if datetime.now() > registro["expiracion"]:
            raise HTTPException(status_code=410, detail="El código ha expirado")

        return {"message": "Código válido"}

    except HTTPException:
        raise
    except Exception as e:
        print("Error en verificación:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error al verificar el código")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
@router.post("/reset-password")
def reset_password(correo: str = Form(...), nueva_contrasena: str = Form(...)):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Verificar si existe el correo
        cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (correo,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Correo no encontrado")

        # Actualizar la contraseña usando SHA2 (puedes cambiar esto si usas otro hash)
        cursor.execute("""
            UPDATE usuarios 
            SET contrasena = SHA2(%s, 256) 
            WHERE correo = %s
        """, (nueva_contrasena, correo))
        conn.commit()

        return {"message": "Contraseña actualizada correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        print("Error al actualizar contraseña:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error del servidor")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
