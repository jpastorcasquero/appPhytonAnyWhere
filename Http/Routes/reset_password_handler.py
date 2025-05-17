from flask import Blueprint, render_template_string, request, jsonify
from BBDD.database_connection_handler import DatabaseConnectionHandler
from Logger.logger import Logger
from BBDD.validator_UI import Validator

reset_password_bp = Blueprint('reset_password_bp', __name__)

class ResetPasswordHandler:
    def __init__(self, logger: Logger):
        self.logger = logger
        handler = DatabaseConnectionHandler(logger)
        handler.functions.load_and_connect()
        self.db_connection = handler.functions.db_connection
        self.setup_routes()

    def setup_routes(self):
        @reset_password_bp.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
        def reset_password(user_id):
            if request.method == 'GET':
                return render_template_string(self.get_reset_password_form(), user_id=user_id)
            elif request.method == 'POST':
                return self.handle_reset_password(user_id)

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
                <form method="POST">
                    <input type="password" name="password1" placeholder="Nueva contraseña" required><br>
                    <input type="password" name="password2" placeholder="Confirmar contraseña" required><br>
                    <input type="submit" value="Guardar">
                    {% if error %}
                        <div class="error">{{ error }}</div>
                    {% endif %}
                </form>
            </div>
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
            cursor = self.db_connection.connection.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (password1, user_id))
            self.db_connection.connection.commit()
            cursor.close()

            self.logger.log(f"🔐 Contraseña restablecida para el usuario {user_id}")
            return "✅ Contraseña restablecida exitosamente"
        except Exception as e:
            self.logger.log(f"❌ Error al actualizar la contraseña: {repr(e)}")
            return jsonify({'error': str(e)}), 500
