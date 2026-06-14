"""DeepSeek API provider (OpenAI-compatible)."""
from app.llm.providers.openai_provider import OpenAIProvider
from app.config import settings


class DeepSeekProvider(OpenAIProvider):
    def __init__(self, model: str = "deepseek-chat"):
        super().__init__(model=model)
        self.api_key = settings.deepseek_api_key or settings.openai_api_key
        self.base_url = "https://api.deepseek.com/v1"
