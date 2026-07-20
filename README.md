# SecureVault 🛡️

SecureVault is a professional, high-performance cybersecurity web application that securely encrypts, decrypts, and verifies file integrity using modern cryptographic standards. Built using **Python (Flask)**, **SQLite**, **HTML5**, **CSS3 (Vanilla)**, and **JavaScript**.

---

## 🌟 Key Features

1. **User Authentication**: Secure register, login, and logout portals. Passwords are encrypted on register using secure hashing algorithms (PBKDF2 with SHA-256 salt iterations).
2. **AES-256 File Encryption**: Encrypt any uploaded file up to 50MB. A unique 16-byte salt and Initialization Vector (IV) are generated for each operation. Encryption keys are derived using PBKDF2-HMAC-SHA256 with 100,000 iterations.
3. **Zero-Trust Decryption**: Decrypt downloaded files by uploading them and inputting the matching password. Decryption occurs purely in volatile RAM, and the decrypted stream is piped directly to your web browser as a download attachment (never written to the server's disk).
4. **SHA-256 Integrity Verification**: 
   - **Register baseline**: Upload a file to lock its reference hash signature.
   - **Check integrity**: Upload a file later to compare its signature. The system will flash a green **File Verified (Intact)** alert or a blinking red **File Modified (Changed)** warning.
5. **Interactive Dashboard**: Track metrics including total encrypted files, decrypted files, integrity checks, storage allocation progress indicators, and real-time recent actions feeds.
6. **Detailed Audit Trails**: Maintain complete logs of operations, original file names, sizes, dates, and SHA-256 hash signatures. Search logs, delete records, or export the history as a CSV spreadsheet.
7. **Modern Cybersecurity UI**: Sleek obsidian dark theme featuring interactive glassmorphic panels, neon state colors (cyan, matrix-green, hot-pink), upload drag-and-drop dropzones, and dynamic progress bar animations.

---

## 📂 Project Directory Structure

```text
SecureVault/
│
├── static/
│   ├── css/
│   │   └── style.css            # Dark theme styles (glassmorphism, alerts, neon glows)
│   └── js/
│       └── main.js             # Drag-and-drop bindings, AJAX uploads & progress bars
│
├── templates/
│   ├── base.html                # Master layout (sidebar, alerts, assets setup)
│   ├── index.html               # Features overview and landing screen
│   ├── login.html               # Agent access portal
│   ├── register.html            # Operative registry card
│   ├── dashboard.html           # Live control panel, storage bar, recent events
│   ├── encrypt.html             # Encryption panel (AES-256) and download links
│   ├── decrypt.html             # Decryption panel (in-memory bytes processing)
│   ├── verify.html              # SHA-256 baseline database and integrity checker
│   └── history.html             # Audit log table, filters, CSV exporter, delete hooks
│
├── uploads/                     # Server storage directory for encrypted files
│                                # (Files saved securely as <history_id>.enc)
│
├── app.py                       # Main Flask routing engine and upload configuration
├── auth.py                      # Flask Blueprints and session authentication
├── encryption.py                # AES-256-CBC and PBKDF2HMAC cryptographic routines
├── hashing.py                   # SHA-256 hash generator and verification rules
├── database.py                  # SQLite connection factory & tables schema builder
├── models.py                    # Database query commands (User, History, Integrity)
├── requirements.txt             # Python dependency packages
└── README.md                    # Main product guide documentation
```

---

## 🚀 Getting Started

### 📋 Prerequisites
Ensure you have **Python 3.7+** installed. You can check your version using:
```bash
python --version
```

### 1️⃣ Install Dependencies
Navigate to the project root directory and install dependencies:
```bash
pip install -r requirements.txt
```

### 2️⃣ Run the Application
Start the Flask local development server:
```bash
python app.py
```

### 3️⃣ Access Web Portal
Open your web browser and navigate to:
```text
http://127.0.0.1:5000/
```

---

## 🔒 Cryptographic Implementation Notes

### 🛠️ Key Derivation & AES Encryption
Each file is encrypted with a distinct key, preventing key reuse attacks:
1. When a file is uploaded, a random **16-byte Salt** and a random **16-byte Initialization Vector (IV)** are generated using `os.urandom(16)`.
2. A 256-bit AES key is derived from the user-entered password and the salt using **PBKDF2HMAC** with **SHA-256** and **100,000 iterations**.
3. Plaintext file bytes are padded using **PKCS7** block padding.
4. The data is encrypted using **AES-256-CBC** mode.
5. The final encrypted file output layout is: `[16-byte Salt] + [16-byte IV] + [Ciphertext]`.

### 🔓 Decryption & Padding Check
1. The salt and IV are parsed from the header (first 32 bytes).
2. The key is derived using the user-supplied password and the extracted salt.
3. The ciphertext is decrypted using the derived key and IV under AES-256-CBC.
4. Unpadding is performed. If the password is wrong, PKCS7 padding verification will throw an error, which the backend catches to safely report `"Decryption failed. Invalid password or corrupted payload."`

---

## 🛡️ Web Security Safeguards

- **No Plaintext Key Storage**: Encryption keys are calculated in-memory and discarded. Passwords are never sent to or saved on the server.
- **Path Traversal Shield**: Filenames are strictly sanitized using `werkzeug.utils.secure_filename` to prevent directory escape attacks.
- **Upload File Limits**: File uploads are restricted to a maximum size of 50MB by configuring `MAX_CONTENT_LENGTH`.
- **Protected Downloads**: Downloads of server-stored encrypted files check the authenticated session `user_id` to prevent unauthorized file access.
- **Database Injection Safeguards**: All database queries are executed using parameterized SQL statements in `sqlite3` to prevent SQL Injection.
