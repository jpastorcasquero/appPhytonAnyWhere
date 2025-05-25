from flask import jsonify, request

class PhonesHandler:
    def __init__(self, app, logger, db_connection):
        self.app = app
        self.logger = logger
        self.db_connection = db_connection
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

    def ensure_connection(self):
        if not self.db_connection or not self.db_connection.connection:
            self.logger.log("❌ Conexión a base de datos no disponible")
            return False
        return True

    def get_all_phones(self):
        if not self.ensure_connection():
            return jsonify({'error': 'Conexión no disponible'}), 500
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("SELECT * FROM phones")
            phones = cursor.fetchall()
            cursor.close()

            phone_list = []
            for p in phones:
                phone_list.append({
                    'id': p['id'],
                    'user_id': p['user_id'],
                    'country_code': p['country_code'],
                    'phone': p['phone']
                })


            self.logger.log(f"[GET] /phones -> {phone_list}")
            return jsonify(phone_list), 200
        except Exception as e:
            self.logger.log(f"❌ Error en get_all_phones: {repr(e)}")
            return jsonify({'error': str(e)}), 500

    def get_phones_by_user(self, user_id):
        if not self.ensure_connection():
            return jsonify({'error': 'Conexión no disponible'}), 500
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("SELECT * FROM phones WHERE user_id = %s", (user_id,))
            phones = cursor.fetchall()
            cursor.close()

            phone_list = []
            for p in phones:
                phone_list.append({
                        'id': p['id'],
                        'user_id': p['user_id'],
                        'country_code': p['country_code'],
                        'phone': p['phone']
                    })

            self.logger.log(f"[GET] /phones/{user_id} -> {phone_list}")
            return jsonify(phone_list), 200
        except Exception as e:
            self.logger.log(f"❌ Error en get_phones_by_user: {repr(e)}")
            return jsonify({'error': str(e)}), 500

    def create_phone(self):
        if not self.ensure_connection():
            return jsonify({'error': 'Conexión no disponible'}), 500
        try:
            data = request.get_json()
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                INSERT INTO phones (user_id, country_code, phone)
                VALUES (%s, %s, %s)
            """, (
                data.get('user_id'),
                data.get('country_code'),
                data.get('phone')
            ))
            self.db_connection.connection.commit()
            cursor.close()

            self.logger.log(f"[POST] /phones -> {data}")
            return jsonify({'message': 'Teléfono creado exitosamente'}), 201
        except Exception as e:
            self.logger.log(f"❌ Error en create_phone: {repr(e)}")
            return jsonify({'error': str(e)}), 500


    def update_phone(self, phone_id):
        if not self.ensure_connection():
            return jsonify({'error': 'Conexión no disponible'}), 500
        try:
            data = request.get_json()
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                UPDATE phones
                SET country_code = %s, phone = %s
                WHERE id = %s
            """, (
                data.get('country_code'),
                data.get('phone'),
                phone_id
            ))
            self.db_connection.connection.commit()
            cursor.close()
    
            self.logger.log(f"[PUT] /phones/{phone_id} -> {data}")
            return jsonify({'message': 'Teléfono actualizado exitosamente'}), 200
        except Exception as e:
            self.logger.log(f"❌ Error en update_phone: {repr(e)}")
            return jsonify({'error': str(e)}), 500


    def delete_phone(self, user_id):
        if not self.ensure_connection():
            return jsonify({'error': 'Conexión no disponible'}), 500
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("DELETE FROM phones WHERE id = %s", (user_id,))
            self.db_connection.connection.commit()
            cursor.close()

            self.logger.log(f"[DELETE] /phones/{user_id} (id del teléfono) -> eliminado")
            return jsonify({'message': 'Teléfono borrado exitosamente'}), 200
        except Exception as e:
            self.logger.log(f"❌ Error en delete_phone: {repr(e)}")
            return jsonify({'error': str(e)}), 500
