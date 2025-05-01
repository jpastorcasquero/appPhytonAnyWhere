import re


class Validator:
    """
    Clase utilitaria para validación de datos de entrada.
    Contiene métodos estáticos para validar formatos comunes.

    Métodos:
        validate_password: Valida fortaleza de contraseñas
        validate_email: Valida formato de emails
        validate_phone: Valida números telefónicos
    """

    @staticmethod
    def validate_password(password):
        """
        Valida que una contraseña cumpla con requisitos de seguridad básicos.

        Requisitos:
        - Mínimo 8 caracteres
        - Al menos 1 mayúscula
        - Al menos 1 minúscula
        - Al menos 1 número
        - Al menos 1 carácter especial

        Args:
            password (str): Contraseña a validar

        Returns:
            str: Mensaje de error si no es válida, string vacío si es válida
        """
        if len(password) < 8:
            return "La contraseña debe tener al menos 8 caracteres."
        if not re.search(r"[A-Z]", password):
            return "La contraseña debe incluir al menos una letra mayúscula."
        if not re.search(r"[a-z]", password):
            return "La contraseña debe incluir al menos una letra minúscula."
        if not re.search(r"[0-9]", password):
            return "La contraseña debe incluir al menos un número."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return "La contraseña debe incluir al menos un carácter especial."
        return ""

    @staticmethod
    def validate_email(email):
        """
        Valida que un email tenga formato válido usando expresión regular básica.

        Formato requerido:
        - texto@texto.texto
        - No permite múltiples @
        - Requiere punto después del @

        Args:
            email (str): Email a validar

        Returns:
            str: Mensaje de error si no es válido, string vacío si es válido
        """
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "El correo electrónico no es válido."
        return ""

    @staticmethod
    def validate_phone(phone):
        """
        Valida formato de número telefónico internacional.

        Formatos aceptados:
        - +56912345678
        - 56912345678
        - 1234567 (mínimo 7 dígitos)

        Args:
            phone (str): Número telefónico a validar

        Returns:
            str: Mensaje de error si no es válido, string vacío si es válido
        """
        if not re.match(r"^\+?[0-9]{7,15}$", phone):
            return "El número de teléfono no es válido. Debe tener entre 7 y 15 dígitos."
        return ""