from database import get_db_connection

def create_user(username, password_hash):
    """
    Inserts a new user into the database.
    Returns the user ID of the newly created user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_user_by_username(username):
    """
    Retrieves a user record by username.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_user_by_id(user_id):
    """
    Retrieves a user record by user ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

# File History Audit Log Operations
def add_history_entry(user_id, filename, file_size, sha256_hash, operation):
    """
    Inserts an audit log entry for a file operation.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO file_history (user_id, filename, file_size, sha256_hash, operation)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, filename, file_size, sha256_hash, operation)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_history_by_user(user_id, search_query=None):
    """
    Retrieves file operation history for a specific user.
    Supports optional case-insensitive search by file name or operation.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    if search_query:
        # SQLite LIKE is case-insensitive for ASCII characters
        q = f"%{search_query}%"
        cursor.execute(
            """
            SELECT * FROM file_history 
            WHERE user_id = ? AND (filename LIKE ? OR operation LIKE ? OR sha256_hash LIKE ?)
            ORDER BY timestamp DESC
            """,
            (user_id, q, q, q)
        )
    else:
        cursor.execute(
            "SELECT * FROM file_history WHERE user_id = ? ORDER BY timestamp DESC",
            (user_id,)
        )
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_history_entry(user_id, entry_id):
    """
    Deletes a history record by its ID, ensuring it belongs to the user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM file_history WHERE id = ? AND user_id = ?",
            (entry_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Integrity Hashes operations
def add_integrity_hash(user_id, filename, sha256_hash):
    """
    Saves or replaces the integrity SHA-256 hash reference for a file name.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT OR REPLACE INTO integrity_hashes (user_id, filename, sha256_hash)
            VALUES (?, ?, ?)
            """,
            (user_id, filename, sha256_hash)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_integrity_hash(user_id, filename):
    """
    Retrieves the registered integrity SHA-256 hash reference for a filename.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM integrity_hashes WHERE user_id = ? AND filename = ?",
        (user_id, filename)
    )
    row = cursor.fetchone()
    conn.close()
    return row

def delete_integrity_hash(user_id, filename):
    """
    Deletes an integrity reference from the registry.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM integrity_hashes WHERE user_id = ? AND filename = ?",
            (user_id, filename)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Dashboard Stats Aggregation
def get_dashboard_stats(user_id):
    """
    Aggregates dashboard stats for the user:
    - total_encrypted
    - total_decrypted
    - total_integrity_checks
    - recent_activity (last 5 history items)
    - storage_stats (sum of bytes encrypted, number of unique files)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Total encrypted
    cursor.execute(
        "SELECT COUNT(*) FROM file_history WHERE user_id = ? AND operation = 'ENCRYPT'",
        (user_id,)
    )
    total_encrypted = cursor.fetchone()[0]
    
    # 2. Total decrypted
    cursor.execute(
        "SELECT COUNT(*) FROM file_history WHERE user_id = ? AND operation = 'DECRYPT'",
        (user_id,)
    )
    total_decrypted = cursor.fetchone()[0]
    
    # 3. Total integrity checks (VERIFY_SUCCESS or VERIFY_FAIL)
    cursor.execute(
        "SELECT COUNT(*) FROM file_history WHERE user_id = ? AND operation LIKE 'VERIFY%'",
        (user_id,)
    )
    total_integrity_checks = cursor.fetchone()[0]
    
    # 4. Storage size from history (sum size of all files encrypted by user)
    cursor.execute(
        "SELECT SUM(file_size) FROM file_history WHERE user_id = ? AND operation = 'ENCRYPT'",
        (user_id,)
    )
    storage_bytes = cursor.fetchone()[0] or 0
    
    # 5. Recent activity (last 5 rows)
    cursor.execute(
        "SELECT * FROM file_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5",
        (user_id,)
    )
    recent_rows = cursor.fetchall()
    
    # Format recent activity rows
    recent_activity = []
    for r in recent_rows:
        recent_activity.append({
            'id': r['id'],
            'filename': r['filename'],
            'file_size': r['file_size'],
            'sha256_hash': r['sha256_hash'],
            'operation': r['operation'],
            'timestamp': r['timestamp']
        })
        
    conn.close()
    
    return {
        'total_encrypted': total_encrypted,
        'total_decrypted': total_decrypted,
        'total_integrity_checks': total_integrity_checks,
        'storage_bytes': storage_bytes,
        'recent_activity': recent_activity
    }
