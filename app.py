from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from BBDD.database_functions import DatabaseFunctions
from Logger.logger import Logger
import os
import smtplib
from email.mime.text import MIMEText

# Inicialización de Flask
app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'
CORS(app)

# Rutas del sistema
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
SECURE_DIR = os.path.join(BASE_DIR, 'secure')
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SECURE_DIR, exist_ok=True)

# Logger y conexión a BD
log_path = os.path.join(LOG_DIR, 'webapp.log')
logger = Logger(log_path)
db_handler = DatabaseFunctions(logger)
db_handler.load_and_connect()

@app.route('/')
def index():
    return redirect(url_for('usuarios'))

@app.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')

@app.route('/usuario/<int:user_id>', methods=['GET'])
def obtener_usuario(user_id):
    usuario = db_handler.fetch_users_from_db()
    datos = next((u for u in usuario if int(u['id']) == user_id), None)
    return jsonify(datos)

@app.route('/usuario/crear', methods=['POST'])
def crear_usuario():
    datos = request.form.to_dict()
    user_data = {
        "Nombre": datos.get("nombre"),
        "Nombre de usuario": datos.get("nick_name"),
        "Correo": datos.get("email"),
        "Contraseña": datos.get("password"),
        "Rol": datos.get("role"),
        "Imagen": datos.get("image"),
        "Código de País 1": datos.get("country_code1"),
        "Teléfono 1": datos.get("phone1"),
        "Código de País 2": datos.get("country_code2"),
        "Teléfono 2": datos.get("phone2"),
        "Ciudad": datos.get("city"),
        "País": datos.get("country"),
        "Código postal": datos.get("postal_code"),
        "Dirección": datos.get("address")
    }
    success, message = db_handler.create_user(user_data)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('usuarios'))

@app.route('/usuario/editar/<int:user_id>', methods=['POST'])
def editar_usuario(user_id):
    datos = request.form.to_dict()
    user_data = {
        "Nombre": datos.get("nombre"),
        "Nombre de usuario": datos.get("nick_name"),
        "Correo": datos.get("email"),
        "Contraseña": datos.get("password"),
        "Rol": datos.get("role"),
        "Imagen": datos.get("image"),
        "Código de País 1": datos.get("country_code1"),
        "Teléfono 1": datos.get("phone1"),
        "Código de País 2": datos.get("country_code2"),
        "Teléfono 2": datos.get("phone2"),
        "Ciudad": datos.get("city"),
        "País": datos.get("country"),
        "Código postal": datos.get("postal_code"),
        "Dirección": datos.get("address")
    }
    success, message = db_handler.save_user_data(user_id, user_data)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('usuarios'))

@app.route('/usuario/eliminar/<int:user_id>', methods=['POST'])
def eliminar_usuario(user_id):
    success, message = db_handler.delete_user(user_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('usuarios'))

@app.route('/usuario/reset/<int:user_id>', methods=['GET'])
def restablecer_contraseña(user_id):
    usuarios = db_handler.fetch_users_from_db()
    user = next((u for u in usuarios if int(u['id']) == user_id), None)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    user_email = user['email']
    reset_link = f"https://{request.host}/reset_password/{user_id}"

    msg = MIMEText(f"Haz clic para restablecer tu contraseña: {reset_link}")
    msg['Subject'] = 'Restablecimiento de Contraseña'
    msg['From'] = 'pass.recovery.jpcinformatica@gmail.com'
    msg['To'] = user_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('pass.recovery.jpcinformatica@gmail.com', 'yxko jelw mgoo vumt')
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
        return jsonify({'message': 'Correo enviado correctamente'})
    except Exception as e:
        return jsonify({'error': f'Error al enviar el correo: {e}'}), 500


