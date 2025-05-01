import os  # Importa el módulo os para interactuar con el sistema operativo
from datetime import datetime  # Importa datetime para trabajar con fechas y horas

class Logger:
    def __init__(self, log_path, log_widget=None, db_connection=None):
        # Inicializa la clase Logger con la ruta del archivo de log, un widget opcional para mostrar logs y una conexión opcional a la base de datos
        self.log_path = log_path  # Ruta del archivo de log
        self.log_widget = log_widget  # Widget opcional para mostrar logs en la interfaz de usuario
        self.db_connection = db_connection  # Conexión opcional a la base de datos
        self.connection_logged = False  # Flag para indicar si la conexión ha sido registrada

    def log(self, message):
        # Metodo para registrar un mensaje en el log
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Añade la fecha y hora al mensaje
        log_message = f"{timestamp} - {message}\n"  # Formatea el mensaje de log con la fecha y hora

        # Escribe el mensaje en el archivo de log
        with open(self.log_path, 'a') as log_file:
            log_file.write(log_message)

        # Si se proporciona un widget de log, inserta el mensaje en el widget
        if self.log_widget:
            self.log_widget.insert('end', log_message)  # Inserta el mensaje en el widget de log
            self.log_widget.see('end')  # Desplaza el widget hasta el último mensaje

        # Inserta el log en la base de datos
        self.log_to_db(timestamp, message)

        return log_message  # Devuelve el mensaje de log

    def log_to_db(self, timestamp, message):
        # Metodo para insertar el log en la base de datos
        if self.db_connection:
            try:
                cursor = self.db_connection.cursor()  # Obtiene un cursor de la conexión a la base de datos
                insert_query = "INSERT INTO prevision_demanda_db.logs (timestamp, message) VALUES (%s, %s)"  # Consulta SQL para insertar el log
                cursor.execute(insert_query, (timestamp, message))  # Ejecuta la consulta SQL
                self.db_connection.commit()  # Realiza el commit de la transacción
                cursor.close()  # Cierra el cursor
            except Exception as e:
                print(f"Error al insertar el log en la base de datos: {e}")  # Imprime un mensaje de error si ocurre una excepción

    def log_connection_success(self):
        # Metodo para registrar el éxito de la conexión a la base de datos
        if not self.connection_logged:
            self.log("¡Conexión a la base de datos exitosa!")  # Registra el mensaje de éxito de la conexión
            self.connection_logged = True  # Actualiza el flag para indicar que la conexión ha sido registrada
