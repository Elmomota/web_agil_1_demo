from email.message import EmailMessage
import smtplib
from app.core.config import settings
import traceback
from fastapi import HTTPException
from pydantic import EmailStr

def notificar_gestores_pieza(correo: str, nombre: str, nombre_pieza: str):
    msg = EmailMessage()
    msg["Subject"] = "Nueva pieza asignada a tu almacén"
    msg["From"] = settings.MAIL_USER
    msg["To"] = correo
    msg.set_content(f"""
    Estimado/a {nombre},

    Se ha registrado una nueva pieza "{nombre_pieza}" en el almacén que gestionas.
    Por favor verifica su stock y realiza el seguimiento correspondiente.

    Saludos,
    Sistema de Inventarios - Maestranzas Unidos S.A.
    """)


    with smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT) as server:
        server.starttls()
        server.login(settings.MAIL_USER, settings.MAIL_PASS)
        server.send_message(msg)



#correo de momota

def enviar_correo(destinatario: EmailStr, asunto: str, cuerpo: str):
    try:
        msg = EmailMessage()
        msg['Subject'] = asunto
        msg['From'] = settings.MAIL_USER
        msg['To'] = destinatario
        msg.set_content(cuerpo)

        with smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT) as server:
            server.starttls()
            server.login(settings.MAIL_USER, settings.MAIL_PASS)
            server.send_message(msg)

    except Exception:
        print("Error general al enviar correo:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error al enviar el correo")



def notificar_admin_pieza_vencida(correo_admin, nombre_admin, nombre_pieza, fecha_vencimiento):
    asunto = f"Pieza vencida: {nombre_pieza}"
    cuerpo = (
        f"Estimado(a) {nombre_admin},\n\n"
        f"La pieza '{nombre_pieza}' ha vencido el {fecha_vencimiento} y fue desactivada automáticamente.\n"
        f"Por favor, verifique si la acción en el sistema quedó efectuada.\n\n"
        "Sistema de Inventario - Maestranzas Unidos S.A."
    )
    enviar_correo(correo_admin, asunto, cuerpo)


def notificar_gestores_remocion(correo, nombre, nombre_pieza):
    asunto = f"Remoción física de pieza vencida: {nombre_pieza}"
    cuerpo = (
        f"Estimado(a) {nombre}, \n\n"
        f"la pieza '{nombre_pieza}' venció y ha sido desactivada. Debe ser retirada del almacén físicamente.\n\n"
        "Sistema de Inventario - Maestranzas Unidos S.A."
    )
    enviar_correo(correo, asunto, cuerpo)


def enviar_correo_alerta_stock_bajo(destinatario, pieza):
    asunto = f"⚠️ Stock bajo: {pieza['nombre']} (ID {pieza['id_pieza']})"
    cuerpo = (
        f"La pieza \"{pieza['nombre']}\" (ID {pieza['id_pieza']}) ha alcanzado un nivel crítico de stock.\n\n"
        f"Cantidad actual: {pieza['cantidad']} (mínimo permitido: {pieza['stock_minimo']})\n"
        f"Por favor, revisar reposición en el almacén ID {pieza['id_almacen']}, que usted está asignado.\n\n"
        "Sistema de Inventario - Maestranzas Unidos S.A."
    )
    enviar_correo(destinatario, asunto, cuerpo)
