"""Anthropic Claude API provider."""
import anthropic
from typing import AsyncIterator
from app.llm.provider import LLMProvider
from app.config import settings


class ClaudeProvider(LLMProvider):
    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def chat(self, messages: list, **kwargs) -> str:
        system, msgs = _extract_system(messages)
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 4096),
            system=system,
            messages=msgs,
        )
        return response.content[0].text

    async def chat_stream(self, messages: list, **kwargs):
        system, msgs = _extract_system(messages)
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 4096),
            system=system,
            messages=msgs,
        ) as stream:
            async for text in stream.text_stream:
                yield text


def _extract_system(messages: list) -> tuple:
    """Extract system message, return (system_text, remaining_messages)."""
    system = ""
    remaining = []
    for msg in messages:
        if msg["role"] == "system":
            system = msg["content"]
        else:
            remaining.append(msg)
    return system, remaining
