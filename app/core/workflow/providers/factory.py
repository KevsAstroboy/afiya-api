from core.config import settings
from core.workflow.providers.base import LLMProvider


class LLMProviderFactory:
    @staticmethod
    def create() -> LLMProvider:
        provider = settings.LLM_PROVIDER
        if provider == "anthropic":
            from core.workflow.providers.anthropic import AnthropicProvider
            return AnthropicProvider()
        elif provider == "openai":
            from core.workflow.providers.openai import OpenAIProvider
            return OpenAIProvider()
        elif provider == "bedrock":
            from core.workflow.providers.bedrock import BedrockAnthropicProvider
            return BedrockAnthropicProvider()
        else:
            raise ValueError(f"LLM provider '{provider}' non supporte. Utilisez 'anthropic', 'openai' ou 'bedrock'.")
