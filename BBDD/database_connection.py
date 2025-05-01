import mysql.connector
from mysql.connector import Error
from cryptography.fernet import Fernet
import os
import sys
from pathlib import Path
from Logger.logger import Logger


class DatabaseConnection:
    def __init__(self, host=None, database=None, user=None, password=None, port=3306):
        # Configuración inicial con valores por defecto para PythonAnywhere
        self.host = host or 'jpastorcasquero.mysql.pythonanywhere-services.com'
        self.database = database or 'jpastorcasquero$prevision_demanda'
        self.user = user or 'jpastorcasquero'
        self.password = password or 'JPc11082006'
        self.port = port
        self.connection = None

        # Configuración portable de rutas
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.LOG_DIR = self.BASE_DIR / 'logs'
        self.LOG_DIR.mkdir(exist_ok=True, parents=True)

        log_path = self.LOG_DIR / 'database.log'
        self.logger = Logger(str(log_path), db_connection=self.connection)

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.logger.db_connection = self.connection
            return True, "Conexión exitosa"
        except Error as e:
            error_msg = f"Error al conectar a MySQL: {e}"
            self.logger.log(error_msg)
            return False, error_msg

    def save_credentials(self, filename='db_credentials.enc'):
        """Guarda credenciales cifradas de forma portable"""
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)

        credentials = f"{self.host},{self.database},{self.user},{self.password},{self.port}"
        encrypted_credentials = cipher_suite.encrypt(credentials.encode())

        # Guardar en directorio seguro
        creds_dir = self.BASE_DIR / 'secure'
        creds_dir.mkdir(exist_ok=True, mode=0o700)

        with open(creds_dir / filename, 'wb') as file:
            file.write(key + b'\n' + encrypted_credentials)

    @staticmethod
    def load_credentials(filename='db_credentials.enc'):
        """Carga credenciales de forma portable"""
        base_dir = Path(__file__).resolve().parent.parent
        creds_path = base_dir / 'secure' / filename

        with open(creds_path, 'rb') as file:
            key = file.readline().strip()
            encrypted_credentials = file.read().strip()

        cipher_suite = Fernet(key)
        decrypted = cipher_suite.decrypt(encrypted_credentials).decode()
        host, database, user, password, port = decrypted.split(',')

        return DatabaseConnection(host, database, user, password, int(port))

    def execute_query(self, query, params=None, fetch=True):
        try:
            cursor = self.connection.cursor(dictionary=True)  # Devuelve resultados como diccionarios
            cursor.execute(query, params or ())

            if fetch and query.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE")):
                results = cursor.fetchall()
            else:
                self.connection.commit()
                results = cursor.rowcount

            cursor.close()
            self.logger.log(f"Consulta ejecutada: {query[:100]}...")  # Log parcial por seguridad
            return results
        except Error as e:
            self.logger.log(f"Error en consulta: {e}\nConsulta: {query[:200]}...")
            return None

    def close(self):
        if self.connection:
            try:
                self.logger.log("Cerrando conexión a MySQL")
                self.connection.close()
                self.connection = None
                return True, "Conexión cerrada correctamente"
            except Error as e:
                error_msg = f"Error al cerrar conexión: {e}"
                self.logger.log(error_msg)
                return False, error_msg
        return False, "No había conexión activa"