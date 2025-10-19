from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets
import os
import argparse
import sys
import getpass

class FileEncryptor:
    def __init__(self, email, passphrase):
        # Initialize the FileEncryptor with the user's email and passphrase
        self.email = email
        self.passphrase = passphrase

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

    def decrypt_file(self, input_file, output_file):
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

        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")

    def _unpad_data(self, data):
        padding_length = data[-1]
        return data[:-padding_length]
        
    def encrypt_file(self, input_file, output_file):
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
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")

    def _pad_data(self, data):
        # PKCS7 padding
        block_size = algorithms.AES.block_size // 8
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt a file using a GPG key associated with the given email."
    )
    parser.add_argument("operation", choices=["encrypt", "decrypt"], help="Operation to perform (encrypt or decrypt)")
    parser.add_argument("email", help="Recipient email address (positional, no flag)")
    parser.add_argument("-i", "--input", dest="input_file", required=True, help="Path to the file to encrypt")
    parser.add_argument("-o", "--output", dest="output_file", required=True, help="Path to save the encrypted file")
    args = parser.parse_args(argv)
    return args.operation, args.email, args.input_file, args.output_file

def main(argv=None):
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
            encryptor.encrypt_file(input_file, output_file)
        elif operation == "decrypt":
            encryptor.decrypt_file(input_file, output_file) 
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Clear sensitive data
        del passphrase

if __name__ == "__main__":
    main()