"""Encryption helpers for user-owned provider credentials.

The secret is environment-owned: it is deliberately never generated or stored
in source code, logs, or database rows.
"""
from cryptography.fernet import Fernet, InvalidToken

from app.config import settings


def _fernet() -> Fernet:
    if not settings.fernet_secret_key:
        raise RuntimeError("Secure key storage has not been configured yet.")
    try:
        return Fernet(settings.fernet_secret_key.encode())
    except (ValueError, TypeError) as exc:
        raise RuntimeError("Secure key storage has not been configured correctly.") from exc


def encrypt_key(raw: str) -> str:
    return _fernet().encrypt(raw.encode()).decode()


def decrypt_key(token: str) -> str:
    try:
        return _fernet().decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise RuntimeError("The saved provider key can no longer be read securely.") from exc
