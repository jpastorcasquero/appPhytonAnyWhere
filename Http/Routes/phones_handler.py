from flask import jsonify, request
from BBDD.database_connection import DatabaseConnection
from datetime import datetime

class PhonesHandler:
    def __init__(self, app, logger):
        self.app = app
        self.logger = logger
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/phones', methods=['GET', 'POST'])
        def handle_phones():
            if request.method == 'GET':
                return self.get_all_phones()
            elif request.method == 'POST':
                return self.create_phone()

        @self.app.route('/phones/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
        def handle_phone_by_user(user_id):
            if request.method == 'GET':
                return self.get_phones_by_user(user_id)
            elif request.method == 'PUT':
                return self.update_phone(user_id)
            elif request.method == 'DELETE':
                return self.delete_phone(user_id)

    def get_all_phones(self):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Ejecutar la consulta para obtener los teléfonos
            cursor = db_connection.connection.cursor()
            cursor.execute("SELECT * FROM prevision_demanda_db.phones")
            phones = cursor.fetchall()
            cursor.close()

            # Construir una lista de diccionarios con los resultados
            phone_list = [{'id': phone[0], 'user_id': phone[1], 'country_code': phone[2], 'phone': phone[3]} for phone in phones]

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nRespuesta: {phone_list}\n"
            self.logger.log(log_message)

            return jsonify(phone_list), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error en la consulta: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def get_phones_by_user(self, user_id):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Ejecutar la consulta para obtener los teléfonos por user_id
            cursor = db_connection.connection.cursor()
            cursor.execute("SELECT * FROM prevision_demanda_db.phones WHERE user_id = %s", (user_id,))
            phones = cursor.fetchall()
            cursor.close()

            # Construir una lista de diccionarios con los resultados
            phone_list = [{'id': phone[0], 'user_id': phone[1], 'country_code': phone[2], 'phone': phone[3]} for phone in phones]

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nRespuesta: {phone_list}\n"
            self.logger.log(log_message)

            return jsonify(phone_list), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error en la consulta: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def create_phone(self):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Obtener los datos de la solicitud
            data = request.get_json()
            user_id = data.get('user_id')
            country_code = data.get('country_code')
            phone = data.get('phone')

            # Ejecutar la consulta para insertar el nuevo teléfono
            cursor = db_connection.connection.cursor()
            cursor.execute("""
                INSERT INTO prevision_demanda_db.phones (user_id, country_code, phone)
                VALUES (%s, %s, %s)
            """, (user_id, country_code, phone))
            db_connection.connection.commit()
            cursor.close()

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nDatos insertados: {data}\n"
            self.logger.log(log_message)

            return jsonify({'message': 'Teléfono creado exitosamente'}), 201
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error al crear el teléfono: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def update_phone(self, user_id):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Obtener los datos de la solicitud
            data = request.get_json()
            country_code = data.get('country_code')
            phone = data.get('phone')

            # Ejecutar la consulta para actualizar el teléfono
            cursor = db_connection.connection.cursor()
            cursor.execute("""
                UPDATE prevision_demanda_db.phones
                SET country_code = %s, phone = %s
                WHERE user_id = %s
            """, (country_code, phone, user_id))
            db_connection.connection.commit()
            cursor.close()

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nDatos actualizados: {data}\n"
            self.logger.log(log_message)

            return jsonify({'message': 'Teléfono actualizado exitosamente'}), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error al actualizar el teléfono: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def delete_phone(self, user_id):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Ejecutar la consulta para borrar el teléfono
            cursor = db_connection.connection.cursor()
            cursor.execute("DELETE FROM prevision_demanda_db.phones WHERE user_id = %s", (user_id,))
            db_connection.connection.commit()
            cursor.close()

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nTeléfono borrado para user_id: {user_id}\n"
            self.logger.log(log_message)

            return jsonify({'message': 'Teléfono borrado exitosamente'}), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error al borrar el teléfono: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500