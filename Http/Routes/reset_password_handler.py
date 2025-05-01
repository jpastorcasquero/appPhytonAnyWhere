from flask import Blueprint, render_template_string, request, jsonify
from BBDD.database_connection import DatabaseConnection
from BBDD.validator_UI import Validator

reset_password_bp = Blueprint('reset_password_bp', __name__)

class ResetPasswordHandler:
    def __init__(self, logger):
        self.logger = logger
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
<html>
<head>
    <title>Restablecer Contraseña</title>
    <style>
        /* Estilos generales para el cuerpo */
        body {
            display: flex;
            flex-direction: column;
            min-height: 100vh; 
            background-color: #263238;
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }

        /* Estilos para el contenedor principal */
        .container {
            width: 400px;
            max-width: 600px; /* Aumentar el ancho del contenedor */
            margin: auto;
            padding: 40px; /* Aumentar el padding */
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            color: whitesmoke;
        }

        /* Estilos para el logotipo */
        .logo {
            text-align: center;
        }
        .logo img {
            width: 150px; /* Aumentar el tamaño del logotipo */
        }

        /* Estilos para los grupos de formularios */
        .form-group {
            margin-bottom: 20px; /* Aumentar el margen inferior */
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: black; /* Cambiar el color del texto a negro */
        }
        .form-group input {
            width: 100%; /* Hacer los campos de entrada más anchos */
            padding: 10px; /* Aumentar el padding */
            box-sizing: border-box;
        }
        .form-group .error {
            color: red;
            font-size: 14px; /* Aumentar el tamaño de la fuente */
            margin-top: 5px; /* Añadir margen superior */
        }

        /* Estilos para el checkbox de mostrar contraseña */
        .form-group .show-password {
            display: flex;
            align-items: center;
            margin-top: 10px;
        }
        .form-group .show-password input {
            width: auto;
            margin-right: 5px;
        }

        /* Estilos para el botón */
        .form-group button {
            width: 100%;
            padding: 15px; /* Aumentar el padding */
            background: linear-gradient(#5c6bc0, #2a9d8f);
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        .form-group button:disabled {
            background-color: #cccccc;
        }
        .form-group button:hover {
            background-color: #344955;
        }
    </style>
    <script>
        /* Función para validar las contraseñas en tiempo real */
        function validatePassword() {
            var password1 = document.getElementById('password1').value;
            var password2 = document.getElementById('password2').value;
            var error = '';
            if (password1 !== password2) {
                error = 'Las contraseñas no coinciden.';
            } else {
                var passwordError = validatePasswordStrength(password1);
                if (passwordError) {
                    error = passwordError;
                }
            }
            document.getElementById('error').innerText = error;
            document.getElementById('submit').disabled = !!error;
        }

        /* Función para validar la fortaleza de la contraseña */
        function validatePasswordStrength(password) {
            if (password.length < 8) {
                return 'La contraseña debe tener al menos 8 caracteres.';
            }
            if (!/[A-Z]/.test(password)) {
                return 'La contraseña debe incluir al menos una letra mayúscula.';
            }
            if (!/[a-z]/.test(password)) {
                return 'La contraseña debe incluir al menos una letra minúscula.';
            }
            if (!/[0-9]/.test(password)) {
                return 'La contraseña debe incluir al menos un número.';
            }
            if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
                return 'La contraseña debe incluir al menos un carácter especial.';
            }
            return '';
        }

        /* Función para mostrar/ocultar la contraseña */
        function togglePasswordVisibility() {
            var passwordFields = document.querySelectorAll('.password-field');
            passwordFields.forEach(function(field) {
                field.type = field.type === 'password' ? 'text' : 'password';
            });
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="logo">
            <!-- Logotipo incrustado -->
            <img src="https://raw.githubusercontent.com/jpastorcasquero/TFG/ce58269da22db81e32b5f4f53c1840d1003b12f9/Logo.ico" alt="Logo">
        </div>
        <!-- Formulario de restablecimiento de contraseña -->
        <form action="/reset_password/{{ user_id }}" method="post" oninput="validatePassword()">
            <div class="form-group">
                <label for="password1">Nueva Contraseña:</label>
                <input type="password" id="password1" name="password1" class="password-field" required>
                <div class="show-password">
                    <input type="checkbox" id="show-password1" onclick="togglePasswordVisibility()">
                    <label for="show-password1">Mostrar Contraseña</label>
                </div>
            </div>
            <div class="form-group">
                <label for="password2">Confirmar Contraseña:</label>
                <input type="password" id="password2" name="password2" class="password-field" required>
            </div>
            <div class="form-group">
                <span id="error" class="error"></span>
            </div>
            <div class="form-group">
                <button type="submit" id="submit" disabled>Restablecer</button>
            </div>
        </form>
    </div>
</body>
</html>
'''

    def handle_reset_password(self, user_id):
        password1 = request.form['password1']
        password2 = request.form['password2']
        if password1 != password2:
            return "Las contraseñas no coinciden", 400
        error_message = Validator.validate_password(password1)
        if error_message:
            return error_message, 400
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()
        if not success:
            return "Fallo al conectar con la base de datos", 500
        try:
            cursor = db_connection.connection.cursor()
            cursor.execute("UPDATE prevision_demanda_db.users SET password = %s WHERE id = %s", (password1, user_id))
            db_connection.connection.commit()
            cursor.close()
            log_message = f"Contraseña restablecida para el usuario {user_id}"
            self.logger.log(log_message)
            return "Contraseña restablecida exitosamente", 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error actualizar password: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500