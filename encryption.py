"""
encryption.py - Handles file encryption and decryption logic.

This module uses AES encryption (via Fernet) with a password-derived key.
The password is converted into a secure encryption key using SHA-256 hashing
combined with a salt, then base64-encoded for Fernet compatibility.

Beginner Notes:
- Fernet is a symmetric encryption method (same key encrypts and decrypts).
- We derive the key from the user's password so they don't need to remember
  a complex key — just their password.
- A salt is random data added to the password before hashing to prevent
  rainbow table attacks.
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken


# Salt length in bytes (16 bytes = 128 bits, considered secure)
SALT_LENGTH = 16


def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive a Fernet-compatible encryption key from a password and salt.

    How it works:
    1. Combine the password with a random salt
    2. Hash them together using SHA-256
    3. Encode the hash in base64 (Fernet requires a 32-byte base64-encoded key)

    Args:
        password: The user's password string
        salt: Random bytes used to make the key unique

    Returns:
        A 32-byte base64-encoded key suitable for Fernet encryption
    """
    # Combine password bytes with salt bytes, then hash with SHA-256
    key_material = hashlib.sha256(salt + password.encode('utf-8')).digest()

    # Fernet needs a URL-safe base64-encoded 32-byte key
    key = base64.urlsafe_b64encode(key_material)
    return key


def encrypt_file(input_path: str, output_path: str, password: str) -> bool:
    """
    Encrypt a file using a password.

    Process:
    1. Generate a random salt
    2. Derive an encryption key from the password + salt
    3. Read the original file
    4. Encrypt the file contents
    5. Save: salt + encrypted data (salt is prepended so we can use it for decryption)

    Args:
        input_path: Path to the original file to encrypt
        output_path: Path where the encrypted file will be saved
        password: The password to use for encryption

    Returns:
        True if encryption was successful, False otherwise
    """
    try:
        # Step 1: Generate a random salt (unique for each encryption)
        salt = os.urandom(SALT_LENGTH)

        # Step 2: Derive the encryption key from password + salt
        key = derive_key(password, salt)

        # Step 3: Create a Fernet cipher object with our key
        fernet = Fernet(key)

        # Step 4: Read the original file in binary mode
        with open(input_path, 'rb') as file:
            original_data = file.read()

        # Step 5: Encrypt the file data
        encrypted_data = fernet.encrypt(original_data)

        # Step 6: Write salt + encrypted data to the output file
        # We prepend the salt so we can extract it during decryption
        with open(output_path, 'wb') as file:
            file.write(salt + encrypted_data)

        return True

    except Exception as e:
        print(f"Encryption error: {e}")
        return False


def decrypt_file(input_path: str, output_path: str, password: str) -> bool:
    """
    Decrypt a file using a password.

    Process:
    1. Read the encrypted file
    2. Extract the salt (first 16 bytes)
    3. Derive the same key using password + extracted salt
    4. Decrypt the remaining data
    5. Save the decrypted file

    Args:
        input_path: Path to the encrypted file
        output_path: Path where the decrypted file will be saved
        password: The password used during encryption

    Returns:
        True if decryption was successful, False otherwise
    """
    try:
        # Step 1: Read the encrypted file
        with open(input_path, 'rb') as file:
            file_data = file.read()

        # Step 2: Extract the salt (first SALT_LENGTH bytes)
        salt = file_data[:SALT_LENGTH]

        # Step 3: Extract the actual encrypted data (everything after the salt)
        encrypted_data = file_data[SALT_LENGTH:]

        # Step 4: Derive the same key using the password and extracted salt
        key = derive_key(password, salt)

        # Step 5: Create a Fernet cipher with the derived key
        fernet = Fernet(key)

        # Step 6: Decrypt the data
        # This will raise InvalidToken if the password is wrong
        decrypted_data = fernet.decrypt(encrypted_data)

        # Step 7: Write the decrypted data to the output file
        with open(output_path, 'wb') as file:
            file.write(decrypted_data)

        return True

    except InvalidToken:
        # This error occurs when the wrong password is provided
        print("Decryption failed: Invalid password or corrupted file.")
        return False

    except Exception as e:
        print(f"Decryption error: {e}")
        return False
