import re

class Validator:
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
        return ""

    @staticmethod
    def validate_phone(phone):
        # Valida que el número de teléfono tenga entre 7 y 15 dígitos y opcionalmente comience con un signo +
        if not re.match(r"^\+?[0-9]{7,15}$", phone):
            return "El número de teléfono no es válido. Debe tener entre 7 y 15 dígitos."
        return ""
