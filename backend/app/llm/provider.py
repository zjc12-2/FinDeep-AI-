"""Unified LLM provider interface with per-agent configuration."""
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Dict
from app.config import settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def chat(self, messages: list, **kwargs) -> str:
        """Send a chat completion request and return the response text."""
        ...

    @abstractmethod
    async def chat_stream(self, messages: list, **kwargs) -> AsyncIterator[str]:
        """Send a chat completion request and stream response chunks."""
        ...


def _resolve_agent_config(agent_name: str) -> tuple:
    """Resolve provider and model for a specific agent.
    Falls back to global config if agent-specific config is not set.
    """
    agent_provider_map = {
        "bull": (settings.bull_agent_provider, settings.bull_agent_model),
        "bear": (settings.bear_agent_provider, settings.bear_agent_model),
        "factcheck": (settings.factcheck_agent_provider, settings.factcheck_agent_model),
        "synthesizer": (settings.synthesizer_agent_provider, settings.synthesizer_agent_model),
    }

    agent_provider, agent_model = agent_provider_map.get(
        agent_name, (None, None)
    )
    provider_name = agent_provider or settings.llm_provider
    model_name = agent_model or settings.llm_model
    return provider_name, model_name


def get_llm(agent_name: str = "default") -> LLMProvider:
    """Factory: return the configured LLM provider for the given agent."""
    provider_name, model_name = _resolve_agent_config(agent_name)

    if provider_name == "claude":
        from app.llm.providers.claude import ClaudeProvider
        return ClaudeProvider(model=model_name)
    elif provider_name == "openai":
        from app.llm.providers.openai_provider import OpenAIProvider
        return OpenAIProvider(model=model_name)
    elif provider_name == "deepseek":
        from app.llm.providers.deepseek import DeepSeekProvider
        return DeepSeekProvider(model=model_name)
    elif provider_name == "openai_compatible":
        from app.llm.providers.openai_compatible import OpenAICompatibleProvider
        return OpenAICompatibleProvider(model=model_name)
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
