from flask import jsonify, request

class PhonesHandler:
    def __init__(self, app, logger, db_connection):
        self.app = app
        self.logger = logger
        self.db_connection = db_connection  # ✅ Se reutiliza la conexión principal

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
        try:
            with self.db_connection.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM phones")
                phones = cursor.fetchall()

            phone_list = [{'id': p[0], 'user_id': p[1], 'country_code': p[2], 'phone': p[3]} for p in phones]
            self.logger.log(f"[GET] /phones -> {phone_list}")
            return jsonify(phone_list), 200
        except Exception as e:
            self.logger.log(f"❌ Error en get_all_phones: {e}")
            return jsonify({'error': str(e)}), 500

    def get_phones_by_user(self, user_id):
        try:
            with self.db_connection.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM phones WHERE user_id = %s", (user_id,))
                phones = cursor.fetchall()

            phone_list = [{'id': p[0], 'user_id': p[1], 'country_code': p[2], 'phone': p[3]} for p in phones]
            self.logger.log(f"[GET] /phones/{user_id} -> {phone_list}")
            return jsonify(phone_list), 200
        except Exception as e:
            self.logger.log(f"❌ Error en get_phones_by_user: {e}")
            return jsonify({'error': str(e)}), 500

    def create_phone(self):
        try:
            data = request.get_json()
            with self.db_connection.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO phones (user_id, country_code, phone)
                    VALUES (%s, %s, %s)
                """, (
                    data.get('user_id'),
                    data.get('country_code'),
                    data.get('phone')
                ))
                self.db_connection.connection.commit()

            self.logger.log(f"[POST] /phones -> {data}")
            return jsonify({'message': 'Teléfono creado exitosamente'}), 201
        except Exception as e:
            self.logger.log(f"❌ Error en create_phone: {e}")
            return jsonify({'error': str(e)}), 500

    def update_phone(self, user_id):
        try:
            data = request.get_json()
            with self.db_connection.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE phones
                    SET country_code = %s, phone = %s
                    WHERE user_id = %s
                """, (
                    data.get('country_code'),
                    data.get('phone'),
                    user_id
                ))
                self.db_connection.connection.commit()

            self.logger.log(f"[PUT] /phones/{user_id} -> {data}")
            return jsonify({'message': 'Teléfono actualizado exitosamente'}), 200
        except Exception as e:
            self.logger.log(f"❌ Error en update_phone: {e}")
            return jsonify({'error': str(e)}), 500

    def delete_phone(self, user_id):
        try:
            with self.db_connection.connection.cursor() as cursor:
                cursor.execute("DELETE FROM phones WHERE user_id = %s", (user_id,))
                self.db_connection.connection.commit()

            self.logger.log(f"[DELETE] /phones/{user_id} -> eliminado")
            return jsonify({'message': 'Teléfono borrado exitosamente'}), 200
        except Exception as e:
            self.logger.log(f"❌ Error en delete_phone: {e}")
            return jsonify({'error': str(e)}), 500
