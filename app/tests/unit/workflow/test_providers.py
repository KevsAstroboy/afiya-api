import pytest
from core.workflow.providers.base import LLMProvider
from core.workflow.providers.factory import LLMProviderFactory


class TestLLMProviderFactory:
    def test_llm_provider_abc(self):
        assert hasattr(LLMProvider, "generate")

    def test_factory_has_create_method(self):
        assert hasattr(LLMProviderFactory, "create")
        assert callable(LLMProviderFactory.create)
