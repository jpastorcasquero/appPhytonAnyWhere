from flask import jsonify, request

class AddressesHandler:
    def __init__(self, app, logger, db_connection):
        self.app = app
        self.logger = logger
        self.db_connection = db_connection

        if not self.db_connection or not self.db_connection.connection:
            self.logger.log("❌ No se pudo establecer la conexión en AddressesHandler")

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

    def ensure_connection(self):
        return self.db_connection and self.db_connection.ensure_connection()

    def get_all_addresses(self):
        if not self.ensure_connection():
            return jsonify({'error': 'No hay conexión a la base de datos'}), 500
        try:
            with self.db_connection.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM addresses")
                addresses = cursor.fetchall()
            address_list = [{
                'id': a['id'],
                'user_id': a['user_id'],
                'country': a['country'],
                'city': a['city'],
                'address': a['address'],
                'postal_code': a['postal_code']
            } for a in addresses]
            self.logger.log(f"[GET] /addresses -> {address_list}")
            return jsonify(address_list), 200
        except Exception as e:
            self.logger.log(f"❌ Error en get_all_addresses: {repr(e)}")
            return jsonify({'error': repr(e)}), 500

    def get_addresses_by_user(self, user_id):
        if not self.ensure_connection():
            return jsonify({'error': 'No hay conexión a la base de datos'}), 500
        try:
            with self.db_connection.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM addresses WHERE user_id = %s", (user_id,))
                addresses = cursor.fetchall()
            address_list = [{
                'id': a['id'],
                'user_id': a['user_id'],
                'country': a['country'],
                'city': a['city'],
                'address': a['address'],
                'postal_code': a['postal_code']
            } for a in addresses]
            self.logger.log(f"[GET] /addresses/{user_id} -> {address_list}")
            return jsonify(address_list), 200
        except Exception as e:
            self.logger.log(f"❌ Error en get_addresses_by_user: {repr(e)}")
            return jsonify({'error': repr(e)}), 500

    def create_address(self):
        if not self.ensure_connection():
            return jsonify({'error': 'No hay conexión a la base de datos'}), 500
        try:
            data = request.get_json()
            self.logger.log(f"📥 Datos recibidos en POST /addresses: {data}")

            required_fields = ['user_id', 'country', 'city', 'address', 'postal_code']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Falta el campo obligatorio: {field}'}), 400

            with self.db_connection.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO addresses (user_id, country, city, address, postal_code)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    data['user_id'], data['country'], data['city'],
                    data['address'], data['postal_code']
                ))
                self.db_connection.connection.commit()
                new_id = cursor.lastrowid

            response = {
                'id': new_id,
                'user_id': data['user_id'],
                'country': data['country'],
                'city': data['city'],
                'address': data['address'],
                'postal_code': data['postal_code']
            }

            self.logger.log(f"✅ Dirección insertada: {response}")
            return jsonify(response), 201
        except Exception as e:
            self.logger.log(f"❌ Error en create_address: {repr(e)}")
            return jsonify({'error': repr(e)}), 500

    def update_address(self, user_id):
        if not self.ensure_connection():
            return jsonify({'error': 'No hay conexión a la base de datos'}), 500
        try:
            data = request.get_json()
            with self.db_connection.connection.cursor() as cursor:
                cursor.execute("SELECT id FROM addresses WHERE user_id = %s", (user_id,))
                existing = cursor.fetchone()

                if existing:
                    cursor.execute("""
                        UPDATE addresses
                        SET country = %s, city = %s, address = %s, postal_code = %s
                        WHERE user_id = %s
                    """, (
                        data['country'], data['city'], data['address'],
                        data['postal_code'], user_id
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO addresses (user_id, country, city, address, postal_code)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        user_id, data['country'], data['city'], data['address'], data['postal_code']
                    ))

                self.db_connection.connection.commit()

            self.logger.log(f"[PUT] /addresses/{user_id} -> {data}")
            return jsonify({'message': 'Dirección guardada correctamente'}), 200
        except Exception as e:
            self.logger.log(f"❌ Error en update_address: {repr(e)}")
            return jsonify({'error': repr(e)}), 500

    def delete_address(self, user_id):
        if not self.ensure_connection():
            return jsonify({'error': 'No hay conexión a la base de datos'}), 500
        try:
            with self.db_connection.connection.cursor() as cursor:
                cursor.execute("DELETE FROM addresses WHERE user_id = %s", (user_id,))
                self.db_connection.connection.commit()
            self.logger.log(f"[DELETE] /addresses/{user_id} -> eliminado")
            return jsonify({'message': 'Dirección eliminada correctamente'}), 200
        except Exception as e:
            self.logger.log(f"❌ Error en delete_address: {repr(e)}")
            return jsonify({'error': repr(e)}), 500
