from BBDD.database_connection import DatabaseConnection

class DatabaseFunctions:
    def __init__(self, logger):
        self.logger = logger
        self.db_connection = None

    def load_and_connect(self):
        db_connection = DatabaseConnection(
            host="jpastorcasquero.mysql.pythonanywhere-services.com",
            database="jpastorcasquero$prevision_demanda_db",
            user="jpastorcasquero",
            password="JPc11082006"
        )
        success = db_connection.connect()
        if success:
            self.db_connection = db_connection
            self.logger.log("✅ Conexión directa establecida.")
            return True, "Conexión directa establecida."
        self.logger.log("❌ Fallo al conectar con la base de datos.")
        return False, "Fallo al conectar con la base de datos."

    def fetch_users_from_db(self):
        if not self.db_connection or not self.db_connection.is_connected():
            return []
        query = "SELECT id, name, nick_name, email, password, role, image FROM users ORDER BY id"
        return self.db_connection.execute_query(query)

    def create_user_from_json(self, data):
        if self.db_connection and self.db_connection.is_connected():
            try:
                query = """
                    INSERT INTO users (name, email, nick_name, role, image, password)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                params = (
                    data.get('name'), data.get('email'), data.get('nick_name'),
                    data.get('role'), data.get('image'), data.get('password')
                )
                with self.db_connection.connection.cursor() as cursor:
                    cursor.execute(query, params)
                self.db_connection.connection.commit()
                return True, "Usuario creado exitosamente."
            except Exception as e:
                self.logger.log(f"❌ Error al crear usuario desde JSON: {e}")
                return False, str(e)
        return False, "No hay conexión activa."

    def save_user_data_from_json(self, user_id, data):
        if self.db_connection and self.db_connection.is_connected():
            try:
                query = """
                    UPDATE users SET name = %s, email = %s, nick_name = %s, role = %s, image = %s, password = %s
                    WHERE id = %s
                """
                params = (
                    data.get('name'), data.get('email'), data.get('nick_name'),
                    data.get('role'), data.get('image'), data.get('password'), user_id
                )
                with self.db_connection.connection.cursor() as cursor:
                    cursor.execute(query, params)
                self.db_connection.connection.commit()
                return True, "Usuario actualizado correctamente."
            except Exception as e:
                self.logger.log(f"❌ Error al actualizar usuario desde JSON: {e}")
                return False, str(e)
        return False, "No hay conexión activa."

    def delete_user(self, user_id):
        if self.db_connection and self.db_connection.is_connected():
            try:
                with self.db_connection.connection.cursor() as cursor:
                    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                self.db_connection.connection.commit()
                return True, "Usuario eliminado correctamente"
            except Exception as e:
                self.logger.log(f"❌ Error al eliminar usuario: {e}")
                return False, str(e)
        return False, "No hay conexión activa."

    def check_connection(self):
        return self.db_connection and self.db_connection.is_connected()
