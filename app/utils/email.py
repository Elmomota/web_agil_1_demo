import smtplib
import traceback
from email.message import EmailMessage
from fastapi import HTTPException
from pydantic import EmailStr
from app.core.config import settings


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
