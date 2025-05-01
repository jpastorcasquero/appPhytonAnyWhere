# BBDD/database_functions.py
import pymysql

class DatabaseFunctions:
    def __init__(self, logger=None):
        self.logger = logger
        self.conn = None

    def load_and_connect(self):
        try:
            self.conn = pymysql.connect(
                host="jpastorcasquero.mysql.pythonanywhere-services.com",
                user="jpastorcasquero",
                password="JPc11082006",
                database="jpastorcasquero$default",
                cursorclass=pymysql.cursors.DictCursor
            )
            if self.logger:
                self.logger.log("Conexión exitosa a la base de datos.")
        except Exception as e:
            if self.logger:
                self.logger.log(f"Error de conexión: {e}")
            raise

    def fetch_users_from_db(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()

    def fetch_country_codes(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT codigo, nombre FROM codigos_pais")
            return {row['codigo']: row['nombre'] for row in cursor.fetchall()}

    def fetch_phone_data(self, user_id):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT codigo_pais, numero FROM telefonos WHERE user_id = %s", (user_id,))
            return cursor.fetchall()

    def fetch_address_data(self, user_id):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT ciudad, pais, codigo_postal, direccion FROM direcciones WHERE user_id = %s", (user_id,))
            return cursor.fetchone()

    def create_user(self, entries):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (name, username, email, password, role, avatar)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    entries['Nombre'], entries['Nombre_de_usuario'], entries['Correo'],
                    entries['Contraseña'], entries['Rol'], entries['Imagen']
                ))
                user_id = cursor.lastrowid

                if entries['Teléfono 1']:
                    cursor.execute("INSERT INTO telefonos (user_id, codigo_pais, numero) VALUES (%s, %s, %s)",
                                   (user_id, entries['Código de País 1'], entries['Teléfono 1']))

                if entries['Teléfono 2']:
                    cursor.execute("INSERT INTO telefonos (user_id, codigo_pais, numero) VALUES (%s, %s, %s)",
                                   (user_id, entries['Código de País 2'], entries['Teléfono 2']))

                cursor.execute("""
                    INSERT INTO direcciones (user_id, ciudad, pais, codigo_postal, direccion)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, entries['Ciudad'], entries['País'], entries['Código postal'], entries['Dirección']))

            self.conn.commit()
            return True, "Usuario creado correctamente."
        except Exception as e:
            return False, f"Error al crear usuario: {e}"

    def save_user_data(self, user_id, entries):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users SET name=%s, username=%s, email=%s, password=%s, role=%s, avatar=%s
                    WHERE id=%s
                """, (
                    entries['Nombre'], entries['Nombre_de_usuario'], entries['Correo'],
                    entries['Contraseña'], entries['Rol'], entries['Imagen'], user_id
                ))

                cursor.execute("DELETE FROM telefonos WHERE user_id = %s", (user_id,))
                if entries['Teléfono 1']:
                    cursor.execute("INSERT INTO telefonos (user_id, codigo_pais, numero) VALUES (%s, %s, %s)",
                                   (user_id, entries['Código de País 1'], entries['Teléfono 1']))
                if entries['Teléfono 2']:
                    cursor.execute("INSERT INTO telefonos (user_id, codigo_pais, numero) VALUES (%s, %s, %s)",
                                   (user_id, entries['Código de País 2'], entries['Teléfono 2']))

                cursor.execute("""
                    UPDATE direcciones SET ciudad=%s, pais=%s, codigo_postal=%s, direccion=%s
                    WHERE user_id=%s
                """, (entries['Ciudad'], entries['País'], entries['Código postal'], entries['Dirección'], user_id))

            self.conn.commit()
            return True, "Usuario actualizado correctamente."
        except Exception as e:
            return False, f"Error al actualizar usuario: {e}"

    def delete_user(self, user_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM direcciones WHERE user_id = %s", (user_id,))
                cursor.execute("DELETE FROM telefonos WHERE user_id = %s", (user_id,))
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            self.conn.commit()
            return True, "Usuario eliminado correctamente."
        except Exception as e:
            return False, f"Error al eliminar usuario: {e}"
