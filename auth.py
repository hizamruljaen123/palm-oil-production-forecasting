from functools import wraps
from flask import session, redirect, url_for, flash
import mysql.connector
import hashlib

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'data_air'
}

def login_required(f):
    """Decorator untuk memastikan user sudah login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator untuk memastikan user adalah admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def verify_user(username, password):
    """Verifikasi kredensial user menggunakan MD5"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Hash input password dengan MD5
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        
        if user and user['password'] == hashed_password:
            return user
        return None
    except Exception as e:
        print(f"Error verifying user: {e}")
        return None

def create_user(username, password, role='user', full_name=''):
    """Membuat user baru dengan MD5"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Hash password dengan MD5
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO users (username, password, role, full_name)
            VALUES (%s, %s, %s, %s)
        """, (username, hashed_password, role, full_name))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
