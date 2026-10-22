from app.services.providers.base import AIProvider, ProviderError
from app.services.providers.gemini_provider import GeminiProvider
from app.services.providers.groq_provider import GroqProvider
from app.services.providers.openai_provider import OpenAIProvider

PROVIDER_CLASSES = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "groq": GroqProvider,
}


def get_provider(name: str, api_key: str) -> AIProvider:
    provider = PROVIDER_CLASSES.get(name)
    if provider is None:
        raise ProviderError("That AI provider is not supported.")
    return provider(api_key)
