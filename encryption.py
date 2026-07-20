import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derives a 256-bit AES key from a user password and salt using PBKDF2 with SHA-256.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode('utf-8'))

def encrypt_data(data: bytes, password: str) -> bytes:
    """
    Encrypts bytes using AES-256-CBC.
    Returns: salt (16 bytes) + iv (16 bytes) + ciphertext.
    """
    salt = os.urandom(16)
    iv = os.urandom(16)
    key = derive_key(password, salt)
    
    # Add PKCS7 padding (128-bit block size for AES)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    return salt + iv + ciphertext

def decrypt_data(encrypted_data: bytes, password: str) -> bytes:
    """
    Decrypts bytes using AES-256-CBC.
    Extracts the salt and IV from the prepended header.
    Raises: ValueError if the password is incorrect or data is corrupted.
    """
    if len(encrypted_data) < 32:
        raise ValueError("Invalid or corrupted encrypted file format.")
        
    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]
    
    key = derive_key(password, salt)
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    try:
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    except Exception as e:
        raise ValueError("Decryption failed. Invalid password or corrupted payload.")
        
    unpadder = padding.PKCS7(128).unpadder()
    try:
        data = unpadder.update(padded_data) + unpadder.finalize()
    except Exception as e:
        raise ValueError("Decryption failed. Invalid password or corrupted payload.")
        
    return data
