"""Browser credential checks shared by the web server and privileged helper."""
import hashlib
import hmac
import secrets


def validate_password(password):
    if not isinstance(password, str) or not 1 <= len(password) <= 128:
        raise ValueError('Choose a password from 1 to 128 characters')
    if any(ord(c) < 32 or ord(c) == 127 for c in password):
        raise ValueError('Password cannot contain control characters')
    return password


def matches(password, auth):
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(auth['salt']), 200000).hex()
    return hmac.compare_digest(digest, auth['hash'])


def password_record(password):
    validate_password(password)
    salt = secrets.token_hex(16)
    return {'salt': salt, 'hash': hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 200000).hex()}
