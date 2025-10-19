# GPG Setup on Ubuntu

## Introduction
This document provides a step-by-step guide to setting up GPG (GNU Privacy Guard) on Ubuntu Linux. GPG is a tool for secure communication and data storage, allowing you to encrypt and sign your data and communications.

## Prerequisites
Ensure that you have administrative privileges on your Ubuntu system to install packages.

## Step 1: Install GPG
Open a terminal and run the following command to install GPG:

```bash
sudo apt update
sudo apt install gnupg
```

## Step 2: Generate a GPG Key Pair
After installing GPG, you need to generate a key pair (public and private keys). Run the following command:

```bash
gpg --full-generate-key
```

You will be prompted to select the kind of key you want. The default option (RSA and RSA) is usually sufficient. Follow the prompts to set the key size (2048 or 4096 bits), expiration date, and user identification (name and email address). You will also need to create a passphrase to protect your private key.

## Step 3: List Your Keys
To verify that your keys have been generated, you can list them with the following command:

```bash
gpg --list-keys
```

This will display your public keys. To see your private keys, use:

```bash
gpg --list-secret-keys
```

## Step 4: Export Your Public Key
If you need to share your public key with others, you can export it using the following command:

```bash
gpg --export -a "your_email@example.com" > public_key.asc
```

Replace `your_email@example.com` with the email address you used when generating the key.

## Step 5: Import a Public Key
If you receive a public key from someone else, you can import it using:

```bash
gpg --import public_key.asc
```

## Step 6: Configure GPG for Use
You may want to configure GPG to use a specific key for signing and encrypting. You can set your default key with:

```bash
gpg --default-key your_email@example.com
```

## Conclusion
You have now set up GPG on your Ubuntu system. You can use it to encrypt files and communications securely. For more advanced usage, refer to the GPG documentation or the `man gpg` command for detailed options and features.