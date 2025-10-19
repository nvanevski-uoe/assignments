// GpgUtils.java
package com.example.gpg;

import java.io.IOException;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.stream.Collectors;

/**
 * Utility class for GPG operations.
 */
public class GpgUtils {

    /**
     * Generates a GPG key pair.
     * 
     * @param email The email address associated with the key.
     * @param passphrase The passphrase for the key.
     * @throws IOException If an I/O error occurs during key generation.
     */
    public static void generateKeyPair(String email, String passphrase) throws IOException {
        // Command to generate GPG key pair
        List<String> command = new ArrayList<>(Arrays.asList("gpg", "--batch", "--gen-key"));
        // Here you would typically write the key parameters to a temporary file
        // and pass that file to the gpg command.
        // This is a placeholder for the actual implementation.
    }

    /**
     * Encrypts a file using GPG.
     * 
     * @param filePath The path to the file to encrypt.
     * @param recipientEmail The email address of the recipient.
     * @throws IOException If an I/O error occurs during encryption.
     */
    public static void encryptFile(String filePath, String recipientEmail) throws IOException {
        // Command to encrypt the file
        List<String> command = Arrays.asList("gpg", "--encrypt", "--recipient", recipientEmail, filePath);
        ProcessBuilder processBuilder = new ProcessBuilder(command);
        Process process = processBuilder.start();
        
        // Handle process output and errors
        try {
            int exitCode = process.waitFor();
            if (exitCode != 0) {
                throw new IOException("Encryption failed with exit code: " + exitCode);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IOException("Encryption process was interrupted", e);
        }
    }

    /**
     * Decrypts a file using GPG.
     * 
     * @param filePath The path to the file to decrypt.
     * @param passphrase The passphrase for the key.
     * @throws IOException If an I/O error occurs during decryption.
     */
    public static void decryptFile(String filePath, String passphrase) throws IOException {
        // Command to decrypt the file
        List<String> command = Arrays.asList("gpg", "--decrypt", "--passphrase", passphrase, filePath);
        ProcessBuilder processBuilder = new ProcessBuilder(command);
        Process process = processBuilder.start();
        
        // Handle process output and errors
        try {
            int exitCode = process.waitFor();
            if (exitCode != 0) {
                throw new IOException("Decryption failed with exit code: " + exitCode);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IOException("Decryption process was interrupted", e);
        }
    }
}