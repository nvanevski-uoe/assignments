# File Encryption And Decryption Utility

## Overview
This project provides utilities for encrypting files using AES-256 algorith in both Java and Python. It includes classes for handling file encryption, as well as test scripts to facilitate user interaction for encryption tasks.

## Project Structure
The project is organized into the following directories:

- **java**: Contains the Java implementation of the file encryption utility.
- **python**: Contains the Python implementation of the file encryption utility.
- **scripts**: Contains test scripts for both Java and Python utilities.
- **docs**: Contains documentation for setting up GPG on Ubuntu.
- **comparisons.md**: Contains a comparison of the Java and Python implementations.
- **.gitignore**: Specifies files to be ignored by Git.

## Setup Instructions

### Prerequisites
- Ensure you have Java (JDK) and Maven installed for the Java utility.
- Ensure you have Python and pip installed for the Python utility.

## Usage
To encrypt a file using the Java utility:
1. Navigate to the `java` directory.
2. Compile the Java files using Maven:
   ```bash
   mvn clean install
   ```
3. Run the test script:
   ```bash
   java -jar target/endec.jar encrypt <email-address> -i <input file> -o <output file>
   ```

Output of the script for a 100MB text file is following:
   ```bash
   [~/src/uoe/assignments/m1fp/gpg-file-encryption/java]$ java -jar target/endec.jar encrypt nikola@vanevski.net -i ../../loremipsum.txt -o ../../encrypted.bin
   Enter your passphrase: 
   File encrypted successfully in 384 ms.
   [~/src/uoe/assignments/m1fp/gpg-file-encryption/java]$ java -jar target/endec.jar decrypt nikola@vanevski.net -i ../../encrypted.bin -o ../../decrypted.txt
   Enter your passphrase: 
   File decrypted successfully in 290 ms.
   ```

To encrypt a file using the Python utility:
1. Navigate to the `python` directory.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the test script:
   ```bash
   bash ../scripts/test_python.sh
   ```

## Contributing
Feel free to contribute to this project by submitting issues or pull requests.

## License
This project is licensed under the Creative Commons License.