import os
from datetime import datetime

class Logger:
    def __init__(self, log_path, db_connection=None, log_widget=None):
        self.log_path = log_path
        self.db_connection = db_connection
        self.log_widget = log_widget  # Para uso opcional en GUI (tkinter)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {level}: {message}\n"

        # Escribir en archivo
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(full_message)

        # Mostrar en GUI si aplica
        if self.log_widget:
            self.log_widget.insert('end', full_message)
            self.log_widget.see('end')

        # Escribir en base de datos si hay conexión
        if self.db_connection:
            try:
                with self.db_connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO logs (timestamp, message) VALUES (%s, %s)",
                        (timestamp, message)
                    )
                self.db_connection.commit()
            except Exception as e:
                with open(self.log_path, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] ERROR: No se pudo guardar en BD: {e}\n")

    def log_info(self, message):
        self.log(message, level="INFO")

    def log_error(self, message):
        self.log(message, level="ERROR")
