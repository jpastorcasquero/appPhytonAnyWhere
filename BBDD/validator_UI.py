<<<<<<< HEAD
# BBDD/validator_UI.py
import re

class Validator:
    @staticmethod
    def validate_email(email):
        """Valida el formato del correo electrónico."""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "Correo electrónico no válido."
        return ""

    @staticmethod
    def validate_password(password):
        """Valida la longitud mínima de la contraseña."""
        if len(password) < 6:
            return "La contraseña debe tener al menos 6 caracteres."
=======
import re

class Validator:
    # Establecemos poder llamar al metodo sin instanciar la clase
    @staticmethod
    def validate_password(password):
        # Valida que la contraseña cumpla con los requisitos de seguridad
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
        # Valida que el correo electrónico tenga un formato válido
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "El correo electrónico no es válido."
>>>>>>> ec128bb (Primer commit del proyecto)
        return ""

    @staticmethod
    def validate_phone(phone):
<<<<<<< HEAD
        """Valida que el número de teléfono contenga entre 7 y 15 dígitos."""
        if not re.match(r"^[0-9]{7,15}$", phone):
            return "Número de teléfono no válido."
=======
        # Valida que el número de teléfono tenga entre 7 y 15 dígitos y opcionalmente
        # comience con un signo +
        if not re.match(r"^\+?[0-9]{7,15}$", phone):
            return "El número de teléfono no es válido. Debe tener entre 7 y 15 dígitos."
>>>>>>> ec128bb (Primer commit del proyecto)
        return ""
