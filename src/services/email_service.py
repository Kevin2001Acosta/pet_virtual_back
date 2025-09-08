from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False
)

async def send_reset_password_email(email: str, reset_link: str):
  

    message = MessageSchema(
        subject="🔐 Recuperación de contraseña",
        recipients=[email],
        body=f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Recuperación de contraseña</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #fef2f2;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td align="center" style="padding: 40px 0;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #fecaca;">
                            
                            <tr>
                                <td style="padding: 30px; text-align: center; background-color: #FF0000; border-radius: 8px 8px 0 0;">
                                    
                                    <h1 style="color: white; margin: 0 0 10px 0; font-size: 24px; font-weight: 600;">Recuperación de contraseña</h1>
                                    <p style="color: rgba(255,255,255,0.9); margin: 0; line-height: 1.6; font-size: 16px;">
                                        ¡Te ayudaremos a recuperar tu acceso!
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- CONTENIDO PRINCIPAL -->
                            <tr>
                                <td style="padding: 30px;">
                                    <p style="color: #374151; margin: 0 0 20px 0; line-height: 1.6; font-size: 16px;">Hola 👋,</p>
                                    <p style="color: #374151; margin: 0 0 20px 0; line-height: 1.6; font-size: 16px;">Hemos recibido una solicitud para restablecer tu contraseña. Haz clic en el siguiente botón para continuar:</p>
                                    
                                    <div style="text-align: center; margin: 30px 0;">
                                        <a href="{reset_link}" style="background-color: #FF0000; color: white; padding: 14px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: 600; font-size: 16px; box-shadow: 0 2px 4px rgba(255, 0, 0, 0.3);">Restablecer contraseña</a>
                                    </div>
                                    
                                    <p style="color: #6b7280; margin: 0 0 15px 0; line-height: 1.6; font-size: 14px; text-align: center;">Si el botón no funciona, copia y pega el siguiente enlace en tu navegador:</p>
                                    <p style="color: #DC2626; margin: 0 0 25px 0; line-height: 1.5; word-break: break-all; background-color: #fef2f2; padding: 12px; border-radius: 6px; font-size: 14px; border-left: 4px solid #FF0000;">{reset_link}</p>
                                    
                                    <div style="background-color: #fef2f2; padding: 16px; border-radius: 6px; border-left: 4px solid #FF0000;">
                                        <p style="color: #374151; margin: 0; line-height: 1.6; font-size: 14px;"><strong>💡 Importante:</strong> Este enlace expirará en 1 hora por seguridad. Si no solicitaste este cambio, ignora este mensaje.</p>
                                    </div>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="padding: 20px 30px; background-color: #fef2f2; border-radius: 0 0 8px 8px; border-top: 1px solid #fecaca;">
                                    <p style="color: #EF4444; margin: 0; font-size: 12px; line-height: 1.4; text-align: center;">© {datetime.now().year} Macota virtual. Universidad del valle.</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)