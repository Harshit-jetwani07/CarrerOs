import json
from typing import Protocol


class ProviderError(Exception):
    """Safe provider failure text suitable for returning to the account owner."""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


class AIProvider(Protocol):
    def chat_json(self, system_prompt: str, user_prompt: str) -> dict: ...
    def test_key(self) -> None: ...


def parse_json_response(content: str | None) -> dict:
    if not content:
        raise ProviderError("The provider returned an empty response. Please try again.")
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ProviderError("The provider returned an unreadable response. Please try again.") from exc
    if not isinstance(data, dict):
        raise ProviderError("The provider returned an unexpected response. Please try again.")
    return data


def safe_provider_reason(exc: Exception) -> ProviderError:
    response = getattr(exc, "response", None)
    status = getattr(exc, "status_code", None) or getattr(exc, "code", None) or getattr(response, "status_code", None)
    message = str(getattr(exc, "message", "") or exc).lower()
    if status in {401, 403}:
        return ProviderError("This key was rejected. Check that it is active and copied completely.")
    if status == 429:
        return ProviderError("This provider has reached a rate or daily quota limit. Wait for its reset time and check usage or billing in the provider console. Your key may still be valid.")
    if status == 404 or "model" in message and ("not found" in message or "deprecated" in message):
        return ProviderError("The configured provider model is unavailable. Update the server model setting, then restart the backend.")
    if "billing" in message or "insufficient_quota" in message or "credit" in message:
        return ProviderError("This provider account has no usable credits or billing quota. Add credits or enable the provider free tier, then retry.")
    if status and 400 <= status < 500:
        return ProviderError("The provider could not accept this request. Check the provider console, key permissions, and selected model.")
    return ProviderError("Could not reach this provider right now. Please try again shortly.")
