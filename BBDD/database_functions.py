import os
from pathlib import Path
from BBDD.database_connection import DatabaseConnection
from BBDD.validator_UI import Validator


class DatabaseFunctions:
    """
    Clase principal para manejar todas las operaciones de base de datos.
    Gestiona conexiones, consultas y transacciones con MySQL en PythonAnywhere.

    Atributos:
        db_connection (DatabaseConnection): Objeto para manejar la conexión a la DB
        db_connected (bool): Estado de la conexión actual
        BASE_DIR (Path): Ruta base del proyecto
        SECURE_DIR (Path): Directorio para almacenar credenciales cifradas
        credentials_path (Path): Ruta del archivo de credenciales cifradas
        log_path (Path): Ruta del archivo de log
        logger (Logger): Instancia para registrar eventos
    """

    def __init__(self, logger):
        """
        Inicializa la instancia con configuración de rutas y logger.

        Args:
            logger (Logger): Instancia configurada del logger
        """
        self.db_connection = None
        self.db_connected = False
        self.logger = logger

        # Configuración portable de rutas usando pathlib
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.SECURE_DIR = self.BASE_DIR / 'secure'
        self.SECURE_DIR.mkdir(exist_ok=True, mode=0o700)  # Permisos restringidos
        self.credentials_path = self.SECURE_DIR / 'db_credentials.enc'
        self.log_path = self.BASE_DIR / 'logs' / 'database.log'

    def connect_to_database(self, host, database, user, password, port=3306):
        """
        Establece conexión con la base de datos MySQL usando credenciales proporcionadas.

        Args:
            host (str): Dirección del servidor MySQL
            database (str): Nombre de la base de datos
            user (str): Usuario para autenticación
            password (str): Contraseña del usuario
            port (int, optional): Puerto MySQL. Por defecto 3306.

        Returns:
            tuple: (success: bool, message: str) Resultado de la operación
        """
        try:
            # Ajuste automático para nombres de DB en PythonAnywhere
            if 'pythonanywhere' in host and not database.startswith(user + '$'):
                database = f"{user}${database}"

            # Crear nueva conexión
            self.db_connection = DatabaseConnection(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port
            )

            # Intentar conectar
            success, message = self.db_connection.connect()
            if success:
                self.db_connected = True
                self.db_connection.save_credentials()  # Guardar credenciales cifradas
                self.logger.log(f"Conexión exitosa a MySQL: {database}")
                return True, message
            return False, message

        except Exception as e:
            error_msg = f"Error conectando a MySQL: {str(e)}"
            self.logger.log(error_msg)
            return False, error_msg

    def load_and_connect(self):
        """
        Carga credenciales cifradas del archivo e intenta conectarse automáticamente.

        Returns:
            tuple: (success: bool, message: str) Resultado de la operación
        """
        try:
            if self.credentials_path.exists():
                # Cargar credenciales desde archivo cifrado
                self.db_connection = DatabaseConnection.load_credentials()
                success, message = self.db_connection.connect()

                if success:
                    self.db_connected = True
                    self.logger.log("Conexión exitosa desde credenciales guardadas")
                    return True, message
                return False, message
            return False, "No se encontraron credenciales guardadas"

        except Exception as e:
            error_msg = f"Error cargando credenciales: {str(e)}"
            self.logger.log(error_msg)
            return False, error_msg

    def disconnect_database(self):
        """
        Cierra la conexión activa con la base de datos de forma segura.

        Returns:
            tuple: (success: bool, message: str) Resultado de la operación
        """
        if self.db_connected and self.db_connection:
            success, message = self.db_connection.close()
            self.db_connected = not success  # Actualizar estado
            self.logger.log(message)
            return success, message
        return False, "No había conexión activa"

    def delete_config_file(self):
        """
        Elimina el archivo con credenciales cifradas almacenadas.

        Returns:
            tuple: (success: bool, message: str) Resultado de la operación
        """
        try:
            if self.credentials_path.exists():
                self.credentials_path.unlink()  # Eliminar archivo
                msg = "Credenciales eliminadas correctamente"
                self.logger.log(msg)
                return True, msg
            return False, "No existían credenciales guardadas"

        except Exception as e:
            error_msg = f"Error eliminando credenciales: {str(e)}"
            self.logger.log(error_msg)
            return False, error_msg

    # ========== MÉTODOS PARA MANEJO DE USUARIOS ==========

    def fetch_users_from_db(self):
        """
        Obtiene lista completa de usuarios registrados en la base de datos.

        Returns:
            list: Lista de diccionarios con datos de usuarios o lista vacía si hay error
        """
        if not self.db_connected:
            self.logger.log("Intento de obtener usuarios sin conexión")
            return []

        query = """
                SELECT id, name, nick_name, email, password, role, image
                FROM users
                ORDER BY id \
                """
        try:
            users = self.db_connection.execute_query(query)
            self.logger.log(f"Obtenidos {len(users)} usuarios")
            return users
        except Exception as e:
            self.logger.log(f"Error obteniendo usuarios: {str(e)}")
            return []

    def fetch_phone_data(self, user_id):
        """
        Obtiene los números de teléfono asociados a un usuario.

        Args:
            user_id (int): ID del usuario a consultar

        Returns:
            list: Lista de tuplas con (código_país, número) o lista vacía si hay error
        """
        if not self.db_connected:
            return []

        query = """
                SELECT country_code, phone
                FROM phones
                WHERE user_id = %s \
                """
        try:
            phones = self.db_connection.execute_query(query, (user_id,))
            return phones
        except Exception as e:
            self.logger.log(f"Error obteniendo teléfonos: {str(e)}")
            return []

    def fetch_address_data(self, user_id):
        """
        Obtiene la dirección asociada a un usuario.

        Args:
            user_id (int): ID del usuario a consultar

        Returns:
            tuple: Datos de dirección (ciudad, país, código_postal, dirección) o None si hay error
        """
        if not self.db_connected:
            return None

        query = """
                SELECT city, country, postal_code, address
                FROM addresses
                WHERE user_id = %s LIMIT 1 \
                """
        try:
            address = self.db_connection.execute_query(query, (user_id,))
            return address[0] if address else None
        except Exception as e:
            self.logger.log(f"Error obteniendo dirección: {str(e)}")
            return None

    def fetch_country_codes(self):
        """
        Obtiene todos los códigos de país disponibles en la base de datos.

        Returns:
            dict: Diccionario con {código_país: nombre_país} o diccionario vacío si hay error
        """
        if not self.db_connected:
            return {}

        query = "SELECT country_code, country_name FROM country_codes"
        try:
            codes = self.db_connection.execute_query(query)
            return {code: name for code, name in codes}
        except Exception as e:
            self.logger.log(f"Error obteniendo códigos: {str(e)}")
            return {}

    def get_next_id(self, table_name):
        """
        Calcula el próximo ID disponible para una tabla.

        Args:
            table_name (str): Nombre de la tabla a consultar

        Returns:
            int: Siguiente ID disponible o None si hay error
        """
        if not self.db_connected:
            return None

        query = f"SELECT COALESCE(MAX(id), 0) + 1 FROM {table_name}"
        try:
            result = self.db_connection.execute_query(query)
            return result[0][0] if result else 1
        except Exception as e:
            self.logger.log(f"Error obteniendo ID: {str(e)}")
            return None

    def save_user_data(self, user_id, entries):
        """
        Actualiza los datos de un usuario existente en la base de datos.

        Args:
            user_id (int): ID del usuario a actualizar
            entries (dict): Diccionario con los nuevos valores de los campos

        Returns:
            tuple: (success: bool, message: str) Resultado de la operación
        """
        if not self.db_connected:
            return False, "No hay conexión a la DB"

        # Validación de datos obligatorios
        if error := Validator.validate_password(entries["Contraseña"].get()):
            return False, error
        if error := Validator.validate_email(entries["Correo"].get()):
            return False, error

        try:
            # Usar transacción para asegurar integridad
            with self.db_connection.connection.cursor() as cursor:
                # 1. Actualizar datos principales del usuario
                cursor.execute("""
                               UPDATE users
                               SET name=%s,
                                   nick_name=%s,
                                   email=%s,
                                   password=%s,
                                   role=%s,
                                   image=%s
                               WHERE id = %s
                               """, (
                                   entries["Nombre"].get(),
                                   entries["Nombre de usuario"].get(),
                                   entries["Correo"].get(),
                                   entries["Contraseña"].get(),
                                   entries["Rol"].get(),
                                   entries["Imagen"].get(),
                                   user_id
                               ))

                # 2. Actualizar teléfonos (eliminar existentes y agregar nuevos)
                cursor.execute("DELETE FROM phones WHERE user_id=%s", (user_id,))
                for i in range(1, 3):  # Para teléfono 1 y 2
                    if phone := entries[f"Teléfono {i}"].get():
                        cursor.execute("""
                                       INSERT INTO phones (user_id, country_code, phone)
                                       VALUES (%s, %s, %s)
                                       """, (
                                           user_id,
                                           entries[f"Código de País {i}"].get(),
                                           phone
                                       ))

                # 3. Actualizar dirección (eliminar existente y agregar nueva)
                cursor.execute("DELETE FROM addresses WHERE user_id=%s", (user_id,))
                cursor.execute("""
                               INSERT INTO addresses
                                   (user_id, city, country, postal_code, address)
                               VALUES (%s, %s, %s, %s, %s)
                               """, (
                                   user_id,
                                   entries["Ciudad"].get(),
                                   entries["País"].get(),
                                   entries["Código postal"].get(),
                                   entries["Dirección"].get()
                               ))

                self.db_connection.connection.commit()
                self.logger.log(f"Usuario {user_id} actualizado")
                return True, "Usuario actualizado correctamente"

        except Exception as e:
            self.db_connection.connection.rollback()
            error_msg = f"Error actualizando usuario: {str(e)}"
            self.logger.log(error_msg)
            return False, error_msg

    def create_user(self, entries):
        """
        Crea un nuevo usuario en la base de datos con los datos proporcionados.

        Args:
            entries (dict): Diccionario con los valores de los campos del nuevo usuario

        Returns:
            tuple: (success: bool, message: str) Resultado de la operación
        """
        if not self.db_connected:
            return False, "No hay conexión a la DB"

        # Validación de datos (igual que en save_user_data)
        if error := Validator.validate_password(entries["Contraseña"].get()):
            return False, error
        if error := Validator.validate_email(entries["Correo"].get()):
            return False, error

        try:
            # Obtener próximo ID disponible
            user_id = self.get_next_id("users")
            if not user_id:
                return False, "Error obteniendo ID de usuario"

            # Usar transacción para asegurar integridad
            with self.db_connection.connection.cursor() as cursor:
                # 1. Insertar usuario principal
                cursor.execute("""
                               INSERT INTO users
                                   (id, name, nick_name, email, password, role, image)
                               VALUES (%s, %s, %s, %s, %s, %s, %s)
                               """, (
                                   user_id,
                                   entries["Nombre"].get(),
                                   entries["Nombre de usuario"].get(),
                                   entries["Correo"].get(),
                                   entries["Contraseña"].get(),
                                   entries["Rol"].get(),
                                   entries["Imagen"].get()
                               ))

                # 2. Insertar teléfonos (si fueron proporcionados)
                for i in range(1, 3):
                    if phone := entries[f"Teléfono {i}"].get():
                        cursor.execute("""
                                       INSERT INTO phones (user_id, country_code, phone)
                                       VALUES (%s, %s, %s)
                                       """, (
                                           user_id,
                                           entries[f"Código de País {i}"].get(),
                                           phone
                                       ))

                # 3. Insertar dirección
                cursor.execute("""
                               INSERT INTO addresses
                                   (user_id, city, country, postal_code, address)
                               VALUES (%s, %s, %s, %s, %s)
                               """, (
                                   user_id,
                                   entries["Ciudad"].get(),
                                   entries["País"].get(),
                                   entries["Código postal"].get(),
                                   entries["Dirección"].get()
                               ))

                self.db_connection.connection.commit()
                self.logger.log(f"Nuevo usuario {user_id} creado")
                return True, "Usuario creado correctamente"

        except Exception as e:
            self.db_connection.connection.rollback()
            error_msg = f"Error creando usuario: {str(e)}"
            self.logger.log(error_msg)
            return False, error_msg

    def delete_user(self, user_id):
        """
        Elimina un usuario y todos sus datos relacionados de la base de datos.

        Args:
            user_id (int): ID del usuario a eliminar

        Returns:
            tuple: (success: bool, message: str) Resultado de la operación
        """
        if not self.db_connected:
            return False, "No hay conexión a la DB"

        try:
            # Usar transacción para asegurar integridad
            with self.db_connection.connection.cursor() as cursor:
                # 1. Eliminar datos relacionados en otras tablas
                for table in ['phones', 'addresses', 'connections']:
                    cursor.execute(f"DELETE FROM {table} WHERE user_id=%s", (user_id,))

                # 2. Eliminar usuario principal
                cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))

                self.db_connection.connection.commit()
                self.logger.log(f"Usuario {user_id} eliminado")
                return True, "Usuario eliminado correctamente"

        except Exception as e:
            self.db_connection.connection.rollback()
            error_msg = f"Error eliminando usuario: {str(e)}"
            self.logger.log(error_msg)
            return False, error_msg