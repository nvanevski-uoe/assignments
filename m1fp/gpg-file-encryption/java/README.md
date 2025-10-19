<!--
This documentation describes a command-line utility for GPG file encryption and decryption 
implemented in Java. The tool provides a secure way to encrypt and decrypt files using 
AES-256 standard.

Environment Requirements:
- Operating System: Ubuntu Linux 20.04 LTS or higher
- Memory: Minimum 2GB RAM recommended
- Disk Space: At least 100MB free space
- Network: Internet connection required for initial build (Maven dependencies)

The utility supports:
- Symmetric encryption using passphrase
- File decryption with proper credentials
- Large file handling (files larger than 2GB)
- Progress monitoring during encryption/decryption

-->
# GPG File Encryption - Java Implementation

## Prerequisites
- Java JDK 11 or higher
- Maven 3.6 or higher
- Ubuntu Linux

## Building the Project
1. Clone the repository:
```bash
git clone <repository-url>
cd gpg-file-encryption/java
```

2. Build with Maven:
```bash
mvn clean package
```

The JAR file will be generated in the `target` directory.

## Usage Examples
After building, you can run the JAR file using:

```bash
java -jar target/gpg-file-encryption-1.0.jar <options>
```

### Basic Usage Examples:
1. Encrypt a file:
```bash
java -jar target/gpg-file-encryption-1.0.jar -e -i input.txt -o encrypted.gpg
```

2. Decrypt a file:
```bash
java -jar target/gpg-file-encryption-1.0.jar -d -i encrypted.gpg -o decrypted.txt
```

## Troubleshooting
If you encounter any build issues:
- Ensure Java and Maven are correctly installed:
```bash
java --version
mvn --version
```
- Try cleaning the Maven cache:
```bash
mvn clean
rm -rf ~/.m2/repository/com/example/gpg-file-encryption
```