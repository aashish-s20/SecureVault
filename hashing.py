import hashlib
import models

def calculate_sha256(data_bytes: bytes) -> str:
    """
    Calculates the SHA-256 hash of a byte string and returns the hex digest.
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data_bytes)
    return sha256_hash.hexdigest()

def register_file_hash(user_id: int, filename: str, data_bytes: bytes) -> str:
    """
    Computes SHA-256 and saves it as the reference hash for the given filename.
    """
    sha256 = calculate_sha256(data_bytes)
    models.add_integrity_hash(user_id, filename, sha256)
    # Log the action in file history
    models.add_history_entry(user_id, filename, len(data_bytes), sha256, 'REGISTER_HASH')
    return sha256

def verify_file_hash(user_id: int, filename: str, data_bytes: bytes) -> dict:
    """
    Calculates SHA-256 and compares it against the stored reference hash.
    Logs success or modification in history.
    """
    current_hash = calculate_sha256(data_bytes)
    record = models.get_integrity_hash(user_id, filename)
    
    if not record:
        return {
            'status': 'not_found',
            'reference_hash': None,
            'current_hash': current_hash
        }
        
    reference_hash = record['sha256_hash']
    if current_hash == reference_hash:
        models.add_history_entry(user_id, filename, len(data_bytes), current_hash, 'VERIFY_SUCCESS')
        return {
            'status': 'verified',
            'reference_hash': reference_hash,
            'current_hash': current_hash
        }
    else:
        models.add_history_entry(user_id, filename, len(data_bytes), current_hash, 'VERIFY_FAIL')
        return {
            'status': 'modified',
            'reference_hash': reference_hash,
            'current_hash': current_hash
        }
