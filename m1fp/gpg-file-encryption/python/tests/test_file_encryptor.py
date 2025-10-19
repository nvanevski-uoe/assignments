# test_file_encryptor.py

import os
import gnupg
import unittest

class TestFileEncryptor(unittest.TestCase):
    def setUp(self):
        # Initialize the GPG instance
        self.gpg = gnupg.GPG()
        # Create a temporary file for testing
        self.test_file_path = 'test_file.txt'
        with open(self.test_file_path, 'w') as f:
            f.write('This is a test file for GPG encryption.')

    def tearDown(self):
        # Remove the temporary test file after tests
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_encrypt_file(self):
        # Test the encryption of the file
        email = 'test@example.com'  # Replace with a valid email for testing
        passphrase = 'testpass'      # Replace with a valid passphrase for testing

        # Encrypt the file
        with open(self.test_file_path, 'rb') as f:
            status = self.gpg.encrypt_file(f, recipients=[email], passphrase=passphrase)

        # Check if the encryption was successful
        self.assertTrue(status.ok)
        self.assertIsNotNone(status.stderr)

    def test_encrypt_file_invalid_email(self):
        # Test encryption with an invalid email
        email = 'invalid@example.com'
        passphrase = 'testpass'

        with open(self.test_file_path, 'rb') as f:
            status = self.gpg.encrypt_file(f, recipients=[email], passphrase=passphrase)

        # Check if the encryption failed
        self.assertFalse(status.ok)

if __name__ == '__main__':
    unittest.main()