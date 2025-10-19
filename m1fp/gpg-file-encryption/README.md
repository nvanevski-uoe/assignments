# GPG File Encryption Utility

## Overview
This project provides utilities for encrypting files using GPG (GNU Privacy Guard) in both Java and Python. It includes classes for handling file encryption, as well as test scripts to facilitate user interaction for encryption tasks.

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
- Install GPG on your system.

### GPG Setup on Ubuntu
1. **Install GPG**:
   ```bash
   sudo apt update
   sudo apt install gnupg
   ```

2. **Generate GPG Keys**:
   ```bash
   gpg --full-generate-key
   ```
   Follow the prompts to create your key pair. Make sure to remember the email address and passphrase you used.

3. **List Your Keys**:
   ```bash
   gpg --list-keys
   ```
   This will show you the keys you have generated.

## Usage
To encrypt a file using the Java utility:
1. Navigate to the `java` directory.
2. Compile the Java files using Maven:
   ```bash
   mvn clean install
   ```
3. Run the test script:
   ```bash
   bash ../scripts/test_java.sh
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
This project is licensed under the MIT License. See the LICENSE file for more details.