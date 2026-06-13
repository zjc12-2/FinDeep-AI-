"""Generic OpenAI-compatible API provider with custom base URL."""
from app.llm.providers.openai_provider import OpenAIProvider
from app.config import settings


class OpenAICompatibleProvider(OpenAIProvider):
    def __init__(self, model: str = None):
        super().__init__(model=model or settings.llm_model)
        self.base_url = settings.openai_base_url or "http://localhost:11434/v1"
