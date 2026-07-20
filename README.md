# 🔐 SecureVault

SecureVault is a beginner-friendly cybersecurity web application that provides secure file encryption, decryption, and integrity verification. Built with Python, Flask, SQLite, HTML, CSS, and JavaScript, it demonstrates practical cryptography concepts and secure file management through a modern web interface.

---

## ✨ Features

### 🔒 File Encryption
- Encrypt files using AES-256 encryption
- Password-protected encryption
- Secure encrypted file storage
- Download encrypted files

### 🔓 File Decryption
- Decrypt encrypted files
- Password verification
- Secure file recovery
- Graceful handling of incorrect passwords

### 🛡️ File Integrity Verification
- Generate SHA-256 hashes
- Verify file integrity
- Detect file modifications
- Compare stored and generated hashes

### 👤 User Authentication
- User registration
- Secure login
- Password hashing
- Session management

### 📊 Dashboard
- Total encrypted files
- Total decrypted files
- Total integrity checks
- Recent user activity
- Storage statistics

### 📁 History
- View all operations
- Search records
- Delete history
- Export history (if implemented)

---

# 🛠️ Technologies Used

- Python 3
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript
- Cryptography Library
- Bootstrap (if used)

---

# 📂 Project Structure

```
SecureVault/
│
├── app.py
├── auth.py
├── encryption.py
├── hashing.py
├── database.py
├── models.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── encrypt.html
│   ├── decrypt.html
│   ├── verify.html
│   └── history.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── database.db
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/SecureVault.git
```

Open the project:

```bash
cd SecureVault
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Visit:

```
http://127.0.0.1:5000
```

---

# 🚀 How to Use

## Register
Create a user account.

## Login
Sign in securely.

## Encrypt
Upload a file and provide a password to encrypt it.

## Decrypt
Upload the encrypted file and enter the correct password to recover the original file.

## Verify Integrity
Upload a file to generate or compare its SHA-256 hash and determine whether it has been modified.

---

# 📸 Screenshots

Add screenshots in:

```
screenshots/
├── home.png
├── login.png
├── dashboard.png
├── encrypt.png
├── decrypt.png
├── verify.png
└── history.png
```

---

# 🔒 Security Features

- AES-256 File Encryption
- SHA-256 Integrity Verification
- Password Hashing
- Secure Session Management
- File Validation
- Upload Restrictions
- Error Handling

---

# 📈 Future Improvements

- Multi-user file sharing
- Email verification
- Two-factor authentication (2FA)
- Secure cloud storage
- PDF report generation
- Audit logs
- Docker deployment
- Admin dashboard
- Role-based access control
- Key management system

---

# 🎯 Learning Outcomes

This project demonstrates practical knowledge of:

- Cryptography
- File Encryption
- Hash Functions
- Authentication
- Secure File Handling
- Database Integration
- Flask Web Development
- Cybersecurity Best Practices

---

# ⚠️ Disclaimer

This project is intended for educational purposes and authorized use only. Users are responsible for complying with applicable laws and organizational policies when handling sensitive data.

---

# 👨‍💻 Author

**Aashish S**

Bachelor of Engineering (Computer Science)

Networking & Cybersecurity Enthusiast

---

# 📄 License

This project is licensed under the MIT License.