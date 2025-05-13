from Crypto.Cipher import AES
import base64
import json

class Encryption:
    """
    Clase para manejar operaciones de cifrado y descifrado AES-256 en modo ECB.

    Esta clase proporciona métodos para cifrar y descifrar datos sensibles usando
    el algoritmo AES (Advanced Encryption Standard) con una clave de 256 bits.

    Atributos:
        secret_key (str): Clave secreta para cifrado/descifrado (será ajustada a 32 bytes)
    """

    def __init__(self, secret_key):
        """
        Inicializa la instancia de Encryption con una clave secreta.

        Args:
            secret_key (str): Clave secreta que se usará para cifrado/descifrado.
                             Será rellenada con ceros a la izquierda para asegurar
                             que tenga 32 bytes de longitud (AES-256).
        """
        self.secret_key = secret_key.zfill(32)

    def encrypt(self, data):
        """
        Cifra los datos proporcionados usando AES-256 en modo ECB.

        Args:
            data (str): Datos a cifrar en formato de cadena.

        Returns:
            str: Datos cifrados codificados en base64 como cadena.
        """
        cipher = AES.new(self.secret_key.encode('utf-8'), AES.MODE_ECB)
        padding_length = 16 - (len(data) % 16)
        padded_data = data + ' ' * padding_length
        encrypted_bytes = cipher.encrypt(padded_data.encode('utf-8'))
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    def decrypt(self, encrypted_data):
        """
        Descifra datos previamente cifrados con AES-256 en modo ECB.

        Args:
            encrypted_data (str): Datos cifrados en formato base64.

        Returns:
            str: Datos originales descifrados, sin el relleno añadido.
        """
        cipher = AES.new(self.secret_key.encode('utf-8'), AES.MODE_ECB)
        decrypted_bytes = cipher.decrypt(base64.b64decode(encrypted_data))
        return decrypted_bytes.decode('utf-8').strip()
