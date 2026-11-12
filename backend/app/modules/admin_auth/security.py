import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

PASSWORD_HASHER = PasswordHasher()
DUMMY_HASH = PASSWORD_HASHER.hash(secrets.token_urlsafe(32))
SESSION_LIFETIME = timedelta(days=7)
COOKIE_PATH = "/api/v1/admin"


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def verify_password(encoded: str, password: str) -> bool:
    try:
        return PASSWORD_HASHER.verify(encoded, password)
    except (VerificationError, InvalidHashError):
        return False
