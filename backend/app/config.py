"""
Central app settings, loaded from environment variables / .env file.
"""
import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"

    # A development instance gets a fresh secret rather than a public default.
    # Production must supply JWT_SECRET so tokens survive restarts and cannot be
    # signed with an accidental development value.
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    database_url: str = "postgresql://careeros:careeros@localhost:5432/careeros"
    redis_url: str = "redis://localhost:6379/0"

    openai_api_key: str = ""
    ai_model: str = "gpt-4o-mini"
    gemini_model: str = "gemini-3.8-flash"
    groq_model: str = "llama-3.3-70b-versatile"
    fernet_secret_key: str = ""

    frontend_origin: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()


def resolved_jwt_secret() -> str:
    if settings.jwt_secret:
        return settings.jwt_secret
    if settings.environment.lower() in {"production", "prod"}:
        raise RuntimeError("JWT_SECRET must be set when ENVIRONMENT=production.")
    return secrets.token_urlsafe(48)
