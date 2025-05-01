import tkinter as tk
from tkinter import messagebox, scrolledtext, Menu
from tkinter import ttk
import threading
import os
import sys
from pathlib import Path

from BBDD.database_connection import DatabaseConnection
from Logger.logger import Logger
from BBDD.database_connection_handler import DatabaseConnectionHandler
from BBDD.user_management_UI import UserManagementUI


class DatabaseUI:
    """
    Clase principal para la interfaz gráfica de conexión a base de datos.
    Maneja la UI para conexión a MySQL y gestión de usuarios.

    Atributos:
        root (tk.Tk): Ventana principal de la aplicación
        db_connection (DatabaseConnection): Objeto para manejar conexiones a DB
        logger (Logger): Instancia para registro de eventos
        connection_handler (DatabaseConnectionHandler): Manejador de conexiones
        user_management_ui (UserManagementUI): Interfaz para gestión de usuarios
        log_text (scrolledtext.ScrolledText): Widget para mostrar logs
    """

    def __init__(self, root):
        """
        Inicializa la interfaz gráfica y configura conexión inicial.

        Args:
            root (tk.Tk): Ventana principal de la aplicación
        """
        self.root = root
        self._setup_main_window()
        self._setup_database_connection()
        self._setup_ui_components()

    def _setup_main_window(self):
        """Configura los parámetros básicos de la ventana principal"""
        self.root.title("Conexión a Base de Datos")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")

        # Configuración del icono (solo si no está en PythonAnywhere)
        if not self._is_pythonanywhere():
            try:
                icon_path = Path("Images") / "Logo.ico"
                if icon_path.exists():
                    self.root.iconbitmap(str(icon_path))
            except Exception as e:
                print(f"No se pudo cargar el icono: {e}")

    def _setup_database_connection(self):
        """Configura la conexión inicial a la base de datos"""
        # Conexión con valores por defecto (se pueden sobrescribir)
        self.db_connection = DatabaseConnection(
            host="jpastorcasquero.mysql.pythonanywhere-services.com",
            database="jpastorcasquero$prevision_demanda",
            user="jpastorcasquero",
            password="JPc11082006"
        )
        self.db_connection.connect()

        # Configuración de componentes auxiliares
        self.logger = self.db_connection.logger
        self.connection_handler = DatabaseConnectionHandler(self.logger)
        self.user_management_ui = UserManagementUI(
            self.root,
            self.connection_handler.functions
        )

    def _setup_ui_components(self):
        """Configura los componentes visuales de la interfaz"""
        self._configure_styles()
        self.log_text = None
        self.create_connection_widgets()
        self.connection_handler.check_and_connect(self)

    def _configure_styles(self):
        """Define los estilos visuales para los widgets"""
        style = ttk.Style()
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 12))
        style.configure("TEntry", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 12), padding=6)

    def _is_pythonanywhere(self):
        """Detecta si la aplicación se ejecuta en PythonAnywhere"""
        return 'pythonanywhere' in sys.executable.lower()

    def create_connection_widgets(self):
        """
        Crea los widgets para ingreso de credenciales de conexión.
        Incluye campos para host, base de datos, usuario y contraseña.
        """
        # Campo para host
        self.host_label = ttk.Label(self.root, text="Host:")
        self.host_label.pack(padx=10, pady=5, anchor='w')
        self.host_entry = ttk.Entry(self.root, width=70)
        self.host_entry.pack(padx=10, pady=5, anchor='w')
        self.host_entry.insert(0, self.db_connection.host or "")

        # Campo para base de datos
        self.database_label = ttk.Label(self.root, text="Base de Datos:")
        self.database_label.pack(padx=10, pady=5, anchor='w')
        self.database_entry = ttk.Entry(self.root, width=70)
        self.database_entry.pack(padx=10, pady=5, anchor='w')
        self.database_entry.insert(0, self.db_connection.database or "")

        # Campo para usuario
        self.user_label = ttk.Label(self.root, text="Usuario:")
        self.user_label.pack(padx=10, pady=5, anchor='w')
        self.user_entry = ttk.Entry(self.root, width=70)
        self.user_entry.pack(padx=10, pady=5, anchor='w')
        self.user_entry.insert(0, self.db_connection.user or "")

        # Campo para contraseña
        self.password_label = ttk.Label(self.root, text="Contraseña:")
        self.password_label.pack(padx=10, pady=5, anchor='w')
        self.password_entry = ttk.Entry(self.root, show="*", width=70)
        self.password_entry.pack(padx=10, pady=5, anchor='w')
        self.password_entry.insert(0, self.db_connection.password or "")

        # Botones de acción
        self._create_action_buttons()

        # Etiqueta de estado
        self._create_status_label()

    def _create_action_buttons(self):
        """Crea los botones de conexión y salida"""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        self.connect_button = ttk.Button(
            button_frame,
            text="Conectar",
            command=self.get_credentials_and_connect
        )
        self.connect_button.pack(side=tk.LEFT, padx=10)

        self.exit_button = ttk.Button(
            button_frame,
            text="Salir",
            command=self.exit_program
        )
        self.exit_button.pack(side=tk.LEFT, padx=10)

    def _create_status_label(self):
        """Crea la etiqueta que muestra el estado de la conexión"""
        self.status_label = tk.Label(
            self.root,
            text="BBDD desconectada",
            font=("Arial", 15, "bold"),
            fg="red",
            bg="#f0f0f0"
        )
        self.status_label.pack(side=tk.BOTTOM, anchor='e', padx=10, pady=(0, 10))

    def create_log_and_menu(self):
        """
        Crea el área de registro (log) y la barra de menú superior.
        Solo se muestra después de una conexión exitosa.
        """
        self._create_log_widget()
        self._create_menu_bar()

    def _create_log_widget(self):
        """Crea el widget ScrolledText para mostrar los logs"""
        if not self.log_text:
            self.log_text = scrolledtext.ScrolledText(
                self.root,
                width=60,
                height=10,
                font=("Arial", 10)
            )
            self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.logger.log_widget = self.log_text
        else:
            self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_menu_bar(self):
        """Crea la barra de menú superior con opciones"""
        self.menu_bar = Menu(self.root)

        # Menú de Opciones
        self.options_menu = Menu(self.menu_bar, tearoff=0)
        self._populate_options_menu()
        self.menu_bar.add_cascade(label="Opciones", menu=self.options_menu)

        # Menú de Usuarios
        self.users_menu = Menu(self.menu_bar, tearoff=0)
        self._populate_users_menu()
        self.menu_bar.add_cascade(label="Usuarios", menu=self.users_menu)

        self.root.config(menu=self.menu_bar)

    def _populate_options_menu(self):
        """Llena el menú de opciones según el estado de conexión"""
        if self.connection_handler.functions.db_connected:
            self.options_menu.add_command(
                label="Desconectar Base de Datos",
                command=lambda: self.connection_handler.disconnect_database(self)
            )
        else:
            self.options_menu.add_command(
                label="Conectar Base de Datos",
                command=self.check_and_connect
            )

        self.options_menu.add_command(
            label="Borrar Fichero de Configuración",
            command=lambda: self.connection_handler.delete_config_file(self)
        )
        self.options_menu.add_separator()
        self.options_menu.add_command(label="Salir", command=self.exit_program)

    def _populate_users_menu(self):
        """Llena el menú de gestión de usuarios"""
        self.users_menu.add_command(
            label="Gestión de usuarios",
            command=self.user_management_ui.show_user_management
        )
        self.users_menu.add_command(
            label="Crear usuario",
            command=self.user_management_ui.show_user_form
        )

    def check_and_connect(self):
        """
        Verifica y establece conexión con la base de datos.
        Evita múltiples ventanas de gestión de usuarios.
        """
        if hasattr(self, 'user_management_window') and self.user_management_window.winfo_exists():
            self.user_management_window.lift()
            return
        self.connection_handler.check_and_connect(self)

    def update_ui_on_connect(self, message):
        """
        Actualiza la interfaz después de una conexión exitosa.

        Args:
            message (str): Mensaje descriptivo del resultado de la conexión
        """
        db_name = self.connection_handler.functions.db_connection.database
        self.root.title(f"Conexión a Base de Datos {db_name} correcta")
        self.root.state('zoomed')

        # Limpiar widgets excepto el log
        for widget in self.root.winfo_children():
            if widget != self.log_text:
                widget.pack_forget()

        self.create_log_and_menu()
        self.update_status_label()
        self.status_label.pack(side=tk.BOTTOM, anchor='e', padx=10, pady=(0, 10))
        self.logger.log(f"Conexión exitosa: {message}")

    def update_status_label(self):
        """Actualiza la etiqueta de estado según la conexión actual"""
        if self.connection_handler.functions.db_connected:
            self.status_label.config(text="BBDD conectada", fg="green")
        else:
            self.status_label.config(text="BBDD desconectada", fg="red")

    def get_credentials_and_connect(self):
        """
        Obtiene credenciales de los campos de entrada y establece conexión.
        Usa un hilo separado para no bloquear la interfaz.
        """
        host = self.host_entry.get()
        database = self.database_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()

        self.logger.log(
            f"Intento de conexión - Host: {host} | DB: {database} | User: {user}"
        )

        # Conexión en hilo separado
        threading.Thread(
            target=self.connection_handler.connect_and_log,
            args=(host, database, user, password, self)
        ).start()

    def clear_entries(self):
        """Limpia todos los campos de entrada de credenciales"""
        self.host_entry.delete(0, tk.END)
        self.database_entry.delete(0, tk.END)
        self.user_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def exit_program(self):
        """Cierra la aplicación de manera controlada"""
        self.logger.log("Aplicación cerrada correctamente")
        self.root.quit()
        os._exit(0)

    def get_log_path(self):
        """
        Obtiene la ruta para almacenar los archivos de log.
        Usa rutas diferentes según sea PythonAnywhere o entorno local.

        Returns:
            str: Ruta completa al archivo de log
        """
        base = Path.home() / 'logs' if self._is_pythonanywhere() else Path(__file__).parent.parent / 'logs'
        base.mkdir(exist_ok=True)
        return str(base / 'application.log')