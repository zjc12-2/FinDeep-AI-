"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # LLM通用配置
    llm_provider: str = "claude"
    llm_model: str = "claude-sonnet-4-6"

    # 按Agent独立配置
    bull_agent_provider: Optional[str] = None
    bull_agent_model: Optional[str] = None
    bear_agent_provider: Optional[str] = None
    bear_agent_model: Optional[str] = None
    factcheck_agent_provider: Optional[str] = None
    factcheck_agent_model: Optional[str] = None
    synthesizer_agent_provider: Optional[str] = None
    synthesizer_agent_model: Optional[str] = None

    # API Keys
    anthropic_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None

    # ChromaDB
    chroma_host: str = "chromadb"
    chroma_port: int = 8000

    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
