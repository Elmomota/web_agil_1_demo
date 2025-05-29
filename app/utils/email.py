from email.message import EmailMessage
import smtplib
from app.core.config import settings

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
