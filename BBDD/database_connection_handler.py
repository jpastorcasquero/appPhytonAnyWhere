import os
from BBDD.database_functions import DatabaseFunctions
from BBDD.database_connection import DatabaseConnection
from Logger.logger import Logger

class DatabaseConnectionHandler:
    def __init__(self, logger=None):
        if logger is None:
            log_path = os.path.expanduser('~/JPC/log.txt')
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            logger = Logger(log_path)

        self.logger = logger
        self.functions = DatabaseFunctions(logger)
        self.functions.load_and_connect()

        # Conexión directa a MySQL
        db_connection = DatabaseConnection(
            host="jpastorcasquero.mysql.pythonanywhere-services.com",
            database="jpastorcasquero$prevision_demanda_db",
            user="jpastorcasquero",
            password="JPc11082006"
        )
        success = db_connection.connect()

        # ⬇️ Esto es lo que faltaba
        self.db_connection = db_connection

        # Inicializar funciones de base de datos
        self.functions = DatabaseFunctions(self.logger)
        self.functions.db_connection = db_connection
        self.functions.db_connected = success

        # Logs de depuración
        self.logger.log(f"db_connection: {self.db_connection}")
        self.logger.log(f"db_connection.connection: {self.db_connection.connection}")

        if not success:
            self.logger.log("❌ Error al conectar a la base de datos.")
