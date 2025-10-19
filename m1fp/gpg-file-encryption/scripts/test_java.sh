#!/bin/bash

# This script tests the Java GPG file encryption utility.

# Prompt the user for their email address
read -p "Enter your email address for GPG: " email

# Prompt the user for their passphrase
read -s -p "Enter your passphrase: " passphrase
echo

# Specify the file to encrypt
read -p "Enter the path of the file to encrypt: " file_to_encrypt

# Call the Java program to encrypt the file
# Assuming the compiled Java class is in the target directory
java -cp ../target/classes com.example.gpg.FileEncryptor "$file_to_encrypt" "$email" "$passphrase"

# Check if the encryption was successful
if [ $? -eq 0 ]; then
    echo "File encrypted successfully."
else
    echo "File encryption failed."
fi