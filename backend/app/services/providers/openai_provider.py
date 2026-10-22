from openai import OpenAI

from app.config import settings
from app.services.providers.base import ProviderError, parse_json_response, safe_provider_reason


class OpenAIProvider:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def chat_json(self, system_prompt: str, user_prompt: str) -> dict:
        try:
            response = self.client.chat.completions.create(
                model=settings.ai_model, response_format={"type": "json_object"}, temperature=0.3,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            )
            return parse_json_response(response.choices[0].message.content)
        except ProviderError:
            raise
        except Exception as exc:
            raise safe_provider_reason(exc) from exc

    def test_key(self) -> None:
        self.chat_json("Return only JSON.", '{"ok": true}')
