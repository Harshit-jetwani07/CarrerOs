try:
    from groq import Groq
except ImportError:  # App still boots for users who do not use this provider.
    Groq = None

from app.services.providers.base import ProviderError, parse_json_response, safe_provider_reason
from app.config import settings


class GroqProvider:
    def __init__(self, api_key: str):
        if Groq is None:
            raise ProviderError("Groq support is not installed on this server yet.")
        self.client = Groq(api_key=api_key)

    def chat_json(self, system_prompt: str, user_prompt: str) -> dict:
        try:
            response = self.client.chat.completions.create(
                model=settings.groq_model, response_format={"type": "json_object"}, temperature=0.3,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            )
            return parse_json_response(response.choices[0].message.content)
        except ProviderError:
            raise
        except Exception as exc:
            raise safe_provider_reason(exc) from exc

    def test_key(self) -> None:
        self.chat_json("Return only JSON.", '{"ok": true}')
