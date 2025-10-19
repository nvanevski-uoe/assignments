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
 *      FileEncryptor encryptor = new FileEncryptor();
 *      encryptor.encryptFile("input.txt", "encrypted.bin", "user@example.com", "passphrase".toCharArray());
 *      encryptor.decryptFile("encrypted.bin", "decrypted.txt", "user@example.com", "passphrase".toCharArray());
 * 
 * Security features:
 * - Uses SecureRandom for IV generation
 * - Implements standard cryptographic practices with AES-256
 * - Never stores plaintext passwords as strings
 * - Securely wipes sensitive data (passphrase) from memory after use
 * 
 * Command line usage:
 *      java -jar endec.jar <operation> <email> -i <input-file> -o <output-file>
 * 
 * @author Nikola Vanevski <nikola@vanevski.net>
 * @version 1.0
 */

package net.vanevski.endec;

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

    /**
     * Encrypts a file using AES-256 in CBC mode with PKCS5 padding.
     * The encryption key is derived from the provided passphrase using PBKDF2 with HMAC-SHA256.
     * The email address is used as a salt for the key derivation.
     * The IV is randomly generated and prepended to the encrypted file.
     *
     * @param inputFilePath  path to the input file to be encrypted
     * @param outputFilePath path where the encrypted file will be written
     * @param email         email address used as salt for key derivation (if null, uses 8 zero bytes)
     * @param passphrase    the passphrase used to derive the encryption key
     * @throws IOException          if there are issues reading input or writing output files
     * @throws NoSuchAlgorithmException if the required cryptographic algorithms are not available
     * @throws InvalidKeySpecException  if the key specification is invalid
     * @throws NoSuchPaddingException  if the requested padding mechanism is not available
     * @throws InvalidKeyException     if the generated key is invalid
     * @throws InvalidAlgorithmParameterException if the IV parameter is invalid
     */
    public long encryptFile(String inputFilePath, String outputFilePath, String email, char[] passphrase) {
        long startTime = System.currentTimeMillis();
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
            return System.currentTimeMillis() - startTime;
        } catch (IOException e) {
            System.err.println("I/O error during file encryption: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Encryption error: " + e.getMessage());
        }
        return -1L;
    }

    /**
     * Decrypts a file that was encrypted using AES-256 in CBC mode with PKCS5 padding.
     * The decryption key is derived from the provided passphrase using PBKDF2 with HMAC-SHA256.
     * The email address is used as a salt for the key derivation.
     * The IV is read from the first 16 bytes of the encrypted file.
     *
     * @param inputFilePath  path to the encrypted input file
     * @param outputFilePath path where the decrypted file will be written
     * @param email         email address used as salt for key derivation (if null, uses 8 zero bytes)
     * @param passphrase    the passphrase used to derive the decryption key
     * @throws IOException          if there are issues reading input or writing output files
     * @throws NoSuchAlgorithmException if the required cryptographic algorithms are not available
     * @throws InvalidKeySpecException  if the key specification is invalid
     * @throws NoSuchPaddingException  if the requested padding mechanism is not available
     * @throws InvalidKeyException     if the generated key is invalid
     * @throws InvalidAlgorithmParameterException if the IV parameter is invalid
     */
    public long decryptFile(String inputFilePath, String outputFilePath, String email, char[] passphrase) {
        long startTime = System.currentTimeMillis();
        try {
            // Derive AES key from passphrase using PBKDF2 with HMAC-SHA256
            byte[] salt = (email != null) ? email.getBytes(StandardCharsets.UTF_8) : new byte[8];
            SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
            KeySpec spec = new PBEKeySpec(passphrase, salt, 65536, 256);
            SecretKey tmp = factory.generateSecret(spec);
            SecretKeySpec secretKey = new SecretKeySpec(tmp.getEncoded(), "AES");

            // Read IV from the first 16 bytes of encrypted file
            try (FileInputStream fis = new FileInputStream(inputFilePath)) {
                byte[] iv = new byte[16];
                if (fis.read(iv) != 16) {
                    throw new IOException("Invalid encrypted file format");
                }
                IvParameterSpec ivSpec = new IvParameterSpec(iv);

                // Initialize cipher for decryption
                Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
                cipher.init(Cipher.DECRYPT_MODE, secretKey, ivSpec);

                // Stream encrypted input -> cipher -> output
                try (FileOutputStream fos = new FileOutputStream(outputFilePath);
                     CipherOutputStream cos = new CipherOutputStream(fos, cipher)) {
                    byte[] buffer = new byte[4096];
                    int n;
                    while ((n = fis.read(buffer)) != -1) {
                        cos.write(buffer, 0, n);
                    }
                }
            }
            return System.currentTimeMillis() - startTime;
        } catch (IOException e) {
            System.err.println("I/O error during file decryption: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Decryption error: " + e.getMessage());
        }
        return -1L;
    }

    /**
     * A data class to hold the parsed command line arguments.
     * 
     * This class encapsulates four main components required for file encryption/decryption:
     * - The operation to perform (encrypt or decrypt)
     * - The email address associated with the GPG key
     * - The input file path to process
     * - The output file path for the result
     * 
     * The class is immutable as all fields are final.
     */
    private static class ParsedArgs {
        final String operation;
        final String email;
        final String inputFile;
        final String outputFile;

        ParsedArgs(String operation, String email, String inputFile, String outputFile) {
            this.operation = operation;
            this.email = email;
            this.inputFile = inputFile;
            this.outputFile = outputFile;
        }
    }

    private static void printUsage() {
        System.out.println("Usage: java -jar <app>.jar <operation> <email> -i <input-file> -o <output-file>");
        System.out.println("  <operation>       : operation to perform (encrypt or decrypt) - required and must be the first argument");
        System.out.println("  <email>           : email address (used as salt) - required and must be the second argument");
        System.out.println("  -i <input-file>   : path to the file to encrypt");
        System.out.println("  -o <output-file>  : path to write the encrypted output");
        System.out.println();
        System.out.println("Note: The passphrase will be prompted interactively (never pass it on the command line).");
    }


    /**
     * Parses command line arguments for file encryption/decryption operations.
     * 
     * @param args Command line arguments array containing:
     *             1. Operation type ("encrypt" or "decrypt")
     *             2. Email address
     *             3. Input/output file paths with -i and -o flags
     * @return ParsedArgs object containing the parsed arguments, or null if parsing fails
     *         The ParsedArgs contains:
     *         - operation: "encrypt" or "decrypt"
     *         - email: validated email address
     *         - inputFile: path to input file
     *         - outputFile: path to output file
     */
    private static ParsedArgs parseArgs(String[] args) {
        if (args == null || args.length == 0) {
            printUsage();
            return null;
        }

        String operation = args[0];
        if (! ("encrypt".equals(operation) || "decrypt".equals(operation))) {
            System.err.println("Error: first argument must be the operation - 'encrypt' or 'decrypt' (no flag).");
            printUsage();
            return null;
        }

        String email = args[1];
        if (!email.matches("^[A-Za-z0-9+_.-]+@(.+)$")) {
            System.err.println("Error: second argument must be the correctly formatted email.");
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

        return new ParsedArgs(operation, email, inputFile, outputFile);
    }

    /**
     * Main entry point for the file encrypt/decrypt utility.
     * Processes command line arguments and handles file encryption operations.
     * 
     * The program expects command line arguments for:
     * - Operation type (encrypt/decrypt)
     * - Input file path 
     * - Output file path
     * - Email address for encryption
     * 
     * The program will prompt for a passphrase via console or standard input
     * if console is not available. The passphrase is securely handled and
     * cleared from memory after use.
     *
     * @param args Command line arguments containing operation details
     *             
     * Exit codes:
     *  2 - Invalid command line arguments
     *  3 - Missing or invalid passphrase
     *  4 - Encryption or decryption operation failed
\     */
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
            FileEncryptor encryptor = new FileEncryptor();
            long opTime;
            if ("encrypt".equals(p.operation)) {
                opTime = encryptor.encryptFile(p.inputFile, p.outputFile, p.email, pw);
                System.out.println("File encrypted successfully in " + opTime + " ms.");
            } else {
                opTime = encryptor.decryptFile(p.inputFile, p.outputFile, p.email, pw);
                System.out.println("File decrypted successfully in " + opTime + " ms.");
            }
        } catch (Exception e) {
            System.err.println("Operation failed: " + e.getMessage());
            System.exit(4);
        } finally {
            // Safely overwrite passphrase in memory
            java.util.Arrays.fill(pw, '\0');
        }
        
    }
}