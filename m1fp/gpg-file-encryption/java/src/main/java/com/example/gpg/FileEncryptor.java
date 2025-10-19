// FileEncryptor.java
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
    public void encryptFile(String inputFilePath, String outputFilePath, String email, String passphrase) {
        try {
            // Derive AES key from passphrase using PBKDF2 with HMAC-SHA256
            byte[] salt = (email != null) ? email.getBytes(StandardCharsets.UTF_8) : new byte[8];
            SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
            KeySpec spec = new PBEKeySpec(passphrase.toCharArray(), salt, 65536, 256);
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

    private static void printUsage() {
        System.out.println("Usage: java -jar <app>.jar <email> -i <input-file> -o <output-file>");
        System.out.println("  <email>           : email address (used as salt) - required and must be the first argument");
        System.out.println("  -i <input-file>   : path to the file to encrypt");
        System.out.println("  -o <output-file>  : path to write the encrypted output");
        System.out.println();
        System.out.println("Note: The passphrase will be prompted interactively (never pass it on the command line).");
    }

    private static ParsedArgs parseArgs(String[] args) {
        if (args == null || args.length == 0) {
            printUsage();
            return null;
        }

        String email = args[0];
        if (email.startsWith("-")) {
            System.err.println("Error: first argument must be the email (no flag).");
            printUsage();
            return null;
        }

        String inputFile = null;
        String outputFile = null;

        for (int i = 1; i < args.length; i++) {
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

        String passphrase;
        java.io.Console console = System.console();
        if (console != null) {
            char[] pw = console.readPassword("Enter your passphrase: ");
            if (pw == null || pw.length == 0) {
                System.err.println("Passphrase is required.");
                System.exit(3);
                return;
            }
            passphrase = new String(pw);
            java.util.Arrays.fill(pw, '\0'); // clear password chars
        } else {
            // Fallback when no console is available (e.g., IDE). Warn the user.
            System.out.print("Enter your passphrase: ");
            Scanner scanner = new Scanner(System.in);
            passphrase = scanner.nextLine();
            // do not close System.in here if other code may use it; close local scanner
            scanner.close();
        }

        try {
            new FileEncryptor().encryptFile(p.inputFile, p.outputFile, p.email, passphrase);
            System.out.println("File encrypted successfully.");
        } catch (Exception e) {
            System.err.println("Encryption failed: " + e.getMessage());
            System.exit(4);
        } finally {
            // Help GC and reduce lifetime of passphrase
            passphrase = null;
        }
    }
}