from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO  # Puedes comentar esta línea si no usas sockets realmente
import os

from Logger.logger import Logger
from BBDD.database_connection import DatabaseConnection

from Http.Routes.get_prediction_handler import get_prediction_bp
from Http.Routes.get_classifier_handler import get_classifier_bp
from Http.Routes.reset_password_handler import reset_password_bp, ResetPasswordHandler
from Http.Routes.users_handler import UsersHandler
from Http.Routes.addresses_handler import AddressesHandler
from Http.Routes.phones_handler import PhonesHandler
from Http.Routes.connections_handler import ConnectionsHandler
from Http.Routes.users_api import users_api


class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__)

        # Registrar blueprint de API REST
        self.app.register_blueprint(users_api)

        # Configurar CORS para permitir peticiones de cualquier origen
        CORS(self.app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})

        # SocketIO (comenta si no se usa)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Crear carpeta de logs en home si no existe (compatible con Linux)
        os.makedirs('/home/jpastorcasquero/JPC', exist_ok=True)
        log_path = '/home/jpastorcasquero/JPC/log.txt'

        # Conectar a la base de datos usando credenciales cifradas
        self.db_connection = DatabaseConnection.load_credentials()
        success = self.db_connection.connect()
        if not success:
            print("❌ Error al conectar con la base de datos en FlaskApp")

        # Inicializar el logger
        self.logger = Logger(log_path, db_connection=self.db_connection.connection)

        # Instanciar manejadores de rutas
        self.users_handler = UsersHandler(self.app, self.logger)
        self.addresses_handler = AddressesHandler(self.app, self.logger)
        self.phones_handler = PhonesHandler(self.app, self.logger)
        self.connections_handler = ConnectionsHandler(self.app, self.logger)
        self.reset_password_handler = ResetPasswordHandler(self.logger)

        # Registrar blueprints adicionales
        self.app.register_blueprint(reset_password_bp)
        self.app.register_blueprint(get_classifier_bp)
        self.app.register_blueprint(get_prediction_bp)

        # Ruta adicional incluida correctamente
        @self.app.route("/usuarios")
        def usuarios_page():
            return render_template("usuarios.html")  # Asegúrate de tener templates/usuarios.html

    def run(self):
        # SOLO usar en desarrollo local
        if os.getenv('PA_ENV') is None:  # PA_ENV solo existe en PythonAnywhere
            self.app.run(host='127.0.0.1', port=5001, debug=True)
