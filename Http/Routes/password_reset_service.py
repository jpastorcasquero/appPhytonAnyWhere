from flask import request, jsonify
import smtplib
from email.mime.text import MIMEText
from BBDD.database_connection import DatabaseConnection
from Logger.logger import Logger

class PasswordResetService:
    def __init__(self, logger: Logger):
        self.logger = logger

        # Conexión directa sin pasar por handler
        self.db_connection = DatabaseConnection(
            host="jpastorcasquero.mysql.pythonanywhere-services.com",
            database="jpastorcasquero$prevision_demanda_db",
            user="jpastorcasquero",
            password="JPc11082006"
        )

        # Intenta conectar directamente
        connected = self.db_connection.connect()
        if not connected:
            self.logger.log("❌ No se pudo establecer la conexión en PasswordResetService")
            self.db_connection = None

    def send_reset_email(self, email):
        if not self.db_connection or not self.db_connection.connection:
            self.logger.log("❌ No hay conexión activa en PasswordResetService")
            return jsonify({"error": "No hay conexión a la base de datos."}), 500

        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("SELECT id, name, nick_name, email FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()

            if not user:
                self.logger.log(f"❌ No se encontró ningún usuario con el correo: {email}")
                return jsonify({"error": "Usuario no encontrado"}), 404

            user_id = user["id"]
            name = user["name"]
            user_email = user["email"]

            reset_link = f"https://jpastorcasquero.pythonanywhere.com/reset_password/{user_id}"

            html_content = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        text-align: center;
                        background-color: #f7f7f7;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #fff;
                        padding: 30px;
                        margin: auto;
                        max-width: 600px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                        border-radius: 8px;
                    }}
                    .logo {{
                        width: 100px;
                        margin-bottom: 20px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 10px 20px;
                        background-color: #007bff;
                        color: #fff;
                        text-decoration: none;
                        border-radius: 4px;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <img src="https://jpastorcasquero.pythonanywhere.com/static/Logo.ico" class="logo" alt="Logo" />
                    <h2>Restablecimiento de Contraseña</h2>
                    <p>Hola <strong>{name}</strong>,</p>
                    <p>Hemos recibido una solicitud para restablecer tu contraseña. Haz clic en el botón para continuar:</p>
                    <a href="{reset_link}" class="button">Restablecer contraseña</a>
                </div>
            </body>
            </html>
            """

            msg = MIMEText(html_content, 'html')
            msg['Subject'] = 'Restablecer tu contraseña'
            msg['From'] = 'pass.recovery.jpcinformatica@gmail.com'
            msg['To'] = user_email

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login('pass.recovery.jpcinformatica@gmail.com', 'yxko jelw mgoo vumt')
                server.sendmail(msg['From'], msg['To'], msg.as_string())

            self.logger.log(f"✅ Enlace de restablecimiento enviado a {user_email}")
            return jsonify({"message": "Correo enviado correctamente"}), 200

        except Exception as e:
            self.logger.log(f"❌ Error al enviar correo de recuperación: {repr(e)}")
            return jsonify({"error": str(e)}), 500
