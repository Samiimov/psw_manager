import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.fernet import Fernet

BS = 16

class CryptoFunctionalities:
    def __init__(self) -> None:
        self.logging_cipher : Fernet = None

    def encrypt(self, key: bytes, data: str) -> bytes:
        iv = os.urandom(16)
        # Add padding
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data.encode()) + padder.finalize()
        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(iv + ct)
    
    def decrypt(self, key: bytes, ct: bytes) -> bytes:
        enc = base64.b64decode(ct)
        # Separate IV and data
        iv = enc[:16]
        encdata = enc[16:]
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        pt = decryptor.update(encdata) + decryptor.finalize()
        # Unpad
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        output = unpadder.update(pt) + unpadder.finalize()

        return output
    
    def derive_key(self, psw: str, salt: bytes):
        """
        Use PBKDF2 to produce a key using the given password and salt
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        return kdf.derive(psw.encode())
        
    def verify(self, psw: str, key: bytes, salt: bytes):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        
        try:
            kdf.verify(psw.encode(), key)
            return True
        except Exception:
            return False
        
    def hash_str(self, to_hash: str):
        """
        Hash string with SHA256
        """
        digest = hashes.Hash(hashes.SHA256())
        digest.update(to_hash.encode())
        digested = digest.finalize()
        return digested
    
    def hash_bytes(self, to_hash: bytes):
        """
        Hash bytes with SHA256
        """
        digest = hashes.Hash(hashes.SHA256())
        digest.update(to_hash)
        digested = digest.finalize()
        return digested
    
    def encrypted_formatter(self, record):
        encrypted = self.logging_cipher.encrypt(record["message"].encode("utf8"))
        record["extra"]["encrypted"] = base64.b64encode(encrypted).decode()
        return "{extra[encrypted]}\n{exception}"

    def set_logging_cipher(self, key: str):
        key_bytes = base64.b64encode(key.encode())
        self.logging_cipher = Fernet(key_bytes)

crypto = CryptoFunctionalities()