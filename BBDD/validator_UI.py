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
        return ""

    @staticmethod
    def validate_phone(phone):
        """Valida que el número de teléfono contenga entre 7 y 15 dígitos."""
        if not re.match(r"^[0-9]{7,15}$", phone):
            return "Número de teléfono no válido."
        return ""
