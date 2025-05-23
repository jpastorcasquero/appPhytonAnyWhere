from flask import jsonify, request
from BBDD.database_connection_handler import DatabaseConnectionHandler
from Logger.logger import Logger

class ConnectionsHandler:
    def __init__(self, app, logger):
        self.app = app
        self.logger = logger

        # Obtener conexión ya establecida desde el handler
        handler = DatabaseConnectionHandler(logger)
        self.db_connection = handler.functions.db_connection

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
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("SELECT * FROM connections")
            connections = cursor.fetchall()
            cursor.close()

            connection_list = [{'id': c[0], 'user_id': c[1], 'connection_date': c[2], 'disconnection_date': c[3]} for c in connections]
            self.logger.log(f"[GET] /connections -> {connection_list}")
            return jsonify(connection_list), 200
        except Exception as e:
            self.logger.log(f"❌ Error en get_all_connections: {e}")
            return jsonify({'error': str(e)}), 500

    def get_connections_by_user(self, user_id):
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("SELECT * FROM connections WHERE user_id = %s", (user_id,))
            connections = cursor.fetchall()
            cursor.close()

            connection_list = [{'id': c[0], 'user_id': c[1], 'connection_date': c[2], 'disconnection_date': c[3]} for c in connections]
            self.logger.log(f"[GET] /connections/{user_id} -> {connection_list}")
            return jsonify(connection_list), 200
        except Exception as e:
            self.logger.log(f"❌ Error en get_connections_by_user: {e}")
            return jsonify({'error': str(e)}), 500

    def create_connection(self):
        try:
            data = request.get_json()
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                INSERT INTO connections (user_id, connection_date, disconnection_date)
                VALUES (%s, %s, %s)
            """, (
                data.get('user_id'),
                data.get('connection_date'),
                data.get('disconnection_date')
            ))
            self.db_connection.connection.commit()
            cursor.close()

            self.logger.log(f"[POST] /connections -> {data}")
            return jsonify({'message': 'Conexión creada exitosamente'}), 201
        except Exception as e:
            self.logger.log(f"❌ Error en create_connection: {e}")
            return jsonify({'error': str(e)}), 500

    def update_connection(self, user_id):
        try:
            data = request.get_json()
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                UPDATE connections
                SET connection_date = %s, disconnection_date = %s
                WHERE user_id = %s
            """, (
                data.get('connection_date'),
                data.get('disconnection_date'),
                user_id
            ))
            self.db_connection.connection.commit()
            cursor.close()

            self.logger.log(f"[PUT] /connections/{user_id} -> {data}")
            return jsonify({'message': 'Conexión actualizada exitosamente'}), 200
        except Exception as e:
            self.logger.log(f"❌ Error en update_connection: {e}")
            return jsonify({'error': str(e)}), 500

    def delete_connection(self, user_id):
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("DELETE FROM connections WHERE user_id = %s", (user_id,))
            self.db_connection.connection.commit()
            cursor.close()

            self.logger.log(f"[DELETE] /connections/{user_id} -> eliminado")
            return jsonify({'message': 'Conexión borrada exitosamente'}), 200
        except Exception as e:
            self.logger.log(f"❌ Error en delete_connection: {e}")
            return jsonify({'error': str(e)}), 500
