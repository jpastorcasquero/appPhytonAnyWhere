import os
import threading
from tkinter import messagebox
from pathlib import Path
from BBDD.database_functions import DatabaseFunctions


class DatabaseConnectionHandler:
    def __init__(self, logger):
        self.functions = DatabaseFunctions(logger)
        self.logger = logger
        # Configuración portable de rutas
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.SECURE_DIR = self.BASE_DIR / 'secure'
        self.SECURE_DIR.mkdir(exist_ok=True, mode=0o700)  # Permisos seguros

    def check_and_connect(self, ui):
        """Verifica conexión con credenciales existentes o solicita nuevas"""
        creds_file = self.SECURE_DIR / 'db_credentials.enc'

        if creds_file.exists():
            success, message = self.functions.load_and_connect()
            if success:
                ui.update_ui_on_connect(message)
            else:
                ui.root.after(0, lambda: self.ask_retry_credentials(ui, message))
        else:
            self.logger.log("No se encontraron credenciales guardadas")
            ui.get_credentials_and_connect()

    def connect_and_log(self, host, database, user, password, ui):
        """Intenta conectar y maneja el resultado en la UI"""
        # Ajuste para PythonAnywhere (añade el prefijo de usuario si es necesario)
        if 'pythonanywhere' in database and not database.startswith(self.functions.db_connection.user + '$'):
            database = f"{self.functions.db_connection.user}${database}"

        success, message = self.functions.connect_to_database(
            host=host,
            database=database,
            user=user,
            password=password,
            port=3306  # Puerto explícito para MySQL
        )

        if success:
            ui.update_ui_on_connect(message)
            # Guarda las credenciales cifradas
            self.functions.db_connection.save_credentials()
        else:
            ui.root.after(0, lambda: self.ask_retry_credentials(ui, message))
            self.logger.log(f"Error de conexión: {message}")

    def ask_retry_credentials(self, ui, message):
        """Maneja reintentos de conexión"""
        retry = messagebox.askyesno(
            "Error de Conexión",
            f"{message}\n¿Desea reintentar con otras credenciales?",
            parent=ui.root
        )
        ui.clear_entries() if retry else ui.exit_program()

    def disconnect_database(self, ui):
        """Desconecta limpiamente la base de datos"""
        success, message = self.functions.disconnect_database()
        if success:
            ui.update_status_label()
            ui.create_log_and_menu()
            self.logger.log("Desconexión exitosa de MySQL")
            messagebox.showinfo("Conexión", "Base de datos desconectada", parent=ui.root)
        else:
            self.logger.log(f"Error al desconectar: {message}")
            messagebox.showerror("Error", f"Fallo al desconectar:\n{message}", parent=ui.root)

    def delete_config_file(self, ui):
        """Elimina las credenciales guardadas"""
        creds_file = self.SECURE_DIR / 'db_credentials.enc'
        try:
            if creds_file.exists():
                creds_file.unlink()
                msg = "Credenciales eliminadas correctamente"
                self.logger.log(msg)
                messagebox.showinfo("Éxito", f"{msg}\nLa aplicación se cerrará", parent=ui.root)
                ui.exit_program()
            else:
                msg = "No existían credenciales guardadas"
                self.logger.log(msg)
                messagebox.showinfo("Información", msg, parent=ui.root)
        except Exception as e:
            msg = f"No se pudo eliminar el archivo: {e}"
            self.logger.log(msg)
            messagebox.showerror("Error", msg, parent=ui.root)