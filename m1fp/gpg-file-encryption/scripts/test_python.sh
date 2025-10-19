#!/bin/bash
# This script tests the Python GPG file encryption utility.

# Prompt for the user's email address
read -p "Enter your email address: " email

# Prompt for the user's passphrase
read -sp "Enter your passphrase: " passphrase
echo

# Prompt for the file to encrypt
read -p "Enter the path of the file to encrypt: " file_to_encrypt

# Call the Python file encryption utility
python3 -m encryptor.file_encryptor encrypt "$file_to_encrypt" "$email" "$passphrase" 

# Check if the encryption was successful
if [ $? -eq 0 ]; then
    echo "File encrypted successfully."
else
    echo "File encryption failed."
fi