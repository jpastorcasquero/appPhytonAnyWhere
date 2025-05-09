# main.py

from Http.flask_app import FlaskApp
import os
from BBDD.database_connection import DatabaseConnection

def initialize_credentials_if_missing():
    cred_path = os.path.join(os.getenv("HOME", "/tmp"), 'JPC', 'conexionBD.enc')
    if not os.path.exists(cred_path):
        db = DatabaseConnection(
            host="jpastorcasquero.mysql.pythonanywhere-services.com",
            database="jpastorcasquero$prevision_demanda_db",
            user="jpastorcasquero",
            password="JPc11082006"
        )
        db.save_credentials()
        print("Credenciales guardadas correctamente.")
    else:
        print("Credenciales ya existen, no se sobrescriben.")

if __name__ == "__main__":
    initialize_credentials_if_missing()
    flask_app = FlaskApp()
    #flask_app.run()
