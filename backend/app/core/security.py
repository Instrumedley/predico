"""
Security utilities for authentication and authorization.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from passlib.context import CryptContext
from app.core.config import settings

# Initialize passlib context, but we'll use bcrypt directly for hashing
# to avoid passlib's backend initialization issues with long passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    # Truncate password to 72 bytes if longer (bcrypt limit)
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        truncated_bytes = password_bytes[:72]
        # Remove any incomplete UTF-8 sequences at the end
        while truncated_bytes and (truncated_bytes[-1] & 0b11000000) == 0b10000000:
            truncated_bytes = truncated_bytes[:-1]
        password_bytes = truncated_bytes
    
    # Use bcrypt directly to avoid passlib's backend initialization issues
    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password.
    
    Note: bcrypt has a 72-byte limit. Passwords longer than 72 bytes
    will be truncated, which is secure but we should warn users.
    """
    # Ensure password is a string
    if not isinstance(password, str):
        password = str(password)
    
    # Truncate password to 72 bytes if longer (bcrypt limit)
    # We need to handle UTF-8 encoding properly to avoid cutting multi-byte characters
    password_bytes = password.encode('utf-8')
    
    # Truncate to exactly 72 bytes, handling UTF-8 boundaries
    if len(password_bytes) > 72:
        # Take first 72 bytes
        truncated_bytes = password_bytes[:72]
        # Remove any incomplete UTF-8 sequences at the end
        # UTF-8 continuation bytes start with 10xxxxxx (0b10000000 mask)
        while truncated_bytes and (truncated_bytes[-1] & 0b11000000) == 0b10000000:
            truncated_bytes = truncated_bytes[:-1]
        # Use truncated bytes directly for bcrypt (bcrypt expects bytes)
        password_bytes = truncated_bytes
    else:
        # Keep as bytes for bcrypt
        password_bytes = password_bytes
    
    # Use bcrypt directly to avoid passlib's backend initialization issues
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string (passlib format compatible)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

