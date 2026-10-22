"""
Password hashing + JWT creation/verification.
Kept deliberately simple (no external auth provider) so the project runs
fully self-contained. Swap this module out for Clerk/Auth.js later if
you want managed auth without changing the rest of the app.
"""
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings, resolved_jwt_secret

# bcrypt 5.x is incompatible with passlib 1.7.4 on current Python builds and
# crashes before a password is even hashed. PBKDF2-SHA256 is a secure, stable
# built-in passlib scheme for this self-contained project.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
JWT_SECRET = resolved_jwt_secret()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token, JWT_SECRET, algorithms=[settings.jwt_algorithm]
        )
        return payload.get("sub")
    except JWTError:
        return None
