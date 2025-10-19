import gnupg
import os
import argparse
import sys
import getpass


class FileEncryptor:
    def __init__(self, email, passphrase):
        # Initialize the FileEncryptor with the user's email and passphrase
        self.email = email
        self.passphrase = passphrase

    def encrypt_file(self, input_file, output_file):
        # Encrypt the specified input file and save it to the output file

        # Create a GPG object
        gpg = gnupg.GPG()

        # Check if the key already exists
        key_list = gpg.list_keys()
        if not any(key['email'] == self.email for key in key_list):
            raise ValueError("No GPG key found for the provided email.")

        # Read the input file
        with open(input_file, 'rb') as f:
            file_data = f.read()

        # Encrypt the file data
        encrypted_data = gpg.encrypt(file_data, recipients=self.email, passphrase=self.passphrase)

        # Check if the encryption was successful
        if not encrypted_data.ok:
            raise Exception(f"Encryption failed: {encrypted_data.stderr}")

        # Write the encrypted data to the output file
        with open(output_file, 'wb') as f:
            f.write(encrypted_data.data)

        print(f"File '{input_file}' encrypted successfully to '{output_file}'.")

# Example usage:
# if __name__ == "__main__":
#     email = input("Enter your email address: ")
#     passphrase = input("Enter your passphrase: ")
#     input_file = input("Enter the path to the file to encrypt: ")
#     output_file = input("Enter the path to save the encrypted file: ")
#     
#     encryptor = FileEncryptor(email, passphrase)
#     encryptor.encrypt_file(input_file, output_file)

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Encrypt a file using a GPG key associated with the given email."
    )
    parser.add_argument("email", help="Recipient email address (positional, no flag)")
    parser.add_argument("-i", "--input", dest="input_file", required=True, help="Path to the file to encrypt")
    parser.add_argument("-o", "--output", dest="output_file", required=True, help="Path to save the encrypted file")
    args = parser.parse_args(argv)
    return args.email, args.input_file, args.output_file

def main(argv=None):
    try:
        email, input_file, output_file = parse_args(argv)
    except SystemExit:
        # argparse already printed help or error to stderr; re-raise to exit with its code
        raise

    # Never accept passphrase from the command line
    passphrase = getpass.getpass(prompt="Enter your GPG passphrase: ")

    try:
        encryptor = FileEncryptor(email, passphrase)
        encryptor.encrypt_file(input_file, output_file)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()