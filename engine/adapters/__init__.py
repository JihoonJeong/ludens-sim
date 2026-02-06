"""LLM Adapters"""

from .base import BaseLLMAdapter, LLMResponse
from .mock import MockAdapter
from .ollama import OllamaAdapter
from .anthropic import AnthropicAdapter
from .google import GoogleAdapter

ADAPTER_REGISTRY = {
    "mock": MockAdapter,
    "ollama": OllamaAdapter,
    "anthropic": AnthropicAdapter,
    "google": GoogleAdapter,
}


def create_adapter(adapter_type: str, **kwargs) -> BaseLLMAdapter:
    adapter_class = ADAPTER_REGISTRY.get(adapter_type.lower())
    if adapter_class is None:
        raise ValueError(
            f"Unknown adapter type: {adapter_type}. "
            f"Available: {list(ADAPTER_REGISTRY.keys())}"
        )
    return adapter_class(**kwargs)


__all__ = [
    "BaseLLMAdapter",
    "LLMResponse",
    "MockAdapter",
    "OllamaAdapter",
    "AnthropicAdapter",
    "GoogleAdapter",
    "ADAPTER_REGISTRY",
    "create_adapter",
]
