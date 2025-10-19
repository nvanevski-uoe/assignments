// FileEncryptorTest.java
package com.example.gpg;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Paths;

public class FileEncryptorTest {

    @Test
    public void testEncryptFileValidInput() {
        // Arrange
        String email = "test@example.com"; // Replace with a valid email
        String passphrase = "testpass"; // Replace with a valid passphrase
        String inputFilePath = "path/to/input/file.txt"; // Replace with a valid file path
        String outputFilePath = "path/to/output/encrypted_file.gpg"; // Replace with desired output path

        FileEncryptor encryptor = new FileEncryptor();
        
        // Act
        boolean result = encryptor.encryptFile(inputFilePath, outputFilePath, email, passphrase);
        
        // Assert
        assertTrue(result, "File should be encrypted successfully");
        assertTrue(Files.exists(Paths.get(outputFilePath)), "Encrypted file should exist");
    }

    @Test
    public void testEncryptFileInvalidEmail() {
        // Arrange
        String email = "invalid-email"; // Invalid email format
        String passphrase = "testpass";
        String inputFilePath = "path/to/input/file.txt"; // Replace with a valid file path
        String outputFilePath = "path/to/output/encrypted_file.gpg"; // Replace with desired output path

        FileEncryptor encryptor = new FileEncryptor();
        
        // Act
        boolean result = encryptor.encryptFile(inputFilePath, outputFilePath, email, passphrase);
        
        // Assert
        assertFalse(result, "Encryption should fail with invalid email");
    }

    @Test
    public void testEncryptFileInvalidPassphrase() {
        // Arrange
        String email = "test@example.com"; // Replace with a valid email
        String passphrase = ""; // Empty passphrase
        String inputFilePath = "path/to/input/file.txt"; // Replace with a valid file path
        String outputFilePath = "path/to/output/encrypted_file.gpg"; // Replace with desired output path

        FileEncryptor encryptor = new FileEncryptor();
        
        // Act
        boolean result = encryptor.encryptFile(inputFilePath, outputFilePath, email, passphrase);
        
        // Assert
        assertFalse(result, "Encryption should fail with empty passphrase");
    }

    // Additional tests can be added here for more scenarios
}