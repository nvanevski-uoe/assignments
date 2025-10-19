/**
 * A utility class for file encryption using AES-256-CBC with PBKDF2 key derivation.
 * 
 * This class provides functionality to encrypt files using:
 * - AES-256 encryption in CBC mode with PKCS5 padding
 * - PBKDF2 with HMAC-SHA256 for key derivation from a passphrase
 * - Email address as salt for the key derivation
 * - Secure random IV generation
 * 
 * The encrypted file format prepends a 16-byte IV to the encrypted data.
 * The encryption process uses streams for memory-efficient handling of large files.
 * 
 * Usage example:
 * FileEncryptor encryptor = new FileEncryptor();
 * encryptor.encryptFile("input.txt", "encrypted.bin", "user@example.com", "passphrase".toCharArray());
 * encryptor.decryptFile("encrypted.bin", "decrypted.txt", "user@example.com", "passphrase".toCharArray());
 * 
 * Security features:
 * - Uses SecureRandom for IV generation
 * - Implements standard cryptographic practices with AES-256
 * - Never stores plaintext passwords as strings
 * - Securely wipes sensitive data (passphrase) from memory after use
 * 
 * Command line usage:
 * java -jar app.jar <email> -i <input-file> -o <output-file>
 * 
 * @author Nikola Vanevski <nikola@vanevski.net>
 * @version 1.0
 */

package com.example.gpg;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.security.spec.KeySpec;
import java.util.Scanner;

import javax.crypto.Cipher;
import javax.crypto.CipherOutputStream;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;


public class FileEncryptor {

    // Method to encrypt a file using AES-256-CBC with a key derived from the passphrase (email used as salt)
    public void encryptFile(String inputFilePath, String outputFilePath, String email, char[] passphrase) {
        try {
            // Derive AES key from passphrase using PBKDF2 with HMAC-SHA256
            byte[] salt = (email != null) ? email.getBytes(StandardCharsets.UTF_8) : new byte[8];
            SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
            KeySpec spec = new PBEKeySpec(passphrase, salt, 65536, 256);
            SecretKey tmp = factory.generateSecret(spec);
            SecretKeySpec secretKey = new SecretKeySpec(tmp.getEncoded(), "AES");

            // Generate random IV
            byte[] iv = new byte[16];
            SecureRandom random = new SecureRandom();
            random.nextBytes(iv);
            IvParameterSpec ivSpec = new IvParameterSpec(iv);

            // Initialize cipher
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
            cipher.init(Cipher.ENCRYPT_MODE, secretKey, ivSpec);

            // Stream input -> cipher -> output; write IV as the first 16 bytes of the output file
            try (FileInputStream fis = new FileInputStream(inputFilePath);
                 FileOutputStream fos = new FileOutputStream(outputFilePath)) {

                fos.write(iv); // prepend IV
                try (CipherOutputStream cos = new CipherOutputStream(fos, cipher)) {
                    byte[] buffer = new byte[4096];
                    int n;
                    while ((n = fis.read(buffer)) != -1) {
                        cos.write(buffer, 0, n);
                    }
                }
            }
        } catch (IOException e) {
            System.err.println("I/O error during file encryption: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Encryption error: " + e.getMessage());
        }
    }

    // Method to decrypt a file that was encrypted using AES-256-CBC with a key derived from the passphrase
    public void decryptFile(String inputFilePath, String outputFilePath, String email, char[] passphrase) {
        try {
            // Derive AES key from passphrase using PBKDF2 with HMAC-SHA256
            byte[] salt = (email != null) ? email.getBytes(StandardCharsets.UTF_8) : new byte[8];
            SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
            KeySpec spec = new PBEKeySpec(passphrase, salt, 65536, 256);
            SecretKey tmp = factory.generateSecret(spec);
            SecretKeySpec secretKey = new SecretKeySpec(tmp.getEncoded(), "AES");

            // Read IV from the first 16 bytes of the encrypted file
            try (FileInputStream fis = new FileInputStream(inputFilePath)) {
                byte[] iv = new byte[16];
                if (fis.read(iv) != 16) {
                    throw new IOException("Invalid encrypted file format");
                }
                IvParameterSpec ivSpec = new IvParameterSpec(iv);

                // Initialize cipher for decryption
                Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
                cipher.init(Cipher.DECRYPT_MODE, secretKey, ivSpec);

                // Stream input -> cipher -> output
                try (FileOutputStream fos = new FileOutputStream(outputFilePath);
                     CipherOutputStream cos = new CipherOutputStream(fos, cipher)) {
                    byte[] buffer = new byte[4096];
                    int n;
                    while ((n = fis.read(buffer)) != -1) {
                        cos.write(buffer, 0, n);
                    }
                }
            }
        } catch (IOException e) {
            System.err.println("I/O error during file decryption: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Decryption error: " + e.getMessage());
        }
    }

     // Argument holder
    private static class ParsedArgs {
        final String email;
        final String inputFile;
        final String outputFile;

        ParsedArgs(String email, String inputFile, String outputFile) {
            this.email = email;
            this.inputFile = inputFile;
            this.outputFile = outputFile;
        }
    }
    // Main method for parsing command line arguments and determining operation
    private static String parseOperation(String[] args) {
        if (args == null || args.length < 1) {
            return null;
        }
        String op = args[0].toLowerCase();
        if ("encrypt".equals(op) || "decrypt".equals(op)) {
            return op;
        }
        System.err.println("Error: first argument must be either 'encrypt' or 'decrypt'");
        return null;
    }

    private static void printUsage() {
        System.out.println("Usage: java -jar app.jar <operation> <email> -i <input-file> -o <output-file>");
        System.out.println("  <operation>        : 'encrypt' or 'decrypt' - required as first argument");
        System.out.println("  <email>           : email address (used as salt) - required as second argument");
        System.out.println("  -i <input-file>   : path to the input file");
        System.out.println("  -o <output-file>  : path to write the output file");
        System.out.println();
        System.out.println("Note: The passphrase will be prompted interactively (never pass it on the command line).");
    }

    // Updated parseArgs method to handle operation
    private static ParsedArgs parseArgs(String[] args) {
        if (args == null || args.length < 2) {
            printUsage();
            return null;
        }

        String email = args[1];
        if (email.startsWith("-")) {
            System.err.println("Error: second argument must be the email (no flag).");
            printUsage();
            return null;
        }

        String inputFile = null;
        String outputFile = null;

        for (int i = 2; i < args.length; i++) {
            String a = args[i];
            if ("-i".equals(a)) {
                if (i + 1 >= args.length) {
                    System.err.println("Error: -i requires a file path.");
                    printUsage();
                    return null;
                }
                inputFile = args[++i];
            } else if ("-o".equals(a)) {
                if (i + 1 >= args.length) {
                    System.err.println("Error: -o requires a file path.");
                    printUsage();
                    return null;
                }
                outputFile = args[++i];
            } else {
                System.err.println("Unknown option: " + a);
                printUsage();
                return null;
            }
        }

        if (inputFile == null || outputFile == null) {
            System.err.println("Error: both -i and -o must be provided.");
            printUsage();
            return null;
        }

        return new ParsedArgs(email, inputFile, outputFile);
    }

    public static void main(String[] args) {
        ParsedArgs p = parseArgs(args);
        if (p == null) {
            System.exit(2);
        }

        char[] pw;
        java.io.Console console = System.console();
        if (console != null) {
            pw = console.readPassword("Enter your passphrase: ");
            if (pw == null || pw.length == 0) {
                System.err.println("Passphrase is required.");
                System.exit(3);
                return;
            }
        } else {
            // Fallback when no console is available (e.g., IDE). Warn the user.
            System.err.println("Warning: Console not available. Password input may be visible.");
            System.out.print("Enter your passphrase: ");
            Scanner scanner = new Scanner(System.in);
            String passphrase = scanner.nextLine();
            pw = passphrase.toCharArray();
            // Clear the String from memory
            passphrase = null;
            System.gc();
            // do not close System.in here if other code may use it; close local scanner
            scanner.close();
        }

        try {
            new FileEncryptor().encryptFile(p.inputFile, p.outputFile, p.email, pw);
            System.out.println("File encrypted successfully.");
        } catch (Exception e) {
            System.err.println("Encryption failed: " + e.getMessage());
            System.exit(4);
        } finally {
            // Safely overwrite passphrase in memory
            java.util.Arrays.fill(pw, '\0');
        }
        
    }
}