import pymysql

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
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
                connect_timeout=10,
                charset='utf8mb4'
            )
            return True
        except Exception as e:
            print(f"❌ Error al conectar a la base de datos: {e}")
            return False

    def is_connected(self):
        try:
            self.connection.ping(reconnect=True)
            return True
        except Exception as e:
            print(f"⚠️ Conexión perdida. Intentando reconectar... {e}")
            return self.connect()

    def close(self):
        if self.connection:
            try:
                self.connection.close()
                return True, "Conexión cerrada correctamente."
            except Exception as e:
                return False, f"Error al cerrar la conexión: {e}"
        return False, "No hay conexión activa."

    def execute_query(self, query, params=None):
        if not self.is_connected():
            print("❌ No se pudo ejecutar la consulta porque no hay conexión.")
            return []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error al ejecutar consulta: {e}")
            return []

    def ensure_connection(self):
        if not self.connection or not self.is_connected():
            return self.connect()
        return True
