# Secure File Encryption \& Decryption Tool

A beginner-friendly web application built with Python Flask that allows users to securely encrypt and decrypt files using AES encryption (Fernet).

## Features

* **File Encryption** — Upload any supported file and encrypt it with a password
* **File Decryption** — Decrypt previously encrypted files using the same password
* **AES Encryption** — Uses industry-standard Fernet (AES-128-CBC) encryption
* **Password-Based Key Derivation** — Generates secure keys from passwords using SHA-256 + salt
* **No Password Storage** — Passwords are never saved; only you know your password
* **Modern UI** — Responsive Bootstrap 5 interface with clear feedback
* **Input Validation** — Validates file types, empty inputs, and password length
* **Error Handling** — Graceful handling of wrong passwords and corrupted files

## Supported File Types

* `.txt` — Text files
* `.pdf` — PDF documents
* `.docx` — Word documents
* `.png`, `.jpg`, `.jpeg` — Images
* `.csv` — CSV spreadsheets
* `.xlsx` — Excel spreadsheets

Maximum file size: **16 MB**

## Project Structure

```
SecurityPro/
├── app.py              # Main Flask application (routes \& logic)
├── encryption.py       # Encryption/decryption functions
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── templates/
│   └── index.html      # HTML template (Jinja2 + Bootstrap)
├── static/
│   └── style.css       # Custom CSS styles
├── uploads/            # Temporary upload storage (auto-created)
├── encrypted/          # Encrypted file output (auto-created)
└── decrypted/          # Decrypted file output (auto-created)
```

## Setup Instructions

### Prerequisites

* Python 3.8 or higher installed
* pip (Python package manager)

### Step 1: Clone or Download the Project

```bash
cd "C:\\Work file\\SecurityPro"
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\\Scripts\\activate

# Activate it (macOS/Linux)
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

### Step 5: Open in Browser

Navigate to: **http://127.0.0.1:5000**

## How It Works

### Encryption Process

1. User uploads a file and enters a password
2. A random 16-byte **salt** is generated
3. The password + salt are hashed with **SHA-256** to create an encryption key
4. The file is encrypted using **Fernet** (AES symmetric encryption)
5. The salt is prepended to the encrypted data and saved
6. The encrypted file is downloaded by the user

### Decryption Process

1. User uploads the encrypted file and enters the same password
2. The salt is extracted from the first 16 bytes of the file
3. The password + extracted salt are hashed to recreate the same key
4. The file is decrypted using Fernet
5. If the password is wrong, decryption fails with an error message
6. If successful, the original file is downloaded

### Security Notes

* **Passwords are never stored** — they exist only during the request
* **Each encryption uses a unique salt** — same file + same password = different output
* **Fernet provides authenticated encryption** — detects tampering and wrong passwords
* **Files are cleaned up** after processing to minimize data exposure

## Technologies Used

|Technology|Purpose|
|-|-|
|Python 3|Backend programming language|
|Flask|Web framework|
|Cryptography|Fernet/AES encryption library|
|Bootstrap 5|Responsive UI framework|
|Jinja2|HTML templating engine|
|Werkzeug|Secure file handling|

## Troubleshooting

|Problem|Solution|
|-|-|
|"Module not found" error|Run `pip install -r requirements.txt`|
|Port 5000 already in use|Change port in `app.py` or kill the existing process|
|Decryption fails|Ensure you're using the exact same password|
|File type not supported|Check the allowed extensions list above|
|Large file error|Files must be under 16 MB|

## Learning Points (For Beginners)

This project demonstrates:

1. **Flask web development** — Routes, templates, form handling
2. **File upload handling** — Secure filename processing with Werkzeug
3. **Symmetric encryption** — AES/Fernet encryption concepts
4. **Key derivation** — Converting passwords to encryption keys
5. **Error handling** — Try/except blocks, user-friendly error messages
6. **Frontend development** — Bootstrap responsive design
7. **Security practices** — Input validation, no password storage, secure randomness

## License

This project is for educational purposes. Feel free to use and modify it for learning.

