import tkinter as tk
from tkinter import messagebox, scrolledtext, Menu
from tkinter import ttk
import threading
import os

from BBDD.database_connection import DatabaseConnection
from Logger.logger import Logger
from BBDD.database_connection_handler import DatabaseConnectionHandler
from BBDD.user_management_UI import UserManagementUI


class DatabaseUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Conexión a Base de Datos")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        self.root.iconbitmap("Images/Logo.ico")

        # Evita conexión automática con datos vacíos
        self.db_connection = None

        # Ruta segura en Linux
        home = os.path.expanduser("~")
        log_path = os.path.join(home, 'JPC', 'log.txt')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        # Inicializa el logger
        self.logger = Logger(log_path)
        self.connection_handler = DatabaseConnectionHandler(self.logger)
        self.user_management_ui = UserManagementUI(root, self.connection_handler.functions)

        style = ttk.Style()
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 12))
        style.configure("TEntry", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 12), padding=6)

        self.log_text = None
        self.create_connection_widgets()
        self.connection_handler.check_and_connect(self)

    def create_connection_widgets(self):
        self.host_label = ttk.Label(self.root, text="Host:")
        self.host_label.pack(padx=10, pady=5, anchor='w')
        self.host_entry = ttk.Entry(self.root, width=70)
        self.host_entry.pack(padx=10, pady=5, anchor='w')

        self.database_label = ttk.Label(self.root, text="Base de Datos:")
        self.database_label.pack(padx=10, pady=5, anchor='w')
        self.database_entry = ttk.Entry(self.root, width=70)
        self.database_entry.pack(padx=10, pady=5, anchor='w')

        self.user_label = ttk.Label(self.root, text="Usuario:")
        self.user_label.pack(padx=10, pady=5, anchor='w')
        self.user_entry = ttk.Entry(self.root, width=70)
        self.user_entry.pack(padx=10, pady=5, anchor='w')

        self.password_label = ttk.Label(self.root, text="Contraseña:")
        self.password_label.pack(padx=10, pady=5, anchor='w')
        self.password_entry = ttk.Entry(self.root, show="*", width=70)
        self.password_entry.pack(padx=10, pady=5, anchor='w')

        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        self.connect_button = ttk.Button(button_frame, text="Conectar", command=self.get_credentials_and_connect)
        self.connect_button.pack(side=tk.LEFT, padx=10)

        self.exit_button = ttk.Button(button_frame, text="Salir", command=self.exit_program)
        self.exit_button.pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(
            self.root, text="BBDD desconectada", font=("Arial", 15, "bold"), fg="red", bg="#f0f0f0"
        )
        self.status_label.pack(side=tk.BOTTOM, anchor='e', padx=10, pady=(0, 10))

    def create_log_and_menu(self):
        if not self.log_text:
            self.log_text = scrolledtext.ScrolledText(self.root, width=60, height=10, font=("Arial", 10))
            self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.logger.log_widget = self.log_text
        else:
            self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.menu_bar = Menu(self.root)
        self.options_menu = Menu(self.menu_bar, tearoff=0)
        self.users_menu = Menu(self.menu_bar, tearoff=0)

        if self.connection_handler.functions.db_connected:
            self.options_menu.add_command(label="Desconectar Base de Datos",
                                          command=lambda: self.connection_handler.disconnect_database(self))
        else:
            self.options_menu.add_command(label="Conectar Base de Datos", command=self.check_and_connect)

        self.options_menu.add_command(label="Borrar Fichero de Configuración",
                                      command=lambda: self.connection_handler.delete_config_file(self))
        self.options_menu.add_separator()
        self.options_menu.add_command(label="Salir", command=self.exit_program)

        self.users_menu.add_command(label="Gestión de usuarios", command=self.user_management_ui.show_user_management)
        self.users_menu.add_command(label="Crear usuario", command=self.user_management_ui.show_user_form)

        self.menu_bar.add_cascade(label="Opciones", menu=self.options_menu)
        self.menu_bar.add_cascade(label="Usuarios", menu=self.users_menu)
        self.root.config(menu=self.menu_bar)

    def check_and_connect(self):
        if hasattr(self, 'user_management_window') and self.user_management_window.winfo_exists():
            self.user_management_window.lift()
            return
        self.connection_handler.check_and_connect(self)

    def update_ui_on_connect(self, message):
        self.root.title(f"Conexión a Base de Datos {self.connection_handler.functions.db_connection.database} correcta")
        self.root.state('zoomed')
        for widget in self.root.winfo_children():
            if widget != self.log_text:
                widget.pack_forget()
        self.create_log_and_menu()
        self.update_status_label()
        self.status_label.pack(side=tk.BOTTOM, anchor='e', padx=10, pady=(0, 10))
        self.logger.log(f"Conexión exitosa: {message}")

    def update_status_label(self):
        if self.connection_handler.functions.db_connected:
            self.status_label.config(text="BBDD conectada", fg="green")
        else:
            self.status_label.config(text="BBDD desconectada", fg="red")

    def get_credentials_and_connect(self):
        host = self.host_entry.get()
        database = self.database_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()
        self.logger.log("Introducimos nuevas credenciales host:" + host + " database:" + database + " user:" + user)
        threading.Thread(target=self.connection_handler.connect_and_log, args=(host, database, user, password, self)).start()

    def clear_entries(self):
        self.host_entry.delete(0, tk.END)
        self.database_entry.delete(0, tk.END)
        self.user_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def exit_program(self):
        self.logger.log("Aplicación cerrada.")
        self.root.quit()
        os._exit(0)

    def get_log_path(self):
        home = os.path.expanduser("~")
        return os.path.join(home, 'JPC', 'log.txt')
