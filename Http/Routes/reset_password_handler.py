from flask import Blueprint, render_template_string, request, jsonify
from Logger.logger import Logger
from BBDD.validator_UI import Validator
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

reset_password_bp = Blueprint('reset_password_bp', __name__, url_prefix="/users")

class ResetPasswordHandler:
    def __init__(self, logger: Logger, db_connection):
        self.logger = logger
        self.db_connection = db_connection
        self.setup_routes()

    def setup_routes(self):
        @reset_password_bp.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
        def reset_password(user_id):
            if request.method == 'GET':
                return render_template_string(self.get_reset_password_form(), user_id=user_id)
            elif request.method == 'POST':
                return self.handle_reset_password(user_id)

        @reset_password_bp.route('/reset_password', methods=['POST'])
        def send_reset_password_email():
            data = request.get_json()
            email = data.get("email")
            if not email:
                return jsonify({"error": "El campo email es obligatorio"}), 400
        
            try:
                if not self.db_connection.connection:
                    self.db_connection.connect()
        
                with self.db_connection.connection.cursor() as cursor:
                    cursor.execute("SELECT id, name FROM users WHERE email = %s", (email,))
                    user = cursor.fetchone()
        
                if not user:
                    return jsonify({"error": "No existe ningún usuario con ese correo electrónico"}), 404
        
                user_id = user["id"]
                name = user["name"]
                reset_link = f"https://jpastorcasquero.pythonanywhere.com/users/reset_password/{user_id}"
        
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
                        <h2>Restablecimiento de Contraseña</h2>
                        <p>Hola <strong>{name}</strong>,</p>
                        <p>Hemos recibido una solicitud para restablecer tu contraseña. Haz clic en el botón para continuar:</p>
                        <a href="{reset_link}" class="button">Restablecer contraseña</a>
                        <p>Si no solicitaste este cambio, puedes ignorar este mensaje.</p>
                        <img src="https://jpastorcasquero.pythonanywhere.com/static/Logo.png" class="logo" alt="Logo" />
                    </div>
                </body>
                </html>
                """
        
                msg = MIMEMultipart("alternative")
                msg["Subject"] = "Restablecer tu contraseña"
                msg["From"] = "pass.recovery.jpcinformatica@gmail.com"
                msg["To"] = email
                msg.attach(MIMEText(html_content, "html"))
        
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login("pass.recovery.jpcinformatica@gmail.com", "yxko jelw mgoo vumt")  # ✅ contraseña de aplicación
                    server.sendmail(msg["From"], msg["To"], msg.as_string())
        
                self.logger.log(f"✅ Enlace de restablecimiento enviado a {email}")
                return jsonify({"message": "Correo de recuperación enviado correctamente"}), 200
        
            except Exception as e:
                self.logger.log(f"❌ Error al enviar correo de recuperación: {repr(e)}")
                return jsonify({"error": "Error al enviar el correo"}), 500


    def get_reset_password_form(self):
        return '''
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Restablecer Contraseña</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        text-align: center;
                        padding: 40px;
                    }
                    .container {
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        max-width: 500px;
                        margin: auto;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }
                    img.logo {
                        width: 120px;
                        margin-bottom: 20px;
                    }
                    input[type=password], input[type=submit] {
                        width: 80%;
                        padding: 10px;
                        margin: 10px;
                    }
                    .error {
                        color: red;
                        margin-top: 10px;
                    }
                </style>
            </head>
            <body>
            <div class="container">
                <img src="/static/Logo.ico" class="logo" alt="Logo">
                <h2>Restablece tu contraseña</h2>
                <form method="POST" id="resetForm">
                    <input type="password" name="password1" id="password1" placeholder="Nueva contraseña" required><br>
                    <input type="password" name="password2" id="password2" placeholder="Confirmar contraseña" required><br>
                    <input type="submit" value="Guardar">
                    <div class="error" id="errorMessage">{{ error }}</div>
                </form>
            </div>

            <script>
            document.getElementById("resetForm").addEventListener("submit", function(e) {
                const password1 = document.getElementById("password1").value.trim();
                const password2 = document.getElementById("password2").value.trim();
                const errorDiv = document.getElementById("errorMessage");

                errorDiv.textContent = "";

                if (password1.length < 8) {
                    errorDiv.textContent = "❌ La contraseña debe tener al menos 8 caracteres.";
                    e.preventDefault();
                    return;
                }

                if (password1 !== password2) {
                    errorDiv.textContent = "❌ Las contraseñas no coinciden.";
                    e.preventDefault();
                }
            });
            </script>
            </body>
            </html>
        '''

    def handle_reset_password(self, user_id):
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if password1 != password2:
            return render_template_string(self.get_reset_password_form(), user_id=user_id, error="❌ Las contraseñas no coinciden")

        error_message = Validator.validate_password(password1)
        if error_message:
            return render_template_string(self.get_reset_password_form(), user_id=user_id, error=error_message)

        try:
            with self.db_connection.connection.cursor() as cursor:
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (password1, user_id))
                self.db_connection.connection.commit()

            self.logger.log(f"🔐 Contraseña restablecida para el usuario {user_id}")
            return "✅ Contraseña restablecida exitosamente"
        except Exception as e:
            self.logger.log(f"❌ Error al actualizar la contraseña: {repr(e)}")
            return jsonify({'error': str(e)}), 500
