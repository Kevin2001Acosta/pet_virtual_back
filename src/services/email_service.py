from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False
)

async def send_reset_password_email(email: str, reset_link: str):
    message = MessageSchema(
        subject="Recuperación de contraseña",
        recipients=[email],
        body=f"""
        <h3>Hola 👋</h3>
        <p>Haz clic en el siguiente enlace para recuperar tu contraseña:</p>
        <a href="{reset_link}">Recuperar contraseña</a>
        """,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)