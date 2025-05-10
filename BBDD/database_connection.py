import os
import mysql.connector
from mysql.connector import Error
from cryptography.fernet import Fernet
from Logger.logger import Logger

class DatabaseConnection:
    def __init__(self, host=None, database=None, user=None, password=None):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

        # Directorio seguro para logs en entorno Linux
        log_dir = os.path.join(os.path.expanduser("~"), 'JPC')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'log.txt')
        self.logger = Logger(log_path, db_connection=self.connection)

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                self.logger.db_connection = self.connection
                self.logger.log("✅ Conexión a MySQL exitosa.")
                return True
            else:
                self.logger.log("❌ Conexión fallida: estado no conectado.")
                return False, "No se pudo conectar"
        except Error as e:
            self.logger.log(f"❌ Error al conectar a MySQL: {e}")
            return False, str(e)

    def save_credentials(self, filename='conexionBD.enc'):
        # Ruta donde se almacenan las credenciales cifradas
        program_path = os.path.join(os.path.expanduser("~"), 'JPC')
        save_path = os.path.join(program_path, filename)

        if os.path.exists(save_path):
            self.logger.log("ℹ️ Credenciales ya existen, no se sobrescriben.")
            return

        # Cifrado y guardado de credenciales
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        credentials = f"{self.host},{self.database},{self.user},{self.password}"
        encrypted_credentials = cipher_suite.encrypt(credentials.encode())

        os.makedirs(program_path, exist_ok=True)
        with open(save_path, 'wb') as file:
            file.write(key + b'\n' + encrypted_credentials)

        self.logger.log("🔐 Credenciales guardadas de forma segura.")

    @staticmethod
    def load_credentials(filename='conexionBD.enc'):
        program_path = os.path.join(os.path.expanduser("~"), 'JPC')
        load_path = os.path.join(program_path, filename)

        if not os.path.exists(load_path):
            raise FileNotFoundError("❌ No se encontró el archivo de credenciales.")

        with open(load_path, 'rb') as file:
            key = file.readline().strip()
            encrypted_credentials = file.read().strip()

        cipher_suite = Fernet(key)
        decrypted_credentials = cipher_suite.decrypt(encrypted_credentials).decode()
        host, database, user, password = decrypted_credentials.split(',')

        return DatabaseConnection(host, database, user, password)

    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params) if params else cursor.execute(query)

                if query.strip().lower().startswith("select"):
                    results = cursor.fetchall()
                else:
                    self.connection.commit()
                    results = cursor.rowcount

            self.logger.log(f"🟢 Consulta ejecutada: {query} | Params: {params}")
            return results
        except Error as e:
            self.logger.log(f"❌ Error al ejecutar consulta: {e}")
            return []

    def close(self):
        if self.connection and self.connection.is_connected():
            try:
                self.connection.close()
                self.logger.log("🔌 Conexión MySQL cerrada correctamente.")
                return True, "Desconexión exitosa"
            except Error as e:
                self.logger.log(f"❌ Error al cerrar conexión: {e}")
                return False, str(e)
        self.logger.log("⚠️ No hay conexión activa para cerrar.")
        return False, "No hay conexión activa."
