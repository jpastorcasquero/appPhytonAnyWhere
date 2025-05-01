from flask import Flask  # Importa la clase Flask del módulo flask para crear la aplicación web
from flask_cors import CORS  # Importa CORS del módulo flask_cors para manejar las políticas de CORS
from flask_socketio import SocketIO  # Importa SocketIO del módulo flask_socketio para manejar la comunicación en tiempo real

from Http.Routes.get_prediction_handler import get_prediction_bp
from Logger.logger import Logger  # Importa la clase Logger del módulo Logger para registrar eventos
import os  # Importa el módulo os para interactuar con el sistema operativo
from Http.Routes.users_handler import UsersHandler  # Importa el manejador de rutas para usuarios
from Http.Routes.addresses_handler import AddressesHandler  # Importa el manejador de rutas para direcciones
from Http.Routes.phones_handler import PhonesHandler  # Importa el manejador de rutas para teléfonos
from Http.Routes.connections_handler import ConnectionsHandler  # Importa el manejador de rutas para conexiones
from BBDD.database_connection import DatabaseConnection  # Importa la clase DatabaseConnection para manejar la conexión a la base de datos
from Http.Routes.reset_password_handler import reset_password_bp, ResetPasswordHandler  # Importa el manejador de rutas para restablecimiento de contraseña
from Http.Routes.get_classifier_handler import get_classifier_bp  # Importa el manejador de rutas para obtener el clasificador
from Http.Routes.get_prediction_handler import get_prediction_bp  # Importa el manejador de rutas para obtener el clasificador

class FlaskApp:
    def __init__(self, app_instance):
        # Inicializa la aplicación Flask
        self.app = Flask(__name__)
        # Configura CORS para permitir todas las orígenes y métodos
        CORS(self.app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})
        # Configura SocketIO para permitir todas las orígenes
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.app_instance = app_instance

        # Define la ruta para el archivo de log en "Archivos de Programa/JPC"
        program_files = os.getenv('ProgramFiles')
        log_path = os.path.join(program_files, 'JPC', 'log.txt')

        # Cargar las credenciales de la base de datos y conectar
        self.db_connection = DatabaseConnection.load_credentials()
        success = self.db_connection.connect()
        if not success:
            print(f"Error al conectar con la base de datos en la clase FlaskApp")

        # Crea una instancia de Logger
        self.logger = Logger(log_path, log_widget=app_instance.log_text if hasattr(app_instance, 'log_text') else None, db_connection=self.db_connection.connection)

        # Instanciar los manejadores de rutas
        self.users_handler = UsersHandler(self.app, self.logger)
        self.addresses_handler = AddressesHandler(self.app, self.logger)
        self.phones_handler = PhonesHandler(self.app, self.logger)
        self.connections_handler = ConnectionsHandler(self.app, self.logger)
        self.reset_password_handler = ResetPasswordHandler(self.logger)
        self.app.register_blueprint(reset_password_bp)
        self.app.register_blueprint(get_classifier_bp)
        self.app.register_blueprint(get_prediction_bp)

    def run(self):
        # Importa el servidor Waitress para servir la aplicación
        from waitress import serve
        # Sirve la aplicación en el host y puerto especificados
        serve(self.app, host='127.0.0.1', port=5001)
        # Ejecuta la aplicación con SocketIO en el host y puerto especificados, habilitando el modo debug
        self.socketio.run(self.app, host='127.0.0.1', port=5001, debug=True)
