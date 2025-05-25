from flask import Flask, render_template, request, jsonify, redirect
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import atexit

from Logger.logger import Logger
from BBDD.database_connection import DatabaseConnection

from Http.Routes.get_prediction_handler import get_prediction_bp
from Http.Routes.get_classifier_handler import get_classifier_bp
from Http.Routes.reset_password_handler import reset_password_bp, ResetPasswordHandler
from Http.Routes.users_handler import UsersHandler
from Http.Routes.addresses_handler import AddressesHandler
from Http.Routes.phones_handler import PhonesHandler
from Http.Routes.connections_handler import ConnectionsHandler
from Http.Routes.users_api import create_users_routes
from BBDD.database_functions import DatabaseFunctions
from Http.Routes.avatar_routes import avatar_bp
from Http.Routes.password_reset_service import PasswordResetService


class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__, static_folder="static")

        # ✅ Configuración de CORS para producción
        CORS(self.app, supports_credentials=True, resources={
            r"/*": {
                "origins": [
                    "http://localhost:4200",                    # para desarrollo local
                    "https://tu-dominio-produccion.com"        # sustituye por tu dominio real
                ],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })

        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        os.makedirs('/home/jpastorcasquero/JPC', exist_ok=True)
        log_path = '/home/jpastorcasquero/JPC/log.txt'

        # 🔌 Conexión a la base de datos
        self.db_connection = DatabaseConnection(
            host="jpastorcasquero.mysql.pythonanywhere-services.com",
            database="jpastorcasquero$prevision_demanda_db",
            user="jpastorcasquero",
            password="JPc11082006"
        )
        success = self.db_connection.connect()
        if not success:
            print("❌ Error al conectar con la base de datos en FlaskApp")

        # 📝 Logger con conexión activa
        self.logger = Logger(log_path, db_connection=self.db_connection.connection)

        # 🚏 Handlers
        self.users_handler = UsersHandler(self.app, self.logger)
        self.addresses_handler = AddressesHandler(self.app, self.logger, self.db_connection)
        self.phones_handler = PhonesHandler(self.app, self.logger, self.db_connection)
        self.connections_handler = ConnectionsHandler(self.app, self.logger, self.db_connection)
        self.reset_password_handler = ResetPasswordHandler(self.logger, self.db_connection)
        self.reset_service = PasswordResetService(self.logger, self.db_connection)

        # 🔁 Blueprints RESTful
        self.functions = DatabaseFunctions(self.logger)
        self.functions.db_connection = self.db_connection
        create_users_routes(self.app, self.logger, self.functions)
        self.app.register_blueprint(get_classifier_bp)
        self.app.register_blueprint(get_prediction_bp)
        self.app.register_blueprint(reset_password_bp)
        self.app.register_blueprint(avatar_bp)

        # 🌐 Página de login
        @self.app.route("/", methods=["GET", "POST"])
        def login_page():
            error = None
            if request.method == "POST":
                usuario = request.form.get("username")
                clave = request.form.get("password")
                if usuario == "Administrador" and clave == "JPc11082006":
                    return redirect("/usuarios")
                else:
                    error = "Credenciales incorrectas"
            return render_template("index.html", error=error)

        # 👤 Página de usuarios
        @self.app.route("/usuarios")
        def usuarios_page():
            return render_template("usuarios.html")

        # 📧 Endpoint para recuperación de contraseña
        @self.app.route("/users/forgot_password", methods=["POST"])
        def forgot_password():
            data = request.get_json()
            email = data.get("email")
            return self.reset_service.send_reset_email(email)

        # 🧹 Cierre automático de conexión al salir
        atexit.register(self.close_connections)

    def close_connections(self):
        if self.db_connection:
            closed, msg = self.db_connection.close()
            print(f"🔌 {msg}")

    def run(self):
        if os.getenv('PA_ENV') is None:
            self.app.run(host='127.0.0.1', port=5001, debug=True)

    def add_cors_headers(self, response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        return response

