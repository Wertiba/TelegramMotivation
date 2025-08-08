import os
from src.services.singleton import singleton
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode
from dotenv import find_dotenv, load_dotenv


@singleton
class Encryption:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.password = os.getenv("ENCRYPTION_KEY").encode('utf-8')
        # with open(r"", )

    def generate_key(self, password: bytes, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return urlsafe_b64encode(kdf.derive(password))

    def encrypt_message(self, message: bytes) -> tuple:
        # with open("")
        salt = os.urandom(16)  # генерируем соль
        key = self.generate_key(bytes(self.password), salt)
        cipher_suite = Fernet(key)
        encrypted_msg = cipher_suite.encrypt(message)
        return salt, encrypted_msg  # сохраняем вместе с солью

    def decrypt_message(self, salt: bytes, encrypted_msg: bytes) -> bytes:
        key = self.generate_key(bytes(self.password), salt)
        cipher_suite = Fernet(key)
        return cipher_suite.decrypt(encrypted_msg)

# Пример
# enc = Encryption()
# salt, encmsg = enc.encrypt_message(b"Secret message")
# print(enc.decrypt_message(salt, encmsg))
