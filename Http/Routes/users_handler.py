from flask import jsonify, request
from BBDD.database_connection_handler import DatabaseConnectionHandler
from BBDD.validator_UI import Validator

class UsersHandler:
    def __init__(self, app, logger):
        self.app = app
        self.logger = logger
        self.db_handler = DatabaseConnectionHandler(logger)
        self.db_handler.functions.load_and_connect()
        self.db_connection = self.db_handler.functions.db_connection
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

    def get_all_users(self):
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            cursor.close()

            self.logger.log(f"GET /users\nRespuesta: {users}")
            return jsonify(users), 200
        except Exception as e:
            self.logger.log(f"❌ Error en get_all_users: {repr(e)}")
            return jsonify({'error': str(e)}), 500

    def get_user_by_id(self, user_id):
        if not self.db_connection or not self.db_connection.connection:
            return jsonify({'error': 'Conexión a base de datos no disponible'}), 500
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()

            if user:
                self.logger.log(f"GET /users/{user_id}\nRespuesta: {user}")
                return jsonify(user), 200
            else:
                return jsonify({'error': 'Usuario no encontrado'}), 404
        except Exception as e:
            self.logger.log(f"❌ Error en get_user_by_id: {repr(e)}")
            return jsonify({'error': str(e)}), 500

    def create_user(self):
        if not self.db_connection or not self.db_connection.connection:
            return jsonify({'error': 'Conexión a base de datos no disponible'}), 500
        try:
            data = request.get_json()
            self.logger.log(f"Datos recibidos en create_user: {data}")  # <--- LOG IMPORTANTE

            # Validación mínima
            required_fields = ['name', 'email', 'nick_name', 'role', 'image', 'password']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'error': f'Campo faltante o vacío: {field}'}), 400

            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, nick_name, role, image, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data['name'], data['email'], data['nick_name'], data['role'], data['image'], data['password']))
            self.db_connection.connection.commit()
            cursor.close()

            self.logger.log(f"POST /users\nInsertado: {data}")
            return jsonify({'message': 'Usuario creado exitosamente'}), 201
        except Exception as e:
            self.logger.log(f"Error en create_user: {repr(e)}")  # usa repr para ver el tipo de error
            return jsonify({'error': str(e)}), 500

    def update_user(self, user_id):
        if not self.db_connection or not self.db_connection.connection:
            return jsonify({'error': 'Conexión a base de datos no disponible'}), 500
        try:
            data = request.get_json()
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                UPDATE users
                SET name = %s, email = %s, nick_name = %s, role = %s, image = %s, password = %s
                WHERE id = %s
            """, (
                data['name'], data['email'], data['nick_name'],
                data['role'], data['image'], data['password'], user_id
            ))
            self.db_connection.connection.commit()
            cursor.close()

            self.logger.log(f"PUT /users/{user_id}\nActualizado: {data}")
            return jsonify({'message': 'Usuario actualizado exitosamente'}), 200
        except Exception as e:
            self.logger.log(f"❌ Error en update_user: {repr(e)}")
            return jsonify({'error': str(e)}), 500

    def delete_user(self, user_id):
        if not self.db_connection or not self.db_connection.connection:
            return jsonify({'error': 'Conexión a base de datos no disponible'}), 500
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            self.db_connection.connection.commit()
            cursor.close()

            self.logger.log(f"DELETE /users/{user_id}\nEliminado.")
            return jsonify({'message': 'Usuario borrado exitosamente'}), 200
        except Exception as e:
            self.logger.log(f"❌ Error en delete_user: {repr(e)}")
            return jsonify({'error': str(e)}), 500

    def login_user(self):
        if not self.db_connection or not self.db_connection.connection:
            return jsonify({'error': 'Conexión a base de datos no disponible'}), 500
        try:
            data = request.get_json()
            cursor = self.db_connection.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s",
                           (data['email'], data['password']))
            user = cursor.fetchone()
            cursor.close()

            if user:
                self.logger.log(f"POST /users/login\nLogin exitoso: {user}")
                return jsonify(user), 200
            else:
                return jsonify({'error': 'Email o contraseña incorrectos'}), 401
        except Exception as e:
            self.logger.log(f"❌ Error en login_user: {repr(e)}")
            return jsonify({'error': str(e)}), 500

    def check_email_exists(self, email):
        if not self.db_connection or not self.db_connection.connection:
            return jsonify({'error': 'Conexión a base de datos no disponible'}), 500
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()

            existe = user is not None
            self.logger.log(f"GET /users/check_email/{email}\nExiste: {existe}")
            return jsonify({'exists': existe}), (200 if existe else 404)
        except Exception as e:
            self.logger.log(f"❌ Error en check_email_exists: {repr(e)}")
            return jsonify({'error': str(e)}), 500
