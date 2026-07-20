import os
import csv
from io import BytesIO, StringIO
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, abort
from werkzeug.utils import secure_filename

import database
import models
import encryption
import hashing
from auth import auth_bp, login_required

app = Flask(__name__)
# Secure key for session sign-off. In production, this should be a stable, secret environment variable.
app.secret_key = os.environ.get('SECRET_KEY', 'securevault_super_secret_cyber_key_9981')

# Limit uploads to 50MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Setup upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

# Initialize DB on start
database.init_db()

def allowed_file(filename):
    """
    Ensures the file is valid and contains an extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() != ''

@app.errorhandler(413)
def request_entity_too_large(error):
    """
    Handles payload too large errors gracefully.
    """
    flash("File is too large. Maximum allowed size is 50MB.", "danger")
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/')
def index():
    """
    Landing page redirecting to dashboard if already logged in.
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Aggregates stats and displays user dashboard.
    """
    user_id = session['user_id']
    stats = models.get_dashboard_stats(user_id)
    return render_template('dashboard.html', stats=stats)

@app.route('/encrypt', methods=['GET', 'POST'])
@login_required
def encrypt():
    """
    Accepts file and password, encrypts using AES-256, and stores it in uploads/
    named after the history record ID. Displays encryption success screen.
    """
    if request.method == 'POST':
        # Check if file is in request
        if 'file' not in request.files:
            flash("No file part selected.", "danger")
            return redirect(request.url)
            
        file = request.files['file']
        password = request.form.get('password', '')
        
        if file.filename == '':
            flash("No file selected.", "danger")
            return redirect(request.url)
            
        if not password:
            flash("Encryption password is required.", "danger")
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            orig_filename = secure_filename(file.filename)
            file_bytes = file.read()
            file_size = len(file_bytes)
            
            if file_size == 0:
                flash("Empty files cannot be encrypted.", "danger")
                return redirect(request.url)
                
            try:
                # 1. Hashing original file for verification history
                sha256_hash = hashing.calculate_sha256(file_bytes)
                
                # 2. AES-256 encryption
                encrypted_bytes = encryption.encrypt_data(file_bytes, password)
                
                # 3. Create database history record
                # We store the encrypted filename in the logs
                enc_filename = f"{orig_filename}.enc"
                history_id = models.add_history_entry(
                    user_id=session['user_id'],
                    filename=enc_filename,
                    file_size=file_size,
                    sha256_hash=sha256_hash,
                    operation='ENCRYPT'
                )
                
                # 4. Save the encrypted file named by history ID
                dest_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{history_id}.enc")
                with open(dest_path, 'wb') as f:
                    f.write(encrypted_bytes)
                    
                # Store dynamic context for the success view
                success_data = {
                    'history_id': history_id,
                    'orig_filename': orig_filename,
                    'enc_filename': enc_filename,
                    'file_size': file_size,
                    'sha256': sha256_hash
                }
                flash("File encrypted and stored securely!", "success")
                return render_template('encrypt.html', success_data=success_data)
                
            except Exception as e:
                flash(f"Encryption failed: {str(e)}", "danger")
                return redirect(request.url)
        else:
            flash("Invalid file format.", "danger")
            return redirect(request.url)
            
    return render_template('encrypt.html')

@app.route('/decrypt', methods=['GET', 'POST'])
@login_required
def decrypt():
    """
    Accepts an encrypted file and password. Decrypts file in-memory
    and streams download back to user. Avoids writing plaintext back to disk.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part selected.", "danger")
            return redirect(request.url)
            
        file = request.files['file']
        password = request.form.get('password', '')
        
        if file.filename == '':
            flash("No file selected.", "danger")
            return redirect(request.url)
            
        if not password:
            flash("Decryption password is required.", "danger")
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            encrypted_bytes = file.read()
            
            try:
                # 1. AES-256 decryption
                decrypted_bytes = encryption.decrypt_data(encrypted_bytes, password)
                
                # Determine download name
                download_name = filename
                if filename.lower().endswith('.enc'):
                    download_name = filename[:-4] # strip .enc
                else:
                    download_name = f"decrypted_{filename}"
                    
                # 2. Hashing decrypted output for auditing
                decrypted_sha256 = hashing.calculate_sha256(decrypted_bytes)
                
                # 3. Log audit action in history
                models.add_history_entry(
                    user_id=session['user_id'],
                    filename=download_name,
                    file_size=len(decrypted_bytes),
                    sha256_hash=decrypted_sha256,
                    operation='DECRYPT'
                )
                
                # 4. Stream decrypted file directly to browser
                return send_file(
                    BytesIO(decrypted_bytes),
                    as_attachment=True,
                    download_name=download_name
                )
                
            except ValueError as ve:
                flash(str(ve), "danger")
                return redirect(request.url)
            except Exception as e:
                flash(f"Decryption failed: {str(e)}", "danger")
                return redirect(request.url)
        else:
            flash("Invalid file format.", "danger")
            return redirect(request.url)
            
    return render_template('decrypt.html')

@app.route('/verify', methods=['GET', 'POST'])
@login_required
def verify():
    """
    Integrity checker route. Allows registering a reference SHA-256 hash
    or uploading a file to verify its state against SQLite stored records.
    """
    user_id = session['user_id']
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if 'file' not in request.files:
            flash("No file part selected.", "danger")
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash("No file selected.", "danger")
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_bytes = file.read()
            
            if action == 'register':
                try:
                    sha256 = hashing.register_file_hash(user_id, filename, file_bytes)
                    flash(f"SHA-256 Reference registered successfully for {filename}.", "success")
                    # Return to page showing update
                    return redirect(url_for('verify'))
                except Exception as e:
                    flash(f"Registration failed: {str(e)}", "danger")
                    
            elif action == 'verify':
                try:
                    result = hashing.verify_file_hash(user_id, filename, file_bytes)
                    # result contains status, reference_hash, current_hash
                    return render_template('verify.html', result=result, checked_filename=filename)
                except Exception as e:
                    flash(f"Verification failed: {str(e)}", "danger")
            else:
                flash("Invalid action specified.", "danger")
        else:
            flash("Invalid file format.", "danger")
            
    # Fetch registered integrity files for reference list
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT filename, sha256_hash, created_at FROM integrity_hashes WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    registered_files = cursor.fetchall()
    conn.close()
    
    return render_template('verify.html', registered_files=registered_files)

@app.route('/history')
@login_required
def history():
    """
    Displays file history records. Supports text search filter.
    """
    user_id = session['user_id']
    search_query = request.args.get('search', '').strip()
    history_records = models.get_history_by_user(user_id, search_query)
    return render_template('history.html', history=history_records, search_query=search_query)

@app.route('/history/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_history(entry_id):
    """
    Deletes a history record and deletes its corresponding server-stored encrypted file.
    """
    user_id = session['user_id']
    
    # 1. Fetch file history record to verify ownership
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM file_history WHERE id = ? AND user_id = ?", (entry_id, user_id))
    record = cursor.fetchone()
    conn.close()
    
    if not record:
        flash("Record not found or access denied.", "danger")
        return redirect(url_for('history'))
        
    # 2. Remove physical encrypted file if operation was ENCRYPT
    if record['operation'] == 'ENCRYPT':
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{entry_id}.enc")
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                # Log system error but proceed to clean DB record
                print(f"Error removing physical file {filepath}: {str(e)}")
                
    # Also delete integrity hashes if it matches this filename (optional convenience)
    models.delete_integrity_hash(user_id, record['filename'])
                
    # 3. Delete database record
    models.delete_history_entry(user_id, entry_id)
    flash("Record and associated server file removed.", "success")
    return redirect(url_for('history'))

@app.route('/history/export')
@login_required
def export_history():
    """
    Generates a CSV export of user's file operations and history.
    """
    user_id = session['user_id']
    records = models.get_history_by_user(user_id)
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ID', 'File Name', 'File Size (Bytes)', 'SHA-256 Hash', 'Operation', 'Timestamp'])
    
    # Rows
    for r in records:
        writer.writerow([
            r['id'],
            r['filename'],
            r['file_size'],
            r['sha256_hash'],
            r['operation'],
            r['timestamp']
        ])
        
    output.seek(0)
    
    return send_file(
        BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='securevault_history_export.csv'
    )

@app.route('/download/<int:history_id>')
@login_required
def download_file(history_id):
    """
    Allows downloading an encrypted file stored on the server.
    Validates user ownership before serving.
    """
    user_id = session['user_id']
    
    # Fetch database record
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM file_history WHERE id = ? AND user_id = ?", (history_id, user_id))
    record = cursor.fetchone()
    conn.close()
    
    if not record:
        abort(403, "Access denied or record does not exist.")
        
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{history_id}.enc")
    
    if not os.path.exists(filepath):
        flash("The physical file could not be found on the server storage.", "danger")
        return redirect(url_for('history'))
        
    return send_file(
        filepath,
        as_attachment=True,
        download_name=record['filename']
    )

if __name__ == '__main__':
    # Default local dev port
    app.run(debug=True, host='127.0.0.1', port=5000)
