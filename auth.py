from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import models

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """
    Decorator to restrict access to routes that require an authenticated user session.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Authentication required. Please log in first.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration.
    Hashes password using pbkdf2:sha256 with a salt.
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validations
        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template('register.html')
            
        if len(username) < 4:
            flash("Username must be at least 4 characters long.", "danger")
            return render_template('register.html')
            
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return render_template('register.html')
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')
            
        # Check if user already exists
        existing_user = models.get_user_by_username(username)
        if existing_user:
            flash("Username is already taken.", "danger")
            return render_template('register.html')
            
        # Hash password and create user
        password_hash = generate_password_hash(password)
        try:
            models.create_user(username, password_hash)
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash("An error occurred during registration. Please try again.", "danger")
            
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user authentication.
    Verifies passwords against hashed values stored in DB.
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template('login.html')
            
        user = models.get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """
    Clears the session and redirects to the landing page.
    """
    session.clear()
    flash("You have been logged out securely.", "success")
    return redirect(url_for('index'))
