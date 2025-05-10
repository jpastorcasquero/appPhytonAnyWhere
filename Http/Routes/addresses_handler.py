from flask import jsonify, request
from BBDD.database_connection import DatabaseConnection
from datetime import datetime

class AddressesHandler:
    def __init__(self, app, logger):
        self.app = app
        self.logger = logger
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/addresses', methods=['GET', 'POST'])
        def handle_addresses():
            if request.method == 'GET':
                return self.get_all_addresses()
            elif request.method == 'POST':
                return self.create_address()

        @self.app.route('/addresses/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
        def handle_address_by_user(user_id):
            if request.method == 'GET':
                return self.get_addresses_by_user(user_id)
            elif request.method == 'PUT':
                return self.update_address(user_id)
            elif request.method == 'DELETE':
                return self.delete_address(user_id)

    def get_all_addresses(self):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Ejecutar la consulta para obtener las direcciones
            cursor = db_connection.connection.cursor()
            cursor.execute("SELECT * FROM addresses")
            addresses = cursor.fetchall()
            cursor.close()

            # Construir una lista de diccionarios con los resultados
            address_list = [{'id': address[0], 'user_id': address[1], 'country': address[2], 'city': address[3],
                             'address': address[4], 'postal_code': address[5]} for address in addresses]

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nRespuesta: {address_list}\n"
            self.logger.log(log_message)

            return jsonify(address_list), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error en la consulta: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def get_addresses_by_user(self, user_id):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Ejecutar la consulta para obtener las direcciones por user_id
            cursor = db_connection.connection.cursor()
            cursor.execute("SELECT * FROM addresses WHERE user_id = %s", (user_id,))
            addresses = cursor.fetchall()
            cursor.close()

            # Construir una lista de diccionarios con los resultados
            address_list = [{'id': address[0], 'user_id': address[1], 'country': address[2], 'city': address[3],
                             'address': address[4], 'postal_code': address[5]} for address in addresses]

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nRespuesta: {address_list}\n"
            self.logger.log(log_message)

            return jsonify(address_list), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error en la consulta: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def create_address(self):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Obtener los datos de la solicitud
            data = request.get_json()
            user_id = data.get('user_id')
            country = data.get('country')
            city = data.get('city')
            address = data.get('address')
            postal_code = data.get('postal_code')

            # Ejecutar la consulta para insertar la nueva dirección
            cursor = db_connection.connection.cursor()
            cursor.execute("""
                INSERT INTO addresses (user_id, country, city, address, postal_code)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, country, city, address, postal_code))
            db_connection.connection.commit()
            cursor.close()

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nDatos insertados: {data}\n"
            self.logger.log(log_message)

            return jsonify({'message': 'Dirección creada exitosamente'}), 201
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error al crear la dirección: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def update_address(self, user_id):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Obtener los datos de la solicitud
            data = request.get_json()
            country = data.get('country')
            city = data.get('city')
            address = data.get('address')
            postal_code = data.get('postal_code')

            # Ejecutar la consulta para actualizar la dirección
            cursor = db_connection.connection.cursor()
            cursor.execute("""
                UPDATE addresses
                SET country = %s, city = %s, address = %s, postal_code = %s
                WHERE user_id = %s
            """, (country, city, address, postal_code, user_id))
            db_connection.connection.commit()
            cursor.close()

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nDatos actualizados: {data}\n"
            self.logger.log(log_message)

            return jsonify({'message': 'Dirección actualizada exitosamente'}), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error al actualizar la dirección: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500

    def delete_address(self, user_id):
        # Cargar las credenciales de la base de datos
        db_connection = DatabaseConnection.load_credentials()
        success = db_connection.connect()

        if not success:
            return jsonify({'error': 'Fallo al conectar con la base de datos.'}), 500

        try:
            # Ejecutar la consulta para borrar la dirección
            cursor = db_connection.connection.cursor()
            cursor.execute("DELETE FROM addresses WHERE user_id = %s", (user_id,))
            db_connection.connection.commit()
            cursor.close()

            # Registrar la petición y la respuesta en el archivo de logs
            log_message = f"Petición recibida: {request.url}\nDirección borrada para user_id: {user_id}\n"
            self.logger.log(log_message)

            return jsonify({'message': 'Dirección borrada exitosamente'}), 200
        except Exception as e:
            # Registrar el error en el archivo de logs
            log_message = f"Error al borrar la dirección: {str(e)}\n"
            self.logger.log(log_message)

            return jsonify({'error': str(e)}), 500