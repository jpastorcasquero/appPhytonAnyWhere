from flask import Flask, render_template, request, jsonify, redirect

from flask_cors import CORS
from flask_socketio import SocketIO
import os

from Logger.logger import Logger
from BBDD.database_connection import DatabaseConnection

from Http.Routes.get_prediction_handler import get_prediction_bp
from Http.Routes.get_classifier_handler import get_classifier_bp
from Http.Routes.reset_password_handler import reset_password_bp, ResetPasswordHandler  # ✅ CORREGIDO AQUÍ
from Http.Routes.users_handler import UsersHandler
from Http.Routes.addresses_handler import AddressesHandler
from Http.Routes.phones_handler import PhonesHandler
from Http.Routes.connections_handler import ConnectionsHandler
from Http.Routes.users_api import users_api
from Http.Routes.avatar_routes import avatar_bp
from Http.Routes.password_reset_service import PasswordResetService



class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__, static_folder="static")

        CORS(self.app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        os.makedirs('/home/jpastorcasquero/JPC', exist_ok=True)
        log_path = '/home/jpastorcasquero/JPC/log.txt'

        db_connection = DatabaseConnection(
            host="jpastorcasquero.mysql.pythonanywhere-services.com",
            database="jpastorcasquero$prevision_demanda_db",
            user="jpastorcasquero",
            password="JPc11082006"
        )
        success = db_connection.connect()
        self.db_connection = db_connection

        if not success:
            print("❌ Error al conectar con la base de datos en FlaskApp")

        self.logger = Logger(log_path, db_connection=self.db_connection.connection)

        # Handlers principales
        self.users_handler = UsersHandler(self.app, self.logger)
        self.addresses_handler = AddressesHandler(self.app, self.logger)
        self.phones_handler = PhonesHandler(self.app, self.logger)
        self.connections_handler = ConnectionsHandler(self.app, self.logger)
        self.reset_password_handler = ResetPasswordHandler(self.logger)  # ⚠️ YA REGISTRA SU BLUEPRINT
        self.app.register_blueprint(reset_password_bp)

        # Blueprints REST
        self.app.register_blueprint(users_api)
        self.app.register_blueprint(get_classifier_bp)
        self.app.register_blueprint(get_prediction_bp)
        self.app.register_blueprint(avatar_bp)

        # Ruta principal
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

        @self.app.route("/usuarios")
        def usuarios_page():
            return render_template("usuarios.html")

        # Endpoint para enviar email de recuperación
        reset_service = PasswordResetService(self.logger)

        @self.app.route("/users/forgot_password", methods=["POST"])
        def forgot_password():
            data = request.get_json()
            email = data.get("email")
            return reset_service.send_reset_email(email)

    def run(self):
        if os.getenv('PA_ENV') is None:
            self.app.run(host='127.0.0.1', port=5001, debug=True)
