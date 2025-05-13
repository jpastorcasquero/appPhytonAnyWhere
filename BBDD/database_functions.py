import os
from datetime import datetime
from BBDD.database_connection import DatabaseConnection
from BBDD.validator_UI import Validator

class DatabaseFunctions:
    def __init__(self, logger):
        self.db_connection = None
        self.db_connected = False

        home = os.path.expanduser("~")
        self.credentials_path = os.path.join(home, 'JPC', 'conexionBD.enc')
        self.log_path = os.path.join(home, 'JPC', 'log.txt')
        self.logger = logger

    def connect_to_database(self, host, database, user, password):
        db_connection = DatabaseConnection(host, database, user, password)
        success = db_connection.connect()
        if success:
            self.db_connection = db_connection
            self.db_connected = True
            db_connection.save_credentials()
            self.logger.log("Conexión a la base de datos establecida.")
            return True, "Conexión a la base de datos establecida."
        self.logger.log("Fallo al conectar con la base de datos.")
        return False, "Fallo al conectar con la base de datos."

    def load_and_connect(self):
        if os.path.exists(self.credentials_path):
            db_connection = DatabaseConnection.load_credentials()
            success = db_connection.connect()
            if success:
                self.db_connection = db_connection
                self.db_connected = True
                self.logger.log("Conexión a la base de datos establecida desde credenciales guardadas.")
                return True, "Conexión a la base de datos establecida desde credenciales guardadas."
            self.logger.log("Fallo al conectar con la base de datos desde credenciales guardadas.")
            return False, "Fallo al conectar con la base de datos desde credenciales guardadas."
        self.logger.log("No se encontraron credenciales guardadas.")
        return False, "No se encontraron credenciales guardadas."

    def disconnect_database(self):
        if self.db_connected and self.db_connection:
            success, message = self.db_connection.close()
            if success:
                self.db_connected = False
                self.db_connection = None
                self.logger.log("Base de datos desconectada.")
            else:
                self.logger.log(f"Error al desconectar la base de datos: {message}")
            return success, message
        self.logger.log("No hay conexión activa.")
        return False, "No hay conexión activa."

    def delete_config_file(self):
        if os.path.exists(self.credentials_path):
            os.remove(self.credentials_path)
            self.logger.log("Fichero de configuración borrado.")
            return True, "Fichero de configuración borrado."
        self.logger.log("El fichero de configuración no existe.")
        return False, "El fichero de configuración no existe."

    def log_event(self, message):
        return self.logger.log(message)

    def fetch_users_from_db(self):
        if self.db_connected:
            query = "SELECT id, name, nick_name, email, password, role, image FROM prevision_demanda_db.users ORDER BY id"
            users = self.db_connection.execute_query(query)
            self.logger.log("Usuarios obtenidos de la base de datos.")
            return users
        self.logger.log("No hay conexión activa a la base de datos.")
        return []

    def fetch_phone_data(self, user_id):
        if self.db_connected:
            query = f"SELECT country_code, phone FROM prevision_demanda_db.phones WHERE user_id = {user_id}"
            phone_data = self.db_connection.execute_query(query)
            self.logger.log(f"Datos de teléfono obtenidos para el usuario {user_id}.")
            return phone_data
        self.logger.log("No hay conexión activa a la base de datos.")
        return []

    def fetch_address_data(self, user_id):
        if self.db_connected:
            query = f"SELECT city, country, postal_code, address FROM prevision_demanda_db.addresses WHERE user_id = {user_id}"
            address_data = self.db_connection.execute_query(query)
            self.logger.log(f"Datos de dirección obtenidos para el usuario {user_id}.")
            return address_data[0] if address_data else None
        self.logger.log("No hay conexión activa a la base de datos.")
        return None

    def fetch_country_codes(self):
        if self.db_connected:
            query = "SELECT country_code, country_name FROM prevision_demanda_db.country_codes"
            country_codes = self.db_connection.execute_query(query)
            self.logger.log("Códigos de país obtenidos de la base de datos.")
            return {code: name for code, name in country_codes}
        self.logger.log("No hay conexión activa a la base de datos.")
        return {}

    def get_next_id(self, table_name):
        if self.db_connected:
            query = f"SELECT MAX(id) FROM prevision_demanda_db.{table_name}"
            result = self.db_connection.execute_query(query)
            next_id = result[0][0] + 1 if result and result[0][0] is not None else 1
            self.logger.log(f"Siguiente ID obtenido para la tabla {table_name}: {next_id}.")
            return next_id
        self.logger.log("No hay conexión activa a la base de datos.")
        return None
