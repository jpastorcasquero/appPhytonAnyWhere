from flask import jsonify, request
from BBDD.database_connection import DatabaseConnection
from datetime import datetime

class ConnectionsHandler:
    def __init__(self, app, logger):
        self.app = app
        self.logger = logger
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/connections', methods=['GET', 'POST'])
        def handle_connections():
            if request.method == 'GET':
                return self.get_all_connections()
            elif request.method == 'POST':
                return self.create_connection()

        @self.app.route('/connections/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
        def handle_connection_by_user(user_id):
            if request.method == 'GET':
                return self.get_connections_by_user(user_id)
            elif request.method == 'PUT':
                return self.update_connection(user_id)
            elif request.method == 'DELETE':
                return self.delete_connection(user_id)

    def get_all_connections(self):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Ejecutar la consulta para obtener las conexiones
            cursor = db_connection.connection.cursor()
            cursor.execute("SELECT * FROM prevision_demanda_db.connections")
            connections = cursor.fetchall()
            cursor.close()

            # Construir una lista de diccionarios con los resultados
            connection_list = [{'id': connection[0], 'user_id': connection[1], 'connection_date': connection[2], 'disconnection_date': connection[3]} for connection in connections]

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nRespuesta: {connection_list}\n"
            self.logger.log(log_message)

            return jsonify(connection_list), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error en la consulta: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def get_connections_by_user(self, user_id):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Ejecutar la consulta para obtener las conexiones por user_id
            cursor = db_connection.connection.cursor()
            cursor.execute("SELECT * FROM prevision_demanda_db.connections WHERE user_id = %s", (user_id,))
            connections = cursor.fetchall()
            cursor.close()

            # Construir una lista de diccionarios con los resultados
            connection_list = [{'id': connection[0], 'user_id': connection[1], 'connection_date': connection[2], 'disconnection_date': connection[3]} for connection in connections]

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nRespuesta: {connection_list}\n"
            self.logger.log(log_message)

            return jsonify(connection_list), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error en la consulta: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def create_connection(self):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Obtener los datos de la solicitud
            data = request.get_json()
            user_id = data.get('user_id')
            connection_date = data.get('connection_date')
            disconnection_date = data.get('disconnection_date')

            # Ejecutar la consulta para insertar la nueva conexión
            cursor = db_connection.connection.cursor()
            cursor.execute("""
                INSERT INTO prevision_demanda_db.connections (user_id, connection_date, disconnection_date)
                VALUES (%s, %s, %s)
            """, (user_id, connection_date, disconnection_date))
            db_connection.connection.commit()
            cursor.close()

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nDatos insertados: {data}\n"
            self.logger.log(log_message)

            return jsonify({'message': 'Conexión creada exitosamente'}), 201
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error al crear la conexión: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def update_connection(self, user_id):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Obtener los datos de la solicitud
            data = request.get_json()
            connection_date = data.get('connection_date')
            disconnection_date = data.get('disconnection_date')

            # Ejecutar la consulta para actualizar la conexión
            cursor = db_connection.connection.cursor()
            cursor.execute("""
                UPDATE prevision_demanda_db.connections
                SET connection_date = %s, disconnection_date = %s
                WHERE user_id = %s
            """, (connection_date, disconnection_date, user_id))
            db_connection.connection.commit()
            cursor.close()

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nDatos actualizados: {data}\n"
            self.logger.log(log_message)

            return jsonify({'message': 'Conexión actualizada exitosamente'}), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error al actualizar la conexión: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def delete_connection(self, user_id):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Ejecutar la consulta para borrar la conexión
            cursor = db_connection.connection.cursor()
            cursor.execute("DELETE FROM prevision_demanda_db.connections WHERE user_id = %s", (user_id,))
            db_connection.connection.commit()
            cursor.close()

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nConexión borrada para user_id: {user_id}\n"
            self.logger.log(log_message)

            return jsonify({'message': 'Conexión borrada exitosamente'}), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error al borrar la conexión: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500