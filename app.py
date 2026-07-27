"""
app.py - Main Flask application for Secure File Encryption & Decryption Tool.

This is the entry point of the application. It handles:
- Serving the web interface
- Processing file uploads
- Routing encryption/decryption requests
- Sending encrypted/decrypted files back to the user

Beginner Notes:
- Flask is a lightweight web framework for Python.
- Routes (@app.route) define what happens when a user visits a URL.
- We use POST method for file uploads (sending data to the server).
- flash() displays one-time messages to the user (success/error alerts).
"""

import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from encryption import encrypt_file, decrypt_file

# ============================================================
# APP CONFIGURATION
# ============================================================

# Create the Flask application instance
app = Flask(__name__)

# Secret key for session management and flash messages
# In production, use a proper secret key from environment variables
app.secret_key = os.urandom(24)

# Define folder paths for file storage
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ENCRYPTED_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'encrypted')
DECRYPTED_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'decrypted')

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'png', 'jpg', 'jpeg', 'csv', 'xlsx'}

# Maximum file size: 16 MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ============================================================
# HELPER FUNCTIONS
# ============================================================


def create_folders():
    for folder in [UPLOAD_FOLDER, ENCRYPTED_FOLDER, DECRYPTED_FOLDER]:
        os.makedirs(folder, exist_ok=True)

create_folders()


def allowed_file(filename: str) -> bool:
    """
    Check if the uploaded file has an allowed extension.

    Args:
        filename: Name of the uploaded file

    Returns:
        True if the file extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_file(filepath: str):
    """
    Remove a temporary file after it's no longer needed.

    Args:
        filepath: Path to the file to delete
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except OSError as e:
        print(f"Error cleaning up file {filepath}: {e}")


# ============================================================
# ROUTES
# ============================================================


@app.route('/')
def index():
    """
    Home page route - displays the main encryption/decryption interface.
    """
    return render_template('index.html')


@app.route('/encrypt', methods=['POST'])
def encrypt():
    """
    Encryption route - handles file encryption requests.

    Flow:
    1. Validate that a file was uploaded
    2. Validate that a password was provided
    3. Save the uploaded file temporarily
    4. Encrypt the file with the provided password
    5. Send the encrypted file to the user for download
    6. Clean up temporary files
    """
    # --- Validation ---

    # Check if a file was included in the request
    if 'file' not in request.files:
        flash('No file selected. Please choose a file to encrypt.', 'danger')
        return redirect(url_for('index'))

    file = request.files['file']

    # Check if the user actually selected a file (not just an empty field)
    if file.filename == '':
        flash('No file selected. Please choose a file to encrypt.', 'danger')
        return redirect(url_for('index'))

    # Check if the file type is allowed
    if not allowed_file(file.filename):
        flash('File type not supported. Allowed: txt, pdf, docx, png, jpg, csv, xlsx.', 'danger')
        return redirect(url_for('index'))

    # Get the password from the form
    password = request.form.get('password', '').strip()

    # Validate password is not empty
    if not password:
        flash('Password is required for encryption.', 'danger')
        return redirect(url_for('index'))

    # Validate minimum password length
    if len(password) < 4:
        flash('Password must be at least 4 characters long.', 'danger')
        return redirect(url_for('index'))

    # --- File Processing ---

    try:
        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)

        # Save the uploaded file temporarily
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(upload_path)

        # Define the output path for the encrypted file
        encrypted_filename = f"encrypted_{filename}"
        encrypted_path = os.path.join(ENCRYPTED_FOLDER, encrypted_filename)

        # Perform encryption
        success = encrypt_file(upload_path, encrypted_path, password)

        if success:
            # Clean up the original uploaded file (we don't need it anymore)
            cleanup_file(upload_path)

            # Send the encrypted file to the user for download
            return send_file(
                encrypted_path,
                as_attachment=True,
                download_name=encrypted_filename
            )
        else:
            # Clean up on failure
            cleanup_file(upload_path)
            flash('Encryption failed. Please try again.', 'danger')
            return redirect(url_for('index'))

    except Exception as e:
        # Handle any unexpected errors
        flash(f'An error occurred during encryption: {str(e)}', 'danger')
        return redirect(url_for('index'))


@app.route('/decrypt', methods=['POST'])
def decrypt():
    """
    Decryption route - handles file decryption requests.

    Flow:
    1. Validate that a file was uploaded
    2. Validate that a password was provided
    3. Save the uploaded encrypted file temporarily
    4. Decrypt the file with the provided password
    5. Send the decrypted file to the user for download
    6. Clean up temporary files
    """
    # --- Validation ---

    # Check if a file was included in the request
    if 'file' not in request.files:
        flash('No file selected. Please choose a file to decrypt.', 'danger')
        return redirect(url_for('index'))

    file = request.files['file']

    # Check if the user actually selected a file
    if file.filename == '':
        flash('No file selected. Please choose a file to decrypt.', 'danger')
        return redirect(url_for('index'))

    # Get the password from the form
    password = request.form.get('password', '').strip()

    # Validate password is not empty
    if not password:
        flash('Password is required for decryption.', 'danger')
        return redirect(url_for('index'))

    # --- File Processing ---

    try:
        # Secure the filename
        filename = secure_filename(file.filename)

        # Save the uploaded encrypted file temporarily
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(upload_path)

        # Define the output path for the decrypted file
        # Remove "encrypted_" prefix if present to restore original name
        if filename.startswith('encrypted_'):
            decrypted_filename = filename[len('encrypted_'):]
        else:
            decrypted_filename = f"decrypted_{filename}"

        decrypted_path = os.path.join(DECRYPTED_FOLDER, decrypted_filename)

        # Perform decryption
        success = decrypt_file(upload_path, decrypted_path, password)

        if success:
            # Clean up the uploaded encrypted file
            cleanup_file(upload_path)

            # Send the decrypted file to the user for download
            return send_file(
                decrypted_path,
                as_attachment=True,
                download_name=decrypted_filename
            )
        else:
            # Clean up on failure
            cleanup_file(upload_path)
            flash('Decryption failed. Wrong password or corrupted file.', 'danger')
            return redirect(url_for('index'))

    except Exception as e:
        # Handle any unexpected errors
        flash(f'An error occurred during decryption: {str(e)}', 'danger')
        return redirect(url_for('index'))


# ============================================================
# APP STARTUP
# ============================================================

if __name__ == '__main__':
    print("=" * 50)
    print("  Secure File Encryption & Decryption Tool")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 50)

    app.run(
        debug=False,
        use_reloader=False,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )