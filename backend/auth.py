"""
auth.py — JWT signing/verification and password hashing utilities.

Uses python-jose for JWT (HS256) and passlib[bcrypt] for password hashing.
Secret key and token lifetime are read from config.py, which in turn loads
the appropriate .env.{APP_ENV} file. Set SECRET_KEY in each environment file.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
import bcrypt

import config

# ---------------------------------------------------------------------------
# Configuration — sourced from config.py (reads .env.{APP_ENV})
# ---------------------------------------------------------------------------

SECRET_KEY: str = config.SECRET_KEY
ALGORITHM: str = "HS256"

# Role-specific lifetimes
STUDENT_TOKEN_EXPIRE_MINUTES: int = config.STUDENT_TOKEN_EXPIRE_MINUTES
INSTRUCTOR_TOKEN_EXPIRE_MINUTES: int = config.INSTRUCTOR_TOKEN_EXPIRE_MINUTES

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the plaintext password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored bcrypt hash."""
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


# ---------------------------------------------------------------------------
# JWT creation and decoding
# ---------------------------------------------------------------------------

def create_access_token(
    subject: str,
    role: str,
    expires_minutes: int | None = None,
) -> str:
    """
    Create a signed JWT.

    Parameters
    ----------
    subject : str
        The user's UUID (stored as the JWT ``sub`` claim).
    role : str
        ``'student'`` or ``'instructor'`` — stored as a custom claim.
    expires_minutes : int | None
        Override the default lifetime. Falls back to role-specific default.
    """
    if expires_minutes is None:
        expires_minutes = (
            INSTRUCTOR_TOKEN_EXPIRE_MINUTES
            if role == "instructor"
            else STUDENT_TOKEN_EXPIRE_MINUTES
        )

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {
        "sub": subject,   # user UUID
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT.

    Returns the raw payload dict on success.
    Raises ``jose.JWTError`` on invalid / expired tokens.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
