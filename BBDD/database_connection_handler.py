import os
import threading
from tkinter import messagebox
from BBDD.database_functions import DatabaseFunctions

class DatabaseConnectionHandler:
    def __init__(self, logger):
        # Inicializa el manejador de conexión a la base de datos con un logger
        self.functions = DatabaseFunctions(logger)
        self.logger = logger

    def check_and_connect(self, ui):
       # Verifica si existen credenciales guardadas y trata de conectar
        if os.path.exists(self.functions.credentials_path):
            success, message = self.functions.load_and_connect()
            if success:
                # Actualiza la interfaz de usuario si la conexión es exitosa
                ui.update_ui_on_connect(message)
            else:
                # Pide al usuario que reingrese las credenciales si la conexión falla
                ui.root.after(0, lambda: self.ask_retry_credentials(ui, message))
        else:
            # Registra que no se encontraron credenciales y solicita al usuario que las ingrese
            self.logger.log("No se han encontrado credenciales para conectarse a la base de datos.")
            ui.get_credentials_and_connect()

    def connect_and_log(self, host, database, user, password, ui):
        # Intenta conectar a la base de datos con las credenciales proporcionadas
        success, message = self.functions.connect_to_database(host, database, user, password)
        if success:
            # Actualiza la interfaz de usuario si la conexión es exitosa
            ui.update_ui_on_connect(message)
        else:
            # Pide al usuario que reingrese las credenciales si la conexión falla y registra el error
            ui.root.after(0, lambda: self.ask_retry_credentials(ui, message))
            self.logger.log(f"Error de conexión: {message}")

    def ask_retry_credentials(self, ui, message):
        # Pregunta al usuario si quiere reingresar las credenciales en caso de error
        retry = messagebox.askyesno("Error", f"{message}\n"
                                             f"¿Quieres volver a introducir las credenciales?")
        if retry:
            # Limpia las entradas de credenciales en la interfaz de usuario
            ui.clear_entries()
        else:
            # Cierra el programa si el usuario no quiere reingresar las credenciales
            ui.exit_program()

    def disconnect_database(self, ui):
        # Intenta desconectar la base de datos
        success, message = self.functions.disconnect_database()
        if success:
            # Actualiza la interfaz de usuario y registra la desconexión si es exitosa
            ui.update_status_label()
            ui.create_log_and_menu()
            self.logger.log("Base de datos desconectada.")
            messagebox.showinfo("Desconectar", "Base de datos desconectada.")
        else:
            # Registra y muestra un error si la desconexión falla
            self.logger.log(f"Error al desconectar: {message}")
            messagebox.showerror("Error", f"No se pudo desconectar la base de datos: {message}")

    def delete_config_file(self, ui):
        # Intenta eliminar el archivo de configuración
        success, message = self.functions.delete_config_file()
        if success:
            # Registra la eliminación y cierra la aplicación si es exitosa
            self.logger.log(message)
            messagebox.showinfo("Borrar Fichero", f"{message}\n\nSe procede a cerrar la aplicación")
            ui.exit_program()
        else:
            # Registra y muestra una advertencia si la eliminación falla
            self.logger.log(message)
            messagebox.showwarning("Borrar Fichero", message)
