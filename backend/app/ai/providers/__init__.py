import os

from dotenv import load_dotenv

from app.ai.providers.base import LLMProvider, ProviderConfigurationError


load_dotenv()


def get_provider(provider_name: str | None = None) -> LLMProvider:
    name = provider_name if provider_name is not None else os.getenv("LLM_PROVIDER")
    if not name or not name.strip():
        raise ProviderConfigurationError("Missing LLM_PROVIDER; set it to 'nebius' or 'gemini'")

    name = name.strip().lower()
    if name == "nebius":
        from app.ai.providers.nebius import NebiusProvider

        return NebiusProvider()
    if name == "gemini":
        from app.ai.providers.gemini import GeminiProvider

        return GeminiProvider()
    raise ProviderConfigurationError(f"Unsupported LLM_PROVIDER: {name}")
