import os
import base64
import json
import pymysql
from Cifrado.encryption import Encryption

class DatabaseConnection:
    def __init__(self, host="", database="", user="", password=""):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor
            )
            return True
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            return False

    def close(self):
        if self.connection:
            try:
                self.connection.close()
                return True, "Conexión cerrada correctamente."
            except Exception as e:
                return False, f"Error al cerrar la conexión: {e}"
        return False, "No hay conexión activa."

    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Error al ejecutar consulta: {e}")
            return []

    def save_credentials(self):
        data = {
            "host": self.host,
            "database": self.database,
            "user": self.user,
            "password": self.password
        }

        enc = Encryption("JPc11082006")
        encrypted = enc.encrypt(json.dumps(data))

        home = os.path.expanduser("~")
        file_path = os.path.join(home, "JPC", "conexionBD.enc")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            f.write(encrypted)

    @staticmethod
    def load_credentials():
        home = os.path.expanduser("~")
        file_path = os.path.join(home, "JPC", "conexionBD.enc")
        with open(file_path, "r") as f:
            encrypted = f.read()

        enc = Encryption("JPc11082006")
        decrypted = enc.decrypt(encrypted)
        data = json.loads(decrypted)

        return DatabaseConnection(
            host=data["host"],
            database=data["database"],
            user=data["user"],
            password=data["password"]
        )
