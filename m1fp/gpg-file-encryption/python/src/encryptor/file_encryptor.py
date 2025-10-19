from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets
import os
import argparse
import sys
import getpass
import time


"""A class for encrypting and decrypting files using AES encryption in CBC mode.
This class handles file encryption and decryption using AES-256 with CBC mode and PKCS7 padding.
The encryption key is derived from a user-provided passphrase and email using PBKDF2-HMAC-SHA256.
Attributes:
    email (str): The email address used as salt for key derivation
    passphrase (str): The passphrase used to generate the encryption key
Methods:
    encrypt_file(input_file, output_file): Encrypts a file using AES-256-CBC
    decrypt_file(input_file, output_file): Decrypts a file encrypted with this class
    _derive_key(): Derives encryption key from passphrase and email using PBKDF2
    _pad_data(data): Applies PKCS7 padding to data
    _unpad_data(data): Removes PKCS7 padding from data
Example:
    encryptor = FileEncryptor("user@example.com", "mypassphrase")
    encryptor.encrypt_file("plaintext.txt", "encrypted.bin")
    encryptor.decrypt_file("encrypted.bin", "decrypted.txt")
Note:
    The email address is used as the salt for key derivation, ensuring consistent
    key generation across different implementations when using the same email/passphrase.
"""
class FileEncryptor:
    def __init__(self, email, passphrase):
        # Initialize the FileEncryptor with the user's email and passphrase
        self.email = email
        self.passphrase = passphrase

    """
    Derives an encryption key from the user's passphrase using PBKDF2 (Password-Based Key Derivation Function 2).
    The method uses the following parameters:
    - HMAC-SHA256 as the hash function
    - User's email as the salt value
    - 65536 iterations
    - 32 bytes (256 bits) key length
    Returns:
        bytes: A 32-byte derived key suitable for AES encryption
    Note:
        This is an internal method as indicated by the underscore prefix.
        The parameters are specifically chosen to match the Java implementation for compatibility.
    """
    def _derive_key(self):
        # Use email as salt (matching Java implementation)
        salt = self.email.encode('utf-8')
        
        # Create key using PBKDF2 with HMAC-SHA256 (matching Java parameters)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=65536,
            backend=default_backend()
        )
        key = kdf.derive(self.passphrase.encode('utf-8'))
        return key

    """
    Decrypts a file that was previously encrypted using the encrypt_file method.
    This method performs the following operations:
    1. Derives the encryption key from the passphrase using PBKDF2
    2. Reads the IV (Initialization Vector) from the first 16 bytes of the encrypted file
    3. Creates an AES cipher in CBC mode using the derived key and IV
    4. Decrypts the data and removes PKCS7 padding
    5. Writes the decrypted data to the output file
    Args:
        input_file (str): Path to the encrypted file to be decrypted
        output_file (str): Path where the decrypted file should be saved
        int: Time taken to decrypt in milliseconds
    Raises:
        Exception: If any error occurs during the decryption process
        The decryption process uses AES-256 in CBC mode and expects PKCS7 padding.
        The file format must match the one produced by encrypt_file method.

    """
    def decrypt_file(self, input_file, output_file):
        start_time = time.perf_counter()
        try:
            key = self._derive_key()

            # Read IV and encrypted data from file
            with open(input_file, 'rb') as f_in:
                iv = f_in.read(16)  # First 16 bytes are IV
                encrypted_data = f_in.read()

            # Create AES cipher in CBC mode
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()

            # Decrypt the data and remove padding
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            unpadded_data = self._unpad_data(decrypted_data)

            # Write decrypted data to output file
            with open(output_file, 'wb') as f_out:
                f_out.write(unpadded_data)

            print(f"File '{input_file}' decrypted successfully to '{output_file}'.")
            return int((time.perf_counter() - start_time) * 1000)  # Return time in milliseconds

        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")


    """
    Removes PKCS#7 padding from the decrypted data.

    This method is required because block ciphers operate on fixed-size blocks (e.g., 16 bytes for AES). 
    When encrypting data that isn't a multiple of the block size, padding is added to reach the required length.
    After decryption, this padding needs to be removed to restore the original data.

    Args:
        data (bytes): The decrypted data with padding

    Returns:
        bytes: The original data with padding removed

    Example:
        If the last byte is 0x04, it indicates 4 bytes of padding were added,
        so the method removes the last 4 bytes from the data.
    """
    def _unpad_data(self, data):
        padding_length = data[-1]
        return data[:-padding_length]
        
    """Encrypts a file using AES-256 in CBC mode with PKCS7 padding.
    This method reads the input file, encrypts its contents using a key derived from
    the passphrase, and writes the encrypted data along with the IV to the output file.
    Args:
        input_file (str): Path to the file to be encrypted
        output_file (str): Path where the encrypted file will be saved
    Returns:
        int: Time taken for encryption in milliseconds
    Raises:
        Exception: If encryption fails for any reason (file I/O, encryption process, etc.)
    Note:
        The output file format consists of:
        - First 16 bytes: Initialization Vector (IV)
        - Remaining bytes: Encrypted data with PKCS7 padding
    """
    def encrypt_file(self, input_file, output_file):
        start_time = time.perf_counter()
        try:
            # Generate key from passphrase
            key = self._derive_key()
            
            # Generate random IV (16 bytes for AES)
            iv = secrets.token_bytes(16)
            
            # Create AES cipher in CBC mode with PKCS7 padding
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()

            # Read input file and encrypt
            with open(input_file, 'rb') as f_in:
                file_data = f_in.read()
                
            # Encrypt the data
            padded_data = self._pad_data(file_data)
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

            # Write IV and encrypted data to output file
            with open(output_file, 'wb') as f_out:
                f_out.write(iv)  # Write IV first (16 bytes)
                f_out.write(encrypted_data)

            print(f"File '{input_file}' encrypted successfully to '{output_file}'.")
            return int((time.perf_counter() - start_time) * 1000)  # Return time in milliseconds
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")

    """
    Applies PKCS7 padding to the input data for AES encryption.

    PKCS7 padding ensures the data length is a multiple of the block size by
    adding padding bytes. The value of each padding byte is equal to the 
    number of padding bytes added.

    Args:
        data (bytes): The data to be padded

    Returns:
        bytes: The padded data with PKCS7 padding applied

    Example:
        If block_size is 16 and data length is 10, 6 padding bytes each with
        value 6 will be added, resulting in a 16-byte output.
    """
    def _pad_data(self, data):
        # PKCS7 padding
        block_size = algorithms.AES.block_size // 8
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding


"""Parse command line arguments for file encryption/decryption.

This function sets up and processes command line arguments for the file encryption tool.
It handles the operation type (encrypt/decrypt), email address, and file paths.

Args:
    argv (list, optional): List of command line arguments. Defaults to None,
        in which case sys.argv[1:] is used.

Returns:
    tuple: A 4-element tuple containing:
        - operation (str): The operation to perform ('encrypt' or 'decrypt')
        - email (str): The recipient's email address
        - input_file (str): Path to the input file
        - output_file (str): Path for the output file

Example:
    >>> operation, email, in_file, out_file = parse_args(['encrypt', 'user@example.com',
        '-i', 'input.txt', '-o', 'output.enc'])
"""
def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt a file using a passphrase associated with the given email."
    )
    parser.add_argument("operation", choices=["encrypt", "decrypt"], help="Operation to perform (encrypt or decrypt)")
    parser.add_argument("email", help="Recipient email address (positional, no flag)")
    parser.add_argument("-i", "--input", dest="input_file", required=True, help="Path to the file to encrypt")
    parser.add_argument("-o", "--output", dest="output_file", required=True, help="Path to save the encrypted file")
    args = parser.parse_args(argv)
    return args.operation, args.email, args.input_file, args.output_file


def main(argv=None):
    """Entry point for the file encryption/decryption program.

    This function handles the main workflow of the program, including argument parsing,
    passphrase collection, and file encryption/decryption operations.

    Args:
        argv (list, optional): List of command line arguments. Defaults to None.
            If None, sys.argv[1:] will be used.

    Returns:
        None

    Raises:
        SystemExit: If argument parsing fails or if an error occurs during encryption/decryption.

    Note:
        The passphrase is securely collected using getpass and is cleared from memory
        after use for security purposes.
    """
    try:
        operation, email, input_file, output_file = parse_args(argv)
    except SystemExit:
        # argparse already printed help or error to stderr; re-raise to exit with its code
        raise

    # Never accept passphrase from the command line
    passphrase = getpass.getpass(prompt="Enter your passphrase: ")

    try:
        encryptor = FileEncryptor(email, passphrase)
        if operation == "encrypt":
            eltime = encryptor.encrypt_file(input_file, output_file)
            print(f"Encryption completed in {eltime} ms.")
        elif operation == "decrypt":
            eltime = encryptor.decrypt_file(input_file, output_file)
            print(f"Decryption completed in {eltime} ms.")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Clear sensitive data
        del passphrase

if __name__ == "__main__":
    main()