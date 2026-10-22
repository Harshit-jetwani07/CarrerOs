"""Current Gemini SDK integration (the old google-generativeai SDK is retired)."""
import json

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

from app.config import settings
from app.services.providers.base import ProviderError, parse_json_response, safe_provider_reason


class GeminiProvider:
    def __init__(self, api_key: str):
        if genai is None or types is None:
            raise ProviderError("Current Gemini support is not installed on this server yet.")
        self.client = genai.Client(api_key=api_key)

    def chat_json(self, system_prompt: str, user_prompt: str) -> dict:
        try:
            response = self.client.models.generate_content(
                model=settings.gemini_model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3,
                    response_mime_type="application/json",
                ),
            )
            return parse_json_response(response.text)
        except ProviderError:
            raise
        except Exception as exc:
            raise safe_provider_reason(exc) from exc

    def test_key(self) -> None:
        self.chat_json("Return only JSON.", json.dumps({"ok": True}))
