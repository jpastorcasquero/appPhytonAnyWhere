from flask import jsonify, request, render_template_string
from BBDD.database_connection import DatabaseConnection
from datetime import datetime
from BBDD.validator_UI import Validator

class UsersHandler:
    def __init__(self, app, logger):
        self.app = app
        self.logger = logger
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/users', methods=['GET', 'POST'])
        def handle_users():
            if request.method == 'GET':
                return self.get_all_users()
            elif request.method == 'POST':
                return self.create_user()

        @self.app.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
        def handle_user_by_id(user_id):
            if request.method == 'GET':
                return self.get_user_by_id(user_id)
            elif request.method == 'PUT':
                return self.update_user(user_id)
            elif request.method == 'DELETE':
                return self.delete_user(user_id)

        @self.app.route('/users/login', methods=['POST'])
        def login():
            return self.login_user()

        @self.app.route('/users/check_email/<string:email>', methods=['GET'])
        def check_email(email):
            return self.check_email_exists(email)

        """@self.app.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
        def reset_password(user_id):
            if request.method == 'GET':
                return render_template_string('''
                    <form action="/reset_password/{{ user_id }}" method="post">
                        Nueva Contraseña: <input type="password" name="password1"><br>
                        Confirmar Contraseña: <input type="password" name="password2"><br>
                        <input type="submit" value="Restablecer">
                    </form>
                ''', user_id=user_id)
            elif request.method == 'POST':
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
                cursor = db_connection.connection.cursor()
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (password1, user_id))
                db_connection.connection.commit()
                cursor.close()
                return "Contraseña restablecida exitosamente", 200"""

    def get_all_users(self):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Ejecutar la consulta para obtener los usuarios
            cursor = db_connection.connection.cursor()
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            cursor.close()

            # Construir una lista de diccionarios con los resultados
            users_list = [{'id': user[0], 'name': user[1], 'email': user[2], 'nick_name': user[3],
                           'role': user[4], 'image': user[5], 'password': user[6]} for user in users]

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nRespuesta: {users_list}\n"
            self.logger.log(log_message)

            return jsonify(users_list), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error en la consulta: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def get_user_by_id(self, user_id):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Ejecutar la consulta para obtener el usuario por ID
            cursor = db_connection.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()

            if user:
                user_dict = {'id': user[0], 'name': user[1], 'email': user[2], 'nick_name': user[3],
                             'role': user[4], 'image': user[5], 'password': user[6]}

                # Registrar la petición y la respuesta en el archivo de logs
                log_message = f"Petición recibida: {request.url}\nRespuesta: {user_dict}\n"
                self.logger.log(log_message)

                return jsonify(user_dict), 200
            else:
                return jsonify({'error': 'Usuario no encontrado'}), 404
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error en la consulta: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def create_user(self):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Obtener los datos de la solicitud
            data = request.get_json()
            name = data.get('name')
            email = data.get('email')
            nick_name = data.get('nick_name')
            role = data.get('role')
            image = data.get('image')
            password = data.get('password')

            # Ejecutar la consulta para insertar el nuevo usuario
            cursor = db_connection.connection.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, nick_name, role, image, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, email, nick_name, role, image, password))
            db_connection.connection.commit()
            cursor.close()

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nDatos insertados: {data}\n"
            self.logger.log(log_message)

            return jsonify({'message': 'Usuario creado exitosamente'}), 201
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error al crear el usuario: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def update_user(self, user_id):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Obtener los datos de la solicitud
            data = request.get_json()
            name = data.get('name')
            email = data.get('email')
            nick_name = data.get('nick_name')
            role = data.get('role')
            image = data.get('image')
            password = data.get('password')

            # Ejecutar la consulta para actualizar el usuario
            cursor = db_connection.connection.cursor()
            cursor.execute("""
                UPDATE users
                SET name = %s, email = %s, nick_name = %s, role = %s, image = %s, password = %s
                WHERE id = %s
            """, (name, email, nick_name, role, image, password, user_id))
            db_connection.connection.commit()
            cursor.close()

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nDatos actualizados: {data}\n"
            self.logger.log(log_message)

            return jsonify({'message': 'Usuario actualizado exitosamente'}), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error al actualizar el usuario: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def delete_user(self, user_id):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Ejecutar la consulta para borrar el usuario
            cursor = db_connection.connection.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            db_connection.connection.commit()
            cursor.close()

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nUsuario borrado con id: {user_id}\n"
            self.logger.log(log_message)

            return jsonify({'message': 'Usuario borrado exitosamente'}), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error al borrar el usuario: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def login_user(self):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Obtener los datos de la solicitud
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')

            # Ejecutar la consulta para verificar el login
            cursor = db_connection.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s",
                           (email, password))
            user = cursor.fetchone()
            cursor.close()

            if user:
                user_dict = {'id': user[0], 'name': user[1], 'email': user[2], 'nick_name': user[3],
                             'role': user[4], 'image': user[5], 'password': user[6]}

                # Registrar la petición y la respuesta en el archivo de logs
                log_message = f"Petición de login recibida: {request.url}\nRespuesta: {user_dict}\n"
                self.logger.log(log_message)

                # return jsonify({'message': 'Login exitoso', 'user': user_dict}), 200
                return jsonify(user_dict), 200
            else:
                return jsonify({'error': 'Email o contraseña incorrectos'}), 401
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error en la consulta: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def check_email_exists(self, email):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Ejecutar la consulta para verificar si el email existe
            cursor = db_connection.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()

            if user:
                log_message = f"Petición de login recibida: {request.url}\nRespuesta: True\n"
                self.logger.log(log_message)
                return jsonify({True}), 200
            else:
                log_message = f"Petición de login recibida: {request.url}\nRespuesta: False\n"
                self.logger.log(log_message)
                return jsonify({False}), 404
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error en la consulta: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500