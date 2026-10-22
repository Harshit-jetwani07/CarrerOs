from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.crypto import decrypt_key, encrypt_key
from app.database import get_db
from app.deps import get_current_user
from app.models.api_key import UserApiKey
from app.models.user import User
from app.services.providers import get_provider

router = APIRouter(prefix="/api/settings", tags=["settings"])
SUPPORTED_PROVIDERS = {"openai", "gemini", "groq"}


class ApiKeyInput(BaseModel):
    api_key: str = Field(min_length=8, max_length=512)


def _out(key: UserApiKey) -> dict:
    return {"provider": key.provider, "connected": True, "is_default": key.is_default, "last_used_at": key.last_used_at}


@router.get("/api-keys")
def list_api_keys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    keys = db.query(UserApiKey).filter(UserApiKey.user_id == current_user.id).all()
    by_provider = {item.provider: item for item in keys}
    return [{"provider": provider, "connected": provider in by_provider, "is_default": bool(by_provider.get(provider) and by_provider[provider].is_default), "last_used_at": by_provider[provider].last_used_at if provider in by_provider else None} for provider in sorted(SUPPORTED_PROVIDERS)]


@router.put("/api-keys/{provider}")
def save_api_key(provider: str, payload: ApiKeyInput, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    provider = provider.lower()
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=404, detail="That AI provider is not supported.")
    try:
        # Construct the provider locally but do not make a network call here.
        # A valid key should still be savable when the provider is temporarily
        # unavailable; the first real AI request performs the live check.
        get_provider(provider, payload.api_key.strip())
        encrypted_key = encrypt_key(payload.api_key.strip())
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Secure key storage is not configured correctly on this server.") from exc
    saved = db.query(UserApiKey).filter(UserApiKey.user_id == current_user.id, UserApiKey.provider == provider).first()
    if saved is None:
        saved = UserApiKey(user_id=current_user.id, provider=provider, encrypted_key=encrypted_key, is_default=not db.query(UserApiKey).filter(UserApiKey.user_id == current_user.id).first())
        db.add(saved)
    else:
        saved.encrypted_key = encrypted_key
    db.commit(); db.refresh(saved)
    return _out(saved)


@router.delete("/api-keys/{provider}")
def delete_api_key(provider: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = db.query(UserApiKey).filter(UserApiKey.user_id == current_user.id, UserApiKey.provider == provider.lower()).first()
    if saved is None:
        raise HTTPException(status_code=404, detail="This provider is not connected.")
    was_default = saved.is_default
    db.delete(saved); db.flush()
    if was_default:
        replacement = db.query(UserApiKey).filter(UserApiKey.user_id == current_user.id).first()
        if replacement: replacement.is_default = True
    db.commit()
    return {"provider": provider.lower(), "connected": False}


@router.post("/api-keys/{provider}/test")
def test_api_key(provider: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Make one tiny live request so Saved and Working are never confused."""
    saved = db.query(UserApiKey).filter(UserApiKey.user_id == current_user.id, UserApiKey.provider == provider.lower()).first()
    if saved is None:
        raise HTTPException(status_code=404, detail="Save this provider key before testing it.")
    try:
        get_provider(saved.provider, decrypt_key(saved.encrypted_key)).test_key()
    except Exception as exc:
        from app.services.providers.base import ProviderError
        if isinstance(exc, ProviderError):
            raise HTTPException(status_code=422, detail=exc.reason) from exc
        raise HTTPException(status_code=503, detail="Could not test this provider right now. Please try again.") from exc
    return {"provider": saved.provider, "working": True, "message": "Live provider check succeeded."}


@router.patch("/api-keys/{provider}/default")
def set_default_provider(provider: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = db.query(UserApiKey).filter(UserApiKey.user_id == current_user.id, UserApiKey.provider == provider.lower()).first()
    if saved is None:
        raise HTTPException(status_code=404, detail="Connect this provider before making it your default.")
    db.query(UserApiKey).filter(UserApiKey.user_id == current_user.id).update({UserApiKey.is_default: False})
    saved.is_default = True; db.commit(); db.refresh(saved)
    return _out(saved)
