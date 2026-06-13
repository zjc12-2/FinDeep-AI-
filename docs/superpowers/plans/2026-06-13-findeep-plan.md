# FinDeep-AI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete FinDeep-AI multi-agent financial research platform — Next.js frontend + FastAPI backend + LangGraph agents + RAG + ChromaDB, all orchestrated via Docker Compose.

**Architecture:** Docker Compose runs 3 services: Next.js :3000 (UI/SSR), FastAPI :8000 (Agent orchestration + RAG), ChromaDB :8001 (vector storage). Frontend communicates via REST + SSE. Backend uses LangGraph to orchestrate Bull/Bear/FactCheck/Synthesizer agents in a parallel-then-sequential pipeline, with LlamaIndex powering multi-source RAG retrieval.

**Tech Stack:** Python 3.11+ / FastAPI / LangGraph / LlamaIndex / ChromaDB / Next.js 14 / Tailwind / shadcn/ui / TypeScript / Docker Compose

---

## Phase 1: Project Foundation

### Task 1: Project scaffolding and Docker Compose

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `README.md`
- Create: `backend/requirements.txt`
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `frontend/package.json`

- [ ] **Step 1: Create `docker-compose.yml`**

```yaml
version: "3.9"

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    env_file: .env
    depends_on:
      - backend
    volumes:
      - ./frontend/src:/app/src
    command: npm run dev

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      chromadb:
        condition: service_healthy
    volumes:
      - ./backend/app:/app/app
      - ./backend/data:/app/data
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  chroma_data:
```

- [ ] **Step 2: Create `.env.example`**

```env
# LLM通用配置
LLM_PROVIDER=claude
LLM_MODEL=claude-sonnet-4-6

# 按Agent独立配置（可选）
BULL_AGENT_PROVIDER=claude
BULL_AGENT_MODEL=claude-sonnet-4-6
BEAR_AGENT_PROVIDER=claude
BEAR_AGENT_MODEL=claude-sonnet-4-6
FACTCHECK_AGENT_PROVIDER=deepseek
FACTCHECK_AGENT_MODEL=deepseek-chat
SYNTHESIZER_AGENT_PROVIDER=claude
SYNTHESIZER_AGENT_MODEL=claude-sonnet-4-6

# API Keys
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=

# ChromaDB
CHROMA_HOST=chromadb
CHROMA_PORT=8000

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

- [ ] **Step 3: Create `backend/requirements.txt`**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
langgraph==0.2.0
langchain==0.3.0
langchain-community==0.3.0
llama-index==0.11.0
llama-index-embeddings-huggingface==0.3.0
chromadb==0.5.5
akshare==1.14.0
pypdf==4.3.1
python-multipart==0.0.9
python-dotenv==1.0.1
httpx==0.27.2
pydantic==2.9.0
pydantic-settings==2.5.0
```

- [ ] **Step 4: Create `backend/pyproject.toml`**

```toml
[project]
name = "findeep-backend"
version = "0.1.0"
requires-python = ">=3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 5: Create `backend/app/__init__.py`**

```python
"""FinDeep Backend - Multi-agent financial research platform."""
```

- [ ] **Step 6: Create `frontend/package.json`**

```json
{
  "name": "findeep-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-markdown": "^9.0.0",
    "rehype-raw": "^7.0.0",
    "lucide-react": "^0.400.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.4.0"
  },
  "devDependencies": {
    "@types/node": "^20.14.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "typescript": "^5.5.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

- [ ] **Step 7: Create minimal `README.md`**

```markdown
# FinDeep - AI多智能体深度研报生成系统

## Quick Start

1. Copy `.env.example` to `.env` and fill in your API keys
2. Run `docker compose up`
3. Open http://localhost:3000

## Architecture

- Frontend: Next.js 14 + Tailwind + shadcn/ui (:3000)
- Backend: FastAPI + LangGraph + LlamaIndex (:8000)
- Vector DB: ChromaDB (:8001)
```

- [ ] **Step 8: Commit**

```bash
git add -A && git commit -m "chore: project scaffolding with docker-compose and dependency manifests"
```

---

### Task 2: Backend configuration and FastAPI app skeleton

**Files:**
- Create: `backend/app/config.py`
- Create: `backend/app/main.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/research.py`
- Create: `backend/app/models/schemas.py`

- [ ] **Step 1: Create `backend/app/config.py`**

```python
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
```

- [ ] **Step 2: Create `backend/app/models/__init__.py`**

```python
"""Data models for FinDeep backend."""
```

- [ ] **Step 3: Create `backend/app/models/research.py`**

```python
"""Pydantic models for research requests and reports."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from uuid import uuid4


def generate_id() -> str:
    return uuid4().hex[:12]


class DataSourceConfig(BaseModel):
    """Per-request data source selection."""
    akshare: bool = True
    news: bool = True
    uploaded_docs: List[str] = Field(default_factory=list)


class ResearchRequest(BaseModel):
    query: str
    data_sources: DataSourceConfig = Field(default_factory=DataSourceConfig)


class ResearchTask(BaseModel):
    task_id: str = Field(default_factory=generate_id)
    query: str
    data_sources: DataSourceConfig
    status: str = "pending"  # pending → running → completed → failed
    created_at: str = ""


class Citation(BaseModel):
    ref_id: str
    doc_id: str
    chunk_index: int
    text: str
    page: Optional[int] = None
    confidence: float = 0.0


class ResearchReport(BaseModel):
    task_id: str
    query: str
    markdown: str
    citations: Dict[str, Citation] = Field(default_factory=dict)
    bull_view: Optional[str] = None
    bear_view: Optional[str] = None
    factcheck_notes: List[str] = Field(default_factory=list)
    created_at: str = ""


class FollowUpRequest(BaseModel):
    task_id: str
    question: str


class TimelineEvent(BaseModel):
    date: str
    event: str
    type: str  # financial, management, market, other
    causes: List[str] = Field(default_factory=list)
    effects: List[str] = Field(default_factory=list)
    source_ref: Optional[str] = None
```

- [ ] **Step 4: Create `backend/app/models/schemas.py`**

```python
"""Request/response schemas for API endpoints."""
from pydantic import BaseModel
from typing import List, Optional


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    pages: int
    status: str


class ReportResponse(BaseModel):
    task_id: str
    query: str
    markdown: str
    citations: dict
    bull_view: Optional[str] = None
    bear_view: Optional[str] = None
    factcheck_notes: List[str] = []
    created_at: str


class SourceResponse(BaseModel):
    ref_id: str
    doc_id: str
    text: str
    page: Optional[int] = None
    confidence: float


class TimelineResponse(BaseModel):
    events: list


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
```

- [ ] **Step 5: Create `backend/app/main.py`**

```python
"""FinDeep FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title="FinDeep API",
    description="AI多智能体深度研报生成系统",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "findeep-backend"}
```

- [ ] **Step 6: Verify backend starts**

```bash
cd backend && pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 3 && curl http://localhost:8000/api/health
```

Expected: `{"status":"ok","service":"findeep-backend"}`

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "feat: backend config and FastAPI app skeleton"
```

---

### Task 3: LLM provider abstraction layer

**Files:**
- Create: `backend/app/llm/__init__.py`
- Create: `backend/app/llm/provider.py`
- Create: `backend/app/llm/providers/__init__.py`
- Create: `backend/app/llm/providers/claude.py`
- Create: `backend/app/llm/providers/openai_provider.py`
- Create: `backend/app/llm/providers/deepseek.py`
- Create: `backend/app/llm/providers/openai_compatible.py`

- [ ] **Step 1: Create `backend/app/llm/__init__.py`**

```python
"""LLM provider abstraction layer."""
from app.llm.provider import LLMProvider, get_llm

__all__ = ["LLMProvider", "get_llm"]
```

- [ ] **Step 2: Create `backend/app/llm/provider.py`**

```python
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
```

- [ ] **Step 3: Create `backend/app/llm/providers/__init__.py`**

```python
"""LLM provider implementations."""
```

- [ ] **Step 4: Create `backend/app/llm/providers/claude.py`**

```python
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
```

- [ ] **Step 5: Create `backend/app/llm/providers/openai_provider.py`**

```python
"""OpenAI API provider."""
import httpx
from typing import AsyncIterator
from app.llm.provider import LLMProvider
from app.config import settings


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.api_key = settings.openai_api_key
        self.base_url = "https://api.openai.com/v1"

    async def chat(self, messages: list, **kwargs) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": kwargs.get("max_tokens", 4096),
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def chat_stream(self, messages: list, **kwargs):
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": kwargs.get("max_tokens", 4096),
                    "stream": True,
                },
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        import json
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta and delta["content"]:
                            yield delta["content"]
```

- [ ] **Step 6: Create `backend/app/llm/providers/deepseek.py`**

```python
"""DeepSeek API provider (OpenAI-compatible)."""
from app.llm.providers.openai_provider import OpenAIProvider
from app.config import settings


class DeepSeekProvider(OpenAIProvider):
    def __init__(self, model: str = "deepseek-chat"):
        super().__init__(model=model)
        self.base_url = "https://api.deepseek.com/v1"
```

- [ ] **Step 7: Create `backend/app/llm/providers/openai_compatible.py`**

```python
"""Generic OpenAI-compatible API provider with custom base URL."""
from app.llm.providers.openai_provider import OpenAIProvider
from app.config import settings


class OpenAICompatibleProvider(OpenAIProvider):
    def __init__(self, model: str = None):
        super().__init__(model=model or settings.llm_model)
        self.base_url = settings.openai_base_url or "http://localhost:11434/v1"
```

- [ ] **Step 8: Commit**

```bash
git add -A && git commit -m "feat: LLM provider abstraction with Claude/OpenAI/DeepSeek/custom support"
```

---

## Phase 2: RAG Engine

### Task 4: Data source adapter base and implementations

**Files:**
- Create: `backend/app/rag/__init__.py`
- Create: `backend/app/rag/datasources/__init__.py`
- Create: `backend/app/rag/datasources/base.py`
- Create: `backend/app/rag/datasources/akshare.py`
- Create: `backend/app/rag/datasources/news.py`
- Create: `backend/app/rag/datasources/user_upload.py`

- [ ] **Step 1: Create `backend/app/rag/__init__.py`**

```python
"""RAG engine and data source adapters."""
```

- [ ] **Step 2: Create `backend/app/rag/datasources/__init__.py`**

```python
"""Data source adapters for RAG retrieval."""
from app.rag.datasources.base import DataSourceAdapter, Document
from app.rag.datasources.akshare import AkShareAdapter
from app.rag.datasources.news import NewsSearchAdapter
from app.rag.datasources.user_upload import UserUploadAdapter

__all__ = [
    "DataSourceAdapter",
    "Document",
    "AkShareAdapter",
    "NewsSearchAdapter",
    "UserUploadAdapter",
]
```

- [ ] **Step 3: Create `backend/app/rag/datasources/base.py`**

```python
"""Abstract base for data source adapters."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Document:
    """A document chunk returned from a data source."""
    text: str
    doc_id: str = ""
    chunk_index: int = 0
    page: Optional[int] = None
    source_type: str = ""  # akshare, news, user_upload
    metadata: dict = field(default_factory=dict)


class DataSourceAdapter(ABC):
    """Unified data source interface for RAG retrieval."""

    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        """Search for documents relevant to the query."""
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the data source is currently accessible."""
        ...

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Identifier for this source type."""
        ...
```

- [ ] **Step 4: Create `backend/app/rag/datasources/akshare.py`**

```python
"""AkShare financial data adapter for A-share market."""
from typing import List
from app.rag.datasources.base import DataSourceAdapter, Document


class AkShareAdapter(DataSourceAdapter):
    source_type = "akshare"

    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        """Fetch financial data from AkShare based on stock code or company name."""
        try:
            import akshare as ak
        except ImportError:
            return []

        docs = []
        stock_code = _extract_stock_code(query)

        if stock_code:
            try:
                # Fetch basic company info
                info = ak.stock_individual_info_em(symbol=stock_code)
                text_parts = []
                for _, row in info.iterrows():
                    text_parts.append(f"{row['item']}: {row['value']}")
                text = "\n".join(text_parts)
                docs.append(Document(
                    text=text,
                    doc_id=f"akshare_info_{stock_code}",
                    source_type="akshare",
                    metadata={"stock_code": stock_code},
                ))
            except Exception:
                pass

            try:
                # Fetch financial statements summary
                fin = ak.stock_financial_abstract(symbol=stock_code)
                if fin is not None and not fin.empty:
                    recent = fin.head(10)
                    text = "财务指标摘要:\n" + recent.to_string()
                    docs.append(Document(
                        text=text,
                        doc_id=f"akshare_fin_{stock_code}",
                        source_type="akshare",
                        metadata={"stock_code": stock_code},
                    ))
            except Exception:
                pass

        return docs[:top_k]

    async def is_available(self) -> bool:
        try:
            import akshare
            return True
        except ImportError:
            return False


def _extract_stock_code(query: str) -> str:
    """Extract 6-digit stock code from query string."""
    import re
    match = re.search(r'\b(\d{6})\b', query)
    return match.group(1) if match else ""
```

- [ ] **Step 5: Create `backend/app/rag/datasources/news.py`**

```python
"""News search adapter using web-based retrieval."""
from typing import List
from app.rag.datasources.base import DataSourceAdapter, Document
from app.llm.provider import get_llm


class NewsSearchAdapter(DataSourceAdapter):
    source_type = "news"

    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        """Use LLM to summarize relevant news context for the query.
        In production, this would integrate with a news API (e.g., NewsAPI, Bing).
        For MVP, we structure the query context as a synthetic news brief.
        """
        llm = get_llm("default")
        prompt = f"""你是一位财经新闻分析师。关于"{query}"，请基于你的知识提供最新的相关新闻要点。
格式：每条新闻一行，包含简要描述。如果涉及具体数据，请注明。"""

        try:
            response = await llm.chat([
                {"role": "user", "content": prompt}
            ], max_tokens=1024)
            return [Document(
                text=response,
                doc_id="news_context",
                source_type="news",
                metadata={"query": query},
            )]
        except Exception:
            return []

    async def is_available(self) -> bool:
        return True
```

- [ ] **Step 6: Create `backend/app/rag/datasources/user_upload.py`**

```python
"""User-uploaded document adapter."""
import os
from typing import List
from app.rag.datasources.base import DataSourceAdapter, Document


class UserUploadAdapter(DataSourceAdapter):
    source_type = "user_upload"

    def __init__(self, doc_ids: List[str], chroma_client=None):
        self.doc_ids = doc_ids
        self.chroma_client = chroma_client

    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        """Search user-uploaded documents via ChromaDB."""
        if not self.chroma_client or not self.doc_ids:
            return []

        try:
            collection = self.chroma_client.get_or_create_collection("user_docs")
            results = collection.query(
                query_texts=[query],
                n_results=top_k,
                where={"doc_id": {"$in": self.doc_ids}},
            )
            docs = []
            if results["documents"] and results["documents"][0]:
                for i, text in enumerate(results["documents"][0]):
                    meta = results["metadatas"][0][i] if results["metadatas"] else {}
                    docs.append(Document(
                        text=text,
                        doc_id=meta.get("doc_id", ""),
                        chunk_index=meta.get("chunk_index", i),
                        page=meta.get("page"),
                        source_type="user_upload",
                        metadata=meta,
                    ))
            return docs
        except Exception:
            return []

    async def is_available(self) -> bool:
        return self.chroma_client is not None and len(self.doc_ids) > 0
```

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "feat: data source adapters (AkShare, news, user upload)"
```

---

### Task 5: RAG engine with LlamaIndex and ChromaDB

**Files:**
- Create: `backend/app/rag/engine.py`
- Create: `backend/app/rag/citation.py`

- [ ] **Step 1: Create `backend/app/rag/engine.py`**

```python
"""RAG engine integrating LlamaIndex with ChromaDB and multi-source retrieval."""
import uuid
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings as app_settings
from app.rag.datasources.base import DataSourceAdapter, Document
from app.rag.datasources import AkShareAdapter, NewsSearchAdapter, UserUploadAdapter
from app.rag.citation import CitationManager
from app.models.research import DataSourceConfig


class RAGEngine:
    """Orchestrates multi-source document retrieval and citation tracking."""

    def __init__(self, data_sources: DataSourceConfig):
        self.data_sources = data_sources
        self.adapters: List[DataSourceAdapter] = []
        self.citations = CitationManager()

        # Initialize ChromaDB client
        self.chroma_client = chromadb.HttpClient(
            host=app_settings.chroma_host,
            port=app_settings.chroma_port,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Build adapter list based on config
        self._build_adapters()

    def _build_adapters(self):
        """Dynamically build adapter list from data source config."""
        if self.data_sources.akshare:
            self.adapters.append(AkShareAdapter())
        if self.data_sources.news:
            self.adapters.append(NewsSearchAdapter())
        if self.data_sources.uploaded_docs:
            upload_adapter = UserUploadAdapter(
                doc_ids=self.data_sources.uploaded_docs,
                chroma_client=self.chroma_client,
            )
            self.adapters.append(upload_adapter)

    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        """Search across all enabled data sources."""
        if not self.adapters:
            return []

        all_docs = []
        for adapter in self.adapters:
            if await adapter.is_available():
                try:
                    docs = await adapter.search(query, top_k)
                    all_docs.extend(docs)
                except Exception:
                    continue

        # Register citations for each document
        for doc in all_docs:
            self.citations.register(doc)

        return all_docs

    async def search_with_bias(self, query: str, bias: str = "bull", top_k: int = 5) -> List[Document]:
        """Search with a directional bias (bull=positive, bear=negative)."""
        bias_prompt = query
        if bias == "bull":
            bias_prompt = f"{query} 投资价值 竞争优势 增长 利好"
        elif bias == "bear":
            bias_prompt = f"{query} 风险 竞争压力 下滑 利空"

        return await self.search(bias_prompt, top_k)

    def has_sources(self) -> bool:
        """Check if any data sources were provided."""
        return len(self.adapters) > 0

    def get_adapter_names(self) -> List[str]:
        """Return names of active adapters."""
        return [a.source_type for a in self.adapters]
```

- [ ] **Step 2: Create `backend/app/rag/citation.py`**

```python
"""Citation mapping system — links report claims to source documents."""
import uuid
from typing import Dict, Optional
from app.rag.datasources.base import Document
from app.models.research import Citation


class CitationManager:
    """Manages the mapping between citation IDs and source documents."""

    def __init__(self):
        self._citations: Dict[str, Citation] = {}

    def register(self, doc: Document) -> Citation:
        """Register a document and return its citation."""
        ref_id = uuid.uuid4().hex[:8]
        citation = Citation(
            ref_id=ref_id,
            doc_id=doc.doc_id or ref_id,
            chunk_index=doc.chunk_index,
            text=doc.text[:500],
            page=doc.page,
            confidence=0.85,
        )
        self._citations[ref_id] = citation
        return citation

    def get(self, ref_id: str) -> Optional[Citation]:
        """Retrieve a citation by its reference ID."""
        return self._citations.get(ref_id)

    def get_all(self) -> Dict[str, Citation]:
        """Get all citations."""
        return dict(self._citations)

    def to_dict(self) -> dict:
        """Serialize all citations to a JSON-safe dict."""
        return {
            ref_id: {
                "ref_id": c.ref_id,
                "doc_id": c.doc_id,
                "chunk_index": c.chunk_index,
                "text": c.text,
                "page": c.page,
                "confidence": c.confidence,
            }
            for ref_id, c in self._citations.items()
        }
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: RAG engine with LlamaIndex/ChromaDB integration and citation mapping"
```

---

### Task 6: File upload endpoint

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/upload.py`

- [ ] **Step 1: Create `backend/app/api/__init__.py`**

```python
"""API route modules for FinDeep backend."""
```

- [ ] **Step 2: Create `backend/app/api/upload.py`**

```python
"""File upload endpoint — accepts PDFs, vectorizes via ChromaDB."""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pypdf import PdfReader
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings as app_settings
from app.models.schemas import UploadResponse

router = APIRouter(prefix="/api", tags=["upload"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".csv"}


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF or text document, vectorize it, return doc_id."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    text = ""
    pages = 0

    if ext == ".pdf":
        # Save to temp file for pypdf
        temp_path = f"/tmp/{uuid.uuid4().hex}.pdf"
        with open(temp_path, "wb") as f:
            f.write(content)
        reader = PdfReader(temp_path)
        pages = len(reader.pages)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        os.remove(temp_path)
    else:
        text = content.decode("utf-8", errors="replace")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No extractable text found in file")

    doc_id = uuid.uuid4().hex[:12]
    chunks = _chunk_text(text)

    # Store in ChromaDB
    client = chromadb.HttpClient(
        host=app_settings.chroma_host,
        port=app_settings.chroma_port,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection("user_docs")

    for i, chunk in enumerate(chunks):
        collection.add(
            ids=[f"{doc_id}_{i}"],
            documents=[chunk],
            metadatas=[{
                "doc_id": doc_id,
                "filename": file.filename,
                "chunk_index": i,
                "page": min(i, pages - 1) if pages else None,
            }],
        )

    return UploadResponse(
        doc_id=doc_id,
        filename=file.filename or "unknown",
        pages=pages or len(chunks),
        status="vectorized",
    )
```

- [ ] **Step 3: Register the router in `backend/app/main.py`**

Edit `backend/app/main.py` — add after `app = FastAPI(...)` and before `@app.get(...)`:

```python
from app.api.upload import router as upload_router

app.include_router(upload_router)
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: file upload endpoint with PDF vectorization to ChromaDB"
```

---

## Phase 3: Agent System

### Task 7: Bull Agent (multi-perspective analyst)

**Files:**
- Create: `backend/app/agents/__init__.py`
- Create: `backend/app/agents/bull_agent.py`

- [ ] **Step 1: Create `backend/app/agents/__init__.py`**

```python
"""FinDeep multi-agent system — Bull, Bear, FactCheck, Synthesizer."""
```

- [ ] **Step 2: Create `backend/app/agents/bull_agent.py`**

```python
"""Bull Agent — finds investment opportunities and positive factors."""
from typing import AsyncIterator
from app.llm.provider import get_llm
from app.rag.engine import RAGEngine
from app.rag.datasources.base import Document

BULL_SYSTEM_PROMPT = """你是一位资深多方分析师(Bull Analyst)，专注于发现投资机会。

你的职责：
1. 基于提供的资料，找出公司的竞争优势、增长潜力和投资价值
2. 分析行业趋势、市场份额、技术创新、管理能力等正面因素
3. 每个分析结论必须引用具体的检索资料作为支撑，标注来源编号
4. 客观专业，不过度乐观，承认不确定性
5. 用Markdown格式输出，关键数据加粗

输出结构：
## 投资亮点
- 亮点1 [ref:xxx]
- 亮点2 [ref:xxx]

## 增长驱动因素
1. 因素1 [ref:xxx]
2. 因素2 [ref:xxx]

## 估值参考
（基于可用数据）

## 总结
（100字以内综合评估）"""


async def run_bull_agent(
    query: str,
    rag_engine: RAGEngine,
) -> str:
    """Execute the Bull Agent analysis.

    Args:
        query: Research query (company name / stock code)
        rag_engine: RAG engine for document retrieval

    Returns:
        Markdown-formatted bull case analysis
    """
    llm = get_llm("bull")

    # Retrieve documents with bullish bias
    docs = await rag_engine.search_with_bias(query, bias="bull", top_k=8)

    # Build context from retrieved documents
    context_parts = []
    for i, doc in enumerate(docs):
        ref = rag_engine.citations.register(doc)
        context_parts.append(f"--- 资料片段 [{ref.ref_id}] ---\n{doc.text}")

    context = "\n\n".join(context_parts) if context_parts else "无可用的检索资料。"

    messages = [
        {"role": "system", "content": BULL_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请分析以下公司的投资价值和多方因素：

**研究标的：** {query}

**检索资料：**
{context}

请基于以上资料，给出你的多方分析报告。每个观点需要标注引用编号。"""},
    ]

    return await llm.chat(messages, max_tokens=4096)


async def run_bull_agent_stream(
    query: str,
    rag_engine: RAGEngine,
) -> AsyncIterator[str]:
    """Streaming version of Bull Agent."""
    llm = get_llm("bull")
    docs = await rag_engine.search_with_bias(query, bias="bull", top_k=8)

    context_parts = []
    for i, doc in enumerate(docs):
        ref = rag_engine.citations.register(doc)
        context_parts.append(f"--- 资料片段 [{ref.ref_id}] ---\n{doc.text}")

    context = "\n\n".join(context_parts) if context_parts else "无可用的检索资料。"

    messages = [
        {"role": "system", "content": BULL_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请分析以下公司的投资价值和多方因素：

**研究标的：** {query}

**检索资料：**
{context}

请基于以上资料，给出你的多方分析报告。每个观点需要标注引用编号。"""},
    ]

    async for chunk in llm.chat_stream(messages, max_tokens=4096):
        yield chunk
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: Bull Agent — multi-perspective financial analyst"
```

---

### Task 8: Bear Agent (risk-focused analyst)

**Files:**
- Create: `backend/app/agents/bear_agent.py`

- [ ] **Step 1: Create `backend/app/agents/bear_agent.py`**

```python
"""Bear Agent — identifies risks, weaknesses, and negative factors."""
from typing import AsyncIterator
from app.llm.provider import get_llm
from app.rag.engine import RAGEngine

BEAR_SYSTEM_PROMPT = """你是一位资深空方分析师(Bear Analyst)，专注于发现投资风险。

你的职责：
1. 基于提供的资料，找出公司的风险点、竞争威胁和潜在问题
2. 分析行业竞争、财务压力、管理风险、政策变化等负面因素
3. 每个分析结论必须引用具体的检索资料作为支撑，标注来源编号
4. 客观专业，不过度悲观，承认不确定性
5. 用Markdown格式输出，关键数据加粗

输出结构：
## 风险警示
- 风险1 [ref:xxx]
- 风险2 [ref:xxx]

## 潜在压力
1. 压力点1 [ref:xxx]
2. 压力点2 [ref:xxx]

## 需关注的指标
（列出需要持续跟踪的风险指标）

## 总结
（100字以内综合风险评估）"""


async def run_bear_agent(
    query: str,
    rag_engine: RAGEngine,
) -> str:
    """Execute the Bear Agent analysis.

    Args:
        query: Research query
        rag_engine: RAG engine for document retrieval

    Returns:
        Markdown-formatted bear case analysis
    """
    llm = get_llm("bear")

    docs = await rag_engine.search_with_bias(query, bias="bear", top_k=8)

    context_parts = []
    for i, doc in enumerate(docs):
        ref = rag_engine.citations.register(doc)
        context_parts.append(f"--- 资料片段 [{ref.ref_id}] ---\n{doc.text}")

    context = "\n\n".join(context_parts) if context_parts else "无可用的检索资料。"

    messages = [
        {"role": "system", "content": BEAR_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请分析以下公司的投资风险和潜在问题：

**研究标的：** {query}

**检索资料：**
{context}

请基于以上资料，给出你的空方分析报告。每个观点需要标注引用编号。"""},
    ]

    return await llm.chat(messages, max_tokens=4096)


async def run_bear_agent_stream(
    query: str,
    rag_engine: RAGEngine,
) -> AsyncIterator[str]:
    """Streaming version of Bear Agent."""
    llm = get_llm("bear")
    docs = await rag_engine.search_with_bias(query, bias="bear", top_k=8)

    context_parts = []
    for i, doc in enumerate(docs):
        ref = rag_engine.citations.register(doc)
        context_parts.append(f"--- 资料片段 [{ref.ref_id}] ---\n{doc.text}")

    context = "\n\n".join(context_parts) if context_parts else "无可用的检索资料。"

    messages = [
        {"role": "system", "content": BEAR_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请分析以下公司的投资风险和潜在问题：

**研究标的：** {query}

**检索资料：**
{context}

请基于以上资料，给出你的空方分析报告。每个观点需要标注引用编号。"""},
    ]

    async for chunk in llm.chat_stream(messages, max_tokens=4096):
        yield chunk
```

- [ ] **Step 2: Commit**

```bash
git add -A && git commit -m "feat: Bear Agent — risk-focused negative analyst"
```

---

### Task 9: FactCheck Agent and Synthesizer Agent

**Files:**
- Create: `backend/app/agents/factcheck_agent.py`
- Create: `backend/app/agents/synthesizer_agent.py`

- [ ] **Step 1: Create `backend/app/agents/factcheck_agent.py`**

```python
"""FactCheck Agent — verifies claims from Bull and Bear analyses."""
from typing import AsyncIterator
from app.llm.provider import get_llm
from app.rag.engine import RAGEngine

FACTCHECK_SYSTEM_PROMPT = """你是一位严谨的事实核查员(Fact Checker)，负责验证分析师的观点是否有可靠的资料来源支撑。

你的职责：
1. 逐一审查Bull和Bear分析师的每个重要论断
2. 检查每个论断在检索资料中是否有对应支撑
3. 标记 ⚠️ 任何缺乏可靠信源支撑的推断
4. 标记 ✅ 有明确来源支撑的论断
5. 不表达你自己的投资观点，只做事实验证

输出结构：
## 事实核查报告

### ✅ 有信源支撑的论断
- 论断内容 → 来源: [ref:xxx]

### ⚠️ 缺乏可靠支撑的推断
- 论断内容 → 原因: 未在检索资料中找到直接证据

### 📊 总体可靠性评估
（百分比，并解释）"""


async def run_factcheck_agent(
    bull_analysis: str,
    bear_analysis: str,
    rag_engine: RAGEngine,
) -> str:
    """Verify claims from both analysts against available sources.

    Args:
        bull_analysis: Bull Agent's output
        bear_analysis: Bear Agent's output
        rag_engine: RAG engine with registered citations

    Returns:
        Markdown-formatted fact-check report
    """
    llm = get_llm("factcheck")

    citations_list = []
    for ref_id, c in rag_engine.citations.get_all().items():
        citations_list.append(f"[{ref_id}] {c.text[:200]}...")

    citations_text = "\n".join(citations_list) if citations_list else "无可验证的引用来源。"

    messages = [
        {"role": "system", "content": FACTCHECK_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请验证以下两份分析的可靠性：

**可用引用来源：**
{citations_text}

**多方分析师(Bull)报告：**
{bull_analysis}

**空方分析师(Bear)报告：**
{bear_analysis}

请逐条验证关键论断，区分有支撑的结论和缺乏支撑的推断。"""},
    ]

    return await llm.chat(messages, max_tokens=4096)


async def run_factcheck_agent_stream(
    bull_analysis: str,
    bear_analysis: str,
    rag_engine: RAGEngine,
) -> AsyncIterator[str]:
    """Streaming version of FactCheck Agent."""
    llm = get_llm("factcheck")

    citations_list = []
    for ref_id, c in rag_engine.citations.get_all().items():
        citations_list.append(f"[{ref_id}] {c.text[:200]}...")

    citations_text = "\n".join(citations_list) if citations_list else "无可验证的引用来源。"

    messages = [
        {"role": "system", "content": FACTCHECK_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请验证以下两份分析的可靠性：

**可用引用来源：**
{citations_text}

**多方分析师(Bull)报告：**
{bull_analysis}

**空方分析师(Bear)报告：**
{bear_analysis}

请逐条验证关键论断，区分有支撑的结论和缺乏支撑的推断。"""},
    ]

    async for chunk in llm.chat_stream(messages, max_tokens=4096):
        yield chunk
```

- [ ] **Step 2: Create `backend/app/agents/synthesizer_agent.py`**

```python
"""Synthesizer Agent — merges Bull/Bear/FactCheck into a balanced final report."""
from typing import AsyncIterator
from app.llm.provider import get_llm

SYNTHESIZER_SYSTEM_PROMPT = """你是一位资深综合编辑(Synthesizer)，负责将多方观点融合为一份平衡、专业的金融研究报告。

你的职责：
1. 综合Bull、Bear和FactCheck的分析结果
2. 产出完整的Markdown格式研究报告
3. 保持平衡视角——既呈现机会也呈现风险
4. 保留原有的引用标注 [ref:xxx]
5. 重要发现用 ⚠️（需关注）和 ✅（已验证）标记

报告结构：
# [公司名称] 深度研究报告

## 一、核心摘要
（200字概览，平衡呈现多空观点）

## 二、多方视角：投资机会
（来自Bull分析的精炼内容）

## 三、空方视角：风险警示
（来自Bear分析的精炼内容）

## 四、事实核查与可靠性评估
（来自FactCheck的验证结果）

## 五、综合评估
（平衡结论，不做买卖建议）

---
*⚠️ 声明：本报告由AI自动生成，仅供参考，不构成投资建议。*"""


async def run_synthesizer_agent(
    query: str,
    bull_analysis: str,
    bear_analysis: str,
    factcheck_analysis: str,
) -> str:
    """Synthesize all analyses into a final balanced report.

    Args:
        query: Original research query
        bull_analysis: Bull Agent output
        bear_analysis: Bear Agent output
        factcheck_analysis: FactCheck Agent output

    Returns:
        Final Markdown research report
    """
    llm = get_llm("synthesizer")

    messages = [
        {"role": "system", "content": SYNTHESIZER_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请综合以下三份分析，生成一份平衡的最终研究报告：

**研究标的：** {query}

**Bull分析：**
{bull_analysis}

**Bear分析：**
{bear_analysis}

**事实核查：**
{factcheck_analysis}

请严格按照报告结构输出，保留引用标注。"""},
    ]

    return await llm.chat(messages, max_tokens=8192)


async def run_synthesizer_agent_stream(
    query: str,
    bull_analysis: str,
    bear_analysis: str,
    factcheck_analysis: str,
) -> AsyncIterator[str]:
    """Streaming version of Synthesizer Agent."""
    llm = get_llm("synthesizer")

    messages = [
        {"role": "system", "content": SYNTHESIZER_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请综合以下三份分析，生成一份平衡的最终研究报告：

**研究标的：** {query}

**Bull分析：**
{bull_analysis}

**Bear分析：**
{bear_analysis}

**事实核查：**
{factcheck_analysis}

请严格按照报告结构输出，保留引用标注。"""},
    ]

    async for chunk in llm.chat_stream(messages, max_tokens=8192):
        yield chunk
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: FactCheck Agent and Synthesizer Agent"
```

---

### Task 10: LangGraph state graph — multi-agent orchestration

**Files:**
- Create: `backend/app/agents/graph.py`
- Create: `backend/app/agents/followup_agent.py`

- [ ] **Step 1: Create `backend/app/agents/graph.py`**

```python
"""LangGraph state graph for multi-agent debate orchestration.

Workflow:
  START → pre_search → parallel(Bull | Bear) → FactCheck → Synthesizer → END

The Bull and Bear agents run in parallel via LangGraph's Send API.
"""
import asyncio
import json
import operator
from typing import TypedDict, Annotated, AsyncIterator, List
from langgraph.graph import StateGraph, END
from app.models.research import DataSourceConfig
from app.rag.engine import RAGEngine
from app.agents.bull_agent import run_bull_agent
from app.agents.bear_agent import run_bear_agent
from app.agents.factcheck_agent import run_factcheck_agent
from app.agents.synthesizer_agent import run_synthesizer_agent


class ResearchState(TypedDict):
    query: str
    data_sources: DataSourceConfig
    pre_search_docs: list
    bull_analysis: str
    bear_analysis: str
    factcheck_analysis: str
    final_report: str
    citations: dict
    error: str


async def pre_search_node(state: ResearchState) -> ResearchState:
    """Initial RAG search to gather context for all agents."""
    rag = RAGEngine(state["data_sources"])
    if not rag.has_sources():
        state["error"] = "未选择任何数据源。请至少启用一个数据源或上传文档。"
    else:
        state["pre_search_docs"] = []  # Will be done per-agent
    return state


async def bull_node(state: ResearchState) -> ResearchState:
    """Execute Bull Agent analysis."""
    if state.get("error"):
        return state
    rag = RAGEngine(state["data_sources"])
    try:
        state["bull_analysis"] = await run_bull_agent(state["query"], rag)
        # Collect citations from Bull
        state["citations"] = rag.citations.to_dict()
    except Exception as e:
        state["bull_analysis"] = f"Bull分析生成失败: {str(e)}"
    return state


async def bear_node(state: ResearchState) -> ResearchState:
    """Execute Bear Agent analysis."""
    if state.get("error"):
        return state
    rag = RAGEngine(state["data_sources"])
    try:
        state["bear_analysis"] = await run_bear_agent(state["query"], rag)
        # Merge citations from Bear
        bear_citations = rag.citations.to_dict()
        if state.get("citations"):
            state["citations"].update(bear_citations)
        else:
            state["citations"] = bear_citations
    except Exception as e:
        state["bear_analysis"] = f"Bear分析生成失败: {str(e)}"
    return state


async def factcheck_node(state: ResearchState) -> ResearchState:
    """Execute FactCheck Agent on both analyses."""
    if state.get("error"):
        return state
    rag = RAGEngine(state["data_sources"])
    try:
        state["factcheck_analysis"] = await run_factcheck_agent(
            state.get("bull_analysis", ""),
            state.get("bear_analysis", ""),
            rag,
        )
        # Merge citations
        fc_citations = rag.citations.to_dict()
        if state.get("citations"):
            state["citations"].update(fc_citations)
    except Exception as e:
        state["factcheck_analysis"] = f"事实核查失败: {str(e)}"
    return state


async def synthesizer_node(state: ResearchState) -> ResearchState:
    """Synthesize all analyses into final report."""
    if state.get("error"):
        state["final_report"] = f"# 研究失败\n\n错误: {state['error']}"
        return state
    try:
        state["final_report"] = await run_synthesizer_agent(
            state["query"],
            state.get("bull_analysis", ""),
            state.get("bear_analysis", ""),
            state.get("factcheck_analysis", ""),
        )
    except Exception as e:
        state["final_report"] = f"# 报告生成失败\n\n错误: {str(e)}"
    return state


def build_research_graph() -> StateGraph:
    """Build the LangGraph state graph for research workflow."""
    workflow = StateGraph(ResearchState)

    workflow.add_node("pre_search", pre_search_node)
    workflow.add_node("bull", bull_node)
    workflow.add_node("bear", bear_node)
    workflow.add_node("factcheck", factcheck_node)
    workflow.add_node("synthesizer", synthesizer_node)

    workflow.set_entry_point("pre_search")

    # pre_search → both bull AND bear (parallel)
    workflow.add_edge("pre_search", "bull")
    workflow.add_edge("pre_search", "bear")

    # Both must complete before factcheck
    workflow.add_edge("bull", "factcheck")
    workflow.add_edge("bear", "factcheck")

    # factcheck → synthesizer → END
    workflow.add_edge("factcheck", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow.compile()


async def run_research(
    query: str,
    data_sources: DataSourceConfig,
) -> ResearchState:
    """Run the full research workflow and return final state."""
    graph = build_research_graph()
    initial_state: ResearchState = {
        "query": query,
        "data_sources": data_sources,
        "pre_search_docs": [],
        "bull_analysis": "",
        "bear_analysis": "",
        "factcheck_analysis": "",
        "final_report": "",
        "citations": {},
        "error": "",
    }
    result = await graph.ainvoke(initial_state)
    return result
```

- [ ] **Step 2: Create `backend/app/agents/followup_agent.py`**

```python
"""Follow-up Agent — answers user questions about an existing report."""
from typing import AsyncIterator
from app.llm.provider import get_llm

FOLLOWUP_SYSTEM_PROMPT = """你是一位金融研究助手，负责回答用户针对已有研究报告的追问。

你的职责：
1. 基于已有的研报内容回答用户的追问
2. 如需补充分析，可以基于你的知识提供更多背景
3. 保持与原始报告一致的客观平衡视角
4. 用Markdown格式回复，如果引用了报告中的具体内容，标注对应的ref编号

如果问题超出研报范围，诚实说明并提供你可以提供的相关信息。"""


async def run_followup_agent(
    question: str,
    report_markdown: str,
    citations: dict,
) -> str:
    """Answer a follow-up question based on the existing report.

    Args:
        question: User's follow-up question
        report_markdown: The full report markdown
        citations: Citation mapping from the report

    Returns:
        Markdown-formatted answer
    """
    llm = get_llm("default")

    messages = [
        {"role": "system", "content": FOLLOWUP_SYSTEM_PROMPT},
        {"role": "user", "content": f"""**原始研究报告：**
{report_markdown[:8000]}

**引用来源：**
{json.dumps(citations, ensure_ascii=False, indent=2)[:2000]}

**用户追问：**
{question}

请基于以上信息回答用户的追问。"""},
    ]

    return await llm.chat(messages, max_tokens=2048)
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: LangGraph state graph for multi-agent orchestration + followup agent"
```

---

## Phase 4: API Endpoints

### Task 11: Research API endpoints (POST research + SSE streaming)

**Files:**
- Create: `backend/app/api/research.py`

- [ ] **Step 1: Create `backend/app/api/research.py`**

```python
"""Research API endpoints — initiate research and stream progress via SSE."""
import json
import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.research import ResearchRequest, ResearchTask, ResearchReport, DataSourceConfig
from app.agents.graph import run_research, ResearchState
from app.rag.engine import RAGEngine
from app.agents.bull_agent import run_bull_agent_stream
from app.agents.bear_agent import run_bear_agent_stream
from app.agents.factcheck_agent import run_factcheck_agent_stream
from app.agents.synthesizer_agent import run_synthesizer_agent_stream

router = APIRouter(prefix="/api", tags=["research"])

# In-memory task store (replace with DB in production)
_tasks: dict = {}
_reports: dict = {}


@router.post("/research")
async def create_research(request: ResearchRequest):
    """Initiate a new research task. Returns task_id immediately."""
    if not request.data_sources.akshare and not request.data_sources.news and not request.data_sources.uploaded_docs:
        raise HTTPException(status_code=400, detail="至少需要选择一个数据源或上传文档")

    task = ResearchTask(
        query=request.query,
        data_sources=request.data_sources,
        status="pending",
        created_at=datetime.now().isoformat(),
    )
    _tasks[task.task_id] = task

    # Start research in background
    asyncio.create_task(_execute_research(task.task_id, request))

    return {"task_id": task.task_id, "status": "pending"}


async def _execute_research(task_id: str, request: ResearchRequest):
    """Run the full research workflow in background and store the result."""
    _tasks[task_id].status = "running"
    try:
        result = await run_research(request.query, request.data_sources)
        _reports[task_id] = ResearchReport(
            task_id=task_id,
            query=request.query,
            markdown=result.get("final_report", ""),
            citations=result.get("citations", {}),
            bull_view=result.get("bull_analysis", ""),
            bear_view=result.get("bear_analysis", ""),
            factcheck_notes=_extract_factcheck_warnings(result.get("factcheck_analysis", "")),
            created_at=datetime.now().isoformat(),
        )
        _tasks[task_id].status = "completed"
    except Exception as e:
        _tasks[task_id].status = "failed"
        _reports[task_id] = ResearchReport(
            task_id=task_id,
            query=request.query,
            markdown=f"# 研究失败\n\n错误: {str(e)}",
            citations={},
            created_at=datetime.now().isoformat(),
        )


def _extract_factcheck_warnings(factcheck_text: str) -> list:
    """Extract warning items from factcheck output."""
    warnings = []
    for line in factcheck_text.split("\n"):
        if "⚠️" in line or "⚠" in line:
            warnings.append(line.strip())
    return warnings


@router.get("/research/{task_id}/stream")
async def stream_research(task_id: str):
    """SSE endpoint — streams agent progress during research."""
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    async def event_stream():
        """Generate SSE events for the research progress."""
        try:
            # Phase 1: Bull Agent
            yield _sse_event("phase", {"phase": "bull"})
            rag_bull = RAGEngine(task.data_sources)
            bull_chunks = []
            async for chunk in run_bull_agent_stream(task.query, rag_bull):
                bull_chunks.append(chunk)
                yield _sse_event("agent_progress", {"agent": "bull", "chunk": chunk})
            bull_analysis = "".join(bull_chunks)

            # Collect Bull citations
            bull_citations = rag_bull.citations.to_dict()
            for ref_id, c in bull_citations.items():
                yield _sse_event("citation", {"ref_id": ref_id, "source": c})

            # Phase 2: Bear Agent
            yield _sse_event("phase", {"phase": "bear"})
            rag_bear = RAGEngine(task.data_sources)
            bear_chunks = []
            async for chunk in run_bear_agent_stream(task.query, rag_bear):
                bear_chunks.append(chunk)
                yield _sse_event("agent_progress", {"agent": "bear", "chunk": chunk})
            bear_analysis = "".join(bear_chunks)

            # Merge Bear citations
            bear_citations = rag_bear.citations.to_dict()
            for ref_id, c in bear_citations.items():
                if ref_id not in bull_citations:
                    yield _sse_event("citation", {"ref_id": ref_id, "source": c})

            all_citations = {**bull_citations, **bear_citations}

            # Phase 3: FactCheck
            yield _sse_event("phase", {"phase": "factcheck"})
            rag_fc = RAGEngine(task.data_sources)
            fc_chunks = []
            async for chunk in run_factcheck_agent_stream(bull_analysis, bear_analysis, rag_fc):
                fc_chunks.append(chunk)
                yield _sse_event("agent_progress", {"agent": "factcheck", "chunk": chunk})
            factcheck_analysis = "".join(fc_chunks)

            # Check for warnings
            for line in factcheck_analysis.split("\n"):
                if "⚠️" in line or "⚠" in line:
                    yield _sse_event("warning", {"message": line.strip(), "location": "factcheck"})

            # Phase 4: Synthesizer
            yield _sse_event("phase", {"phase": "synthesize"})
            report_chunks = []
            async for chunk in run_synthesizer_agent_stream(
                task.query, bull_analysis, bear_analysis, factcheck_analysis
            ):
                report_chunks.append(chunk)
                yield _sse_event("agent_progress", {"agent": "synthesizer", "chunk": chunk})
            final_report = "".join(report_chunks)

            # Store the report
            _reports[task_id] = ResearchReport(
                task_id=task_id,
                query=task.query,
                markdown=final_report,
                citations=all_citations,
                bull_view=bull_analysis,
                bear_view=bear_analysis,
                factcheck_notes=_extract_factcheck_warnings(factcheck_analysis),
                created_at=datetime.now().isoformat(),
            )
            _tasks[task_id].status = "completed"

            yield _sse_event("complete", {"report_id": task_id})

        except Exception as e:
            _tasks[task_id].status = "failed"
            yield _sse_event("error", {"message": str(e)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _sse_event(event_type: str, data: dict) -> str:
    """Format a Server-Sent Event."""
    return f"data: {json.dumps({'type': event_type, **data}, ensure_ascii=False)}\n\n"


@router.get("/report/{task_id}")
async def get_report(task_id: str):
    """Get the final research report."""
    report = _reports.get(task_id)
    if not report:
        task = _tasks.get(task_id)
        if task and task.status == "running":
            return {"status": "running", "message": "报告生成中，请等待..."}
        raise HTTPException(status_code=404, detail="Report not found")
    return report.model_dump()
```

- [ ] **Step 2: Register research router in `backend/app/main.py`**

```python
from app.api.research import router as research_router
app.include_router(research_router)
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: research API with SSE streaming endpoint"
```

---

### Task 12: Sources, follow-up, and timeline endpoints

**Files:**
- Create: `backend/app/api/timeline.py`

- [ ] **Step 1: Add remaining endpoints to `backend/app/api/research.py`**

Add these routes to the existing router in `backend/app/api/research.py`:

```python
from app.agents.followup_agent import run_followup_agent
from app.models.research import FollowUpRequest


@router.get("/sources/{citation_id}")
async def get_source(citation_id: str):
    """Get the original source text for a citation."""
    # Search through all task reports for the citation
    for task_id, report in _reports.items():
        if citation_id in report.citations:
            return report.citations[citation_id]
    raise HTTPException(status_code=404, detail="Citation not found")


@router.post("/ask")
async def ask_followup(request: FollowUpRequest):
    """Ask a follow-up question about an existing report."""
    report = _reports.get(request.task_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        answer = await run_followup_agent(
            question=request.question,
            report_markdown=report.markdown,
            citations=report.citations,
        )
        return {"answer": answer, "task_id": request.task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"追问失败: {str(e)}")
```

- [ ] **Step 2: Create `backend/app/api/timeline.py`**

```python
"""Timeline API — extract event chains from research reports."""
from fastapi import APIRouter, HTTPException
from app.llm.provider import get_llm
from app.api.research import _reports

router = APIRouter(prefix="/api", tags=["timeline"])

TIMELINE_EXTRACTION_PROMPT = """从以下研究报告内容中提取关键事件链。

对每个事件提取：
- date: 时间（如 2024-Q2）
- event: 事件描述（简短）
- type: 类型（financial, management, market, other）
- causes: 导致此事件的原因列表
- effects: 此事件导致的结果列表
- source_ref: 相关的引用编号（如无则填null）

返回严格JSON数组格式，不要包含markdown代码块标记：
[
  {"date": "...", "event": "...", "type": "...", "causes": [...], "effects": [...], "source_ref": "ref:xxx"},
  ...
]"""


@router.get("/timeline/{task_id}")
async def get_timeline(task_id: str):
    """Extract event timeline from a completed report."""
    report = _reports.get(task_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    llm = get_llm("default")
    try:
        import json
        response = await llm.chat([
            {"role": "system", "content": "你是一位金融数据分析师。只输出JSON，不要包含其他文字。"},
            {"role": "user", "content": f"{TIMELINE_EXTRACTION_PROMPT}\n\n报告内容：\n{report.markdown[:8000]}"},
        ], max_tokens=2048)

        # Clean potential markdown code fences
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

        events = json.loads(cleaned)
        return {"events": events}
    except Exception as e:
        return {"events": [], "error": str(e)}
```

- [ ] **Step 3: Register timeline router in `backend/app/main.py`**

```python
from app.api.timeline import router as timeline_router
app.include_router(timeline_router)
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: sources, follow-up, and timeline API endpoints"
```

---

## Phase 5: Frontend Foundation

### Task 13: Next.js project setup with Tailwind and shadcn/ui

**Files:**
- Create: `frontend/tsconfig.json`
- Create: `frontend/next.config.ts`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/postcss.config.js`
- Create: `frontend/src/styles/globals.css`
- Create: `frontend/src/lib/utils.ts`
- Create: `frontend/src/lib/types.ts`
- Modify: `frontend/package.json`

- [ ] **Step 1: Create `frontend/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 2: Create `frontend/next.config.ts`**

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://backend:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
```

- [ ] **Step 3: Create `frontend/tailwind.config.ts`**

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: { DEFAULT: "hsl(var(--primary))", foreground: "hsl(var(--primary-foreground))" },
        muted: { DEFAULT: "hsl(var(--muted))", foreground: "hsl(var(--muted-foreground))" },
        accent: { DEFAULT: "hsl(var(--accent))", foreground: "hsl(var(--accent-foreground))" },
      },
    },
  },
  plugins: [],
};

export default config;
```

- [ ] **Step 4: Create `frontend/postcss.config.js`**

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

- [ ] **Step 5: Create `frontend/src/styles/globals.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222 47% 11%;
    --primary: 215 70% 35%;
    --primary-foreground: 0 0% 100%;
    --muted: 210 40% 96%;
    --muted-foreground: 215 16% 47%;
    --accent: 142 71% 40%;
    --accent-foreground: 0 0% 100%;
    --border: 214 32% 91%;
  }
}

body {
  @apply bg-background text-foreground antialiased;
}
```

- [ ] **Step 6: Create `frontend/src/lib/utils.ts`**

```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

- [ ] **Step 7: Create `frontend/src/lib/types.ts`**

```typescript
/** Data source selection for a research request */
export interface DataSourceConfig {
  akshare: boolean;
  news: boolean;
  uploadedDocs: string[];
}

/** A citation linking report text to source document */
export interface Citation {
  ref_id: string;
  doc_id: string;
  chunk_index: number;
  text: string;
  page?: number;
  confidence: number;
}

/** SSE event types from the backend */
export type SSEEvent =
  | { type: "phase"; phase: "bull" | "bear" | "factcheck" | "synthesize" | "done" }
  | { type: "agent_progress"; agent: string; chunk: string }
  | { type: "citation"; ref_id: string; source: Citation }
  | { type: "warning"; message: string; location: string }
  | { type: "error"; message: string }
  | { type: "complete"; report_id: string };

/** Full research report */
export interface ResearchReport {
  task_id: string;
  query: string;
  markdown: string;
  citations: Record<string, Citation>;
  bull_view?: string;
  bear_view?: string;
  factcheck_notes: string[];
  created_at: string;
}

/** Timeline event */
export interface TimelineEvent {
  date: string;
  event: string;
  type: "financial" | "management" | "market" | "other";
  causes: string[];
  effects: string[];
  source_ref?: string;
}
```

- [ ] **Step 8: Commit**

```bash
git add -A && git commit -m "feat: Next.js project setup with Tailwind, shadcn/ui config, and types"
```

---

### Task 14: Next.js app layout and API client

**Files:**
- Create: `frontend/src/app/layout.tsx`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/lib/sse.ts`

- [ ] **Step 1: Create `frontend/src/app/layout.tsx`**

```tsx
import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "FinDeep - AI深度研报",
  description: "AI驱动的多智能体协作金融研究报告自动生成平台",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-background text-foreground">
        <header className="border-b border-border px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center gap-2">
            <span className="text-2xl font-bold text-primary">FinDeep</span>
            <span className="text-sm text-muted-foreground">金融深研</span>
          </div>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

- [ ] **Step 2: Create `frontend/src/lib/api.ts`**

```typescript
import { DataSourceConfig, ResearchReport, Citation, TimelineEvent } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  /** Initiate a new research task */
  startResearch: (query: string, dataSources: DataSourceConfig) =>
    request<{ task_id: string; status: string }>("/api/research", {
      method: "POST",
      body: JSON.stringify({ query, data_sources: dataSources }),
    }),

  /** Get the final research report */
  getReport: (taskId: string) => request<ResearchReport>(`/api/report/${taskId}`),

  /** Get a specific citation source */
  getSource: (citationId: string) => request<Citation>(`/api/sources/${citationId}`),

  /** Ask a follow-up question */
  askFollowUp: (taskId: string, question: string) =>
    request<{ answer: string; task_id: string }>("/api/ask", {
      method: "POST",
      body: JSON.stringify({ task_id: taskId, question }),
    }),

  /** Get event timeline */
  getTimeline: (taskId: string) =>
    request<{ events: TimelineEvent[] }>(`/api/timeline/${taskId}`),

  /** Upload a document */
  uploadDocument: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE_URL}/api/upload`, { method: "POST", body: form });
    if (!res.ok) throw new Error("Upload failed");
    return res.json() as Promise<{ doc_id: string; filename: string; pages: number }>;
  },

  /** Get SSE stream URL */
  streamUrl: (taskId: string) => `${BASE_URL}/api/research/${taskId}/stream`,
};
```

- [ ] **Step 3: Create `frontend/src/lib/sse.ts`**

```typescript
import { SSEEvent } from "./types";

type EventHandler = (event: SSEEvent) => void;

export function createSSEConnection(url: string, onEvent: EventHandler): () => void {
  const eventSource = new EventSource(url);

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as SSEEvent;
      onEvent(data);
    } catch {
      // ignore parse errors on incomplete chunks
    }
  };

  eventSource.onerror = () => {
    onEvent({ type: "error", message: "Connection lost. Retrying..." });
  };

  return () => eventSource.close();
}
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: app layout, API client, and SSE connection helper"
```

---

## Phase 6: Frontend Pages and Components

### Task 15: SearchPage — search bar, data source toggles, file upload

**Files:**
- Create: `frontend/src/app/page.tsx`
- Create: `frontend/src/components/SearchBar.tsx`
- Create: `frontend/src/components/DataSourceToggle.tsx`
- Create: `frontend/src/components/FileUpload.tsx`

- [ ] **Step 1: Create `frontend/src/components/SearchBar.tsx`**

```tsx
"use client";

import { useState } from "react";
import { Search } from "lucide-react";

interface Props {
  onSearch: (query: string) => void;
  loading: boolean;
}

export function SearchBar({ onSearch, loading }: Props) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) onSearch(value.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="输入公司名称、行业或股票代码... 如：宁德时代 300750"
          className="w-full pl-12 pr-24 py-4 rounded-xl border border-border bg-white text-lg
                     focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary
                     placeholder:text-muted-foreground/60"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !value.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2 rounded-lg
                     bg-primary text-primary-foreground font-medium
                     hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed
                     transition-colors"
        >
          {loading ? "分析中..." : "开始研究"}
        </button>
      </div>
    </form>
  );
}
```

- [ ] **Step 2: Create `frontend/src/components/DataSourceToggle.tsx`**

```tsx
"use client";

import { Database, Newspaper } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  akshare: boolean;
  news: boolean;
  onAkshareChange: (v: boolean) => void;
  onNewsChange: (v: boolean) => void;
}

export function DataSourceToggle({ akshare, news, onAkshareChange, onNewsChange }: Props) {
  return (
    <div className="flex gap-4 items-center">
      <span className="text-sm text-muted-foreground">数据源：</span>
      <button
        onClick={() => onAkshareChange(!akshare)}
        className={cn(
          "flex items-center gap-2 px-4 py-2 rounded-lg border text-sm transition-colors",
          akshare
            ? "border-primary bg-primary/5 text-primary"
            : "border-border text-muted-foreground hover:border-primary/30"
        )}
      >
        <Database className="w-4 h-4" />
        金融数据API
        {akshare && <span className="text-green-500">✓</span>}
      </button>
      <button
        onClick={() => onNewsChange(!news)}
        className={cn(
          "flex items-center gap-2 px-4 py-2 rounded-lg border text-sm transition-colors",
          news
            ? "border-primary bg-primary/5 text-primary"
            : "border-border text-muted-foreground hover:border-primary/30"
        )}
      >
        <Newspaper className="w-4 h-4" />
        新闻舆情
        {news && <span className="text-green-500">✓</span>}
      </button>
    </div>
  );
}
```

- [ ] **Step 3: Create `frontend/src/components/FileUpload.tsx`**

```tsx
"use client";

import { useState, useCallback } from "react";
import { Upload, FileText, X } from "lucide-react";
import { api } from "@/lib/api";

interface UploadedFile {
  doc_id: string;
  filename: string;
  pages: number;
}

interface Props {
  files: UploadedFile[];
  onChange: (files: UploadedFile[]) => void;
}

export function FileUpload({ files, onChange }: Props) {
  const [uploading, setUploading] = useState(false);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      const droppedFiles = Array.from(e.dataTransfer.files);
      await uploadFiles(droppedFiles);
    },
    [files]
  );

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || []);
    await uploadFiles(selected);
  };

  const uploadFiles = async (fileList: File[]) => {
    setUploading(true);
    for (const file of fileList) {
      try {
        const result = await api.uploadDocument(file);
        onChange([...files, result]);
      } catch (err) {
        console.error("Upload failed:", file.name, err);
      }
    }
    setUploading(false);
  };

  const removeFile = (docId: string) => {
    onChange(files.filter((f) => f.doc_id !== docId));
  };

  return (
    <div>
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className="border-2 border-dashed border-border rounded-xl p-6 text-center
                   hover:border-primary/40 transition-colors cursor-pointer"
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept=".pdf,.txt,.md,.csv"
          multiple
          onChange={handleFileInput}
        />
        <label htmlFor="file-upload" className="cursor-pointer">
          <Upload className="w-6 h-6 mx-auto mb-2 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            {uploading ? "上传中..." : "拖拽PDF/文档到此处，或点击选择"}
          </p>
          <p className="text-xs text-muted-foreground/60 mt-1">支持 PDF、TXT、Markdown、CSV</p>
        </label>
      </div>

      {files.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {files.map((f) => (
            <div
              key={f.doc_id}
              className="flex items-center gap-2 px-3 py-1.5 bg-muted rounded-lg text-sm"
            >
              <FileText className="w-4 h-4 text-primary" />
              <span>{f.filename}</span>
              <span className="text-muted-foreground">({f.pages}页)</span>
              <button onClick={() => removeFile(f.doc_id)} className="hover:text-red-500">
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Create `frontend/src/app/page.tsx`**

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { SearchBar } from "@/components/SearchBar";
import { DataSourceToggle } from "@/components/DataSourceToggle";
import { FileUpload } from "@/components/FileUpload";
import { api } from "@/lib/api";

interface UploadedFile {
  doc_id: string;
  filename: string;
  pages: number;
}

export default function SearchPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [akshare, setAkshare] = useState(true);
  const [news, setNews] = useState(true);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [error, setError] = useState("");

  const handleSearch = async (query: string) => {
    if (!akshare && !news && files.length === 0) {
      setError("请至少选择一个数据源或上传文档");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const { task_id } = await api.startResearch(query, {
        akshare,
        news,
        uploadedDocs: files.map((f) => f.doc_id),
      });
      router.push(`/report/${task_id}`);
    } catch (err: any) {
      setError(err.message || "启动研究失败");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-20">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-3">AI驱动的深度金融研报</h1>
        <p className="text-lg text-muted-foreground">
          多智能体对抗性辩论 · 溯源锚定 · 事件链推理
        </p>
      </div>

      <div className="space-y-6">
        <SearchBar onSearch={handleSearch} loading={loading} />

        <DataSourceToggle
          akshare={akshare}
          news={news}
          onAkshareChange={setAkshare}
          onNewsChange={setNews}
        />

        <FileUpload files={files} onChange={setFiles} />

        {error && (
          <div className="p-3 rounded-lg bg-red-50 text-red-600 text-sm">{error}</div>
        )}
      </div>

      <div className="mt-16 grid grid-cols-3 gap-6">
        {[
          { title: "🐂 多方博弈", desc: "Bull/Bear并行分析，模拟真实投资辩论" },
          { title: "🔍 事实核查", desc: "逐条验证数据来源，⚠️标注无支撑推断" },
          { title: "📎 溯源锚定", desc: "点击分析文字，右侧面板高亮原文出处" },
        ].map((f) => (
          <div key={f.title} className="p-4 rounded-xl bg-muted/50 border border-border">
            <h3 className="font-semibold mb-1">{f.title}</h3>
            <p className="text-sm text-muted-foreground">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: SearchPage with search bar, data source toggles, and file upload"
```

---

### Task 16: ReportPage — SSE progress panel and AgentCards

**Files:**
- Create: `frontend/src/app/report/[taskId]/page.tsx`
- Create: `frontend/src/components/ProgressPanel.tsx`
- Create: `frontend/src/components/AgentCard.tsx`

- [ ] **Step 1: Create `frontend/src/components/AgentCard.tsx`**

```tsx
"use client";

import { cn } from "@/lib/utils";
import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";

interface Props {
  agent: string;
  label: string;
  icon: string;
  status: "idle" | "running" | "done";
  output: string;
}

export function AgentCard({ agent, label, icon, status, output }: Props) {
  return (
    <div
      className={cn(
        "p-4 rounded-xl border transition-all",
        status === "running" && "border-primary/40 bg-primary/5 shadow-sm",
        status === "done" && "border-green-200 bg-green-50/50",
        status === "idle" && "border-border bg-white opacity-60"
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <span className="font-semibold text-sm">{label}</span>
        </div>
        {status === "running" && <Loader2 className="w-4 h-4 animate-spin text-primary" />}
        {status === "done" && <CheckCircle2 className="w-4 h-4 text-green-500" />}
      </div>
      {output && (
        <div className="text-sm text-muted-foreground whitespace-pre-wrap line-clamp-4 max-h-24 overflow-y-auto">
          {output}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create `frontend/src/components/ProgressPanel.tsx`**

```tsx
"use client";

import { AgentCard } from "./AgentCard";

interface Props {
  phase: string;
  agentOutputs: Record<string, string>;
}

const AGENTS = [
  { key: "bull", label: "多方分析师", icon: "🐂" },
  { key: "bear", label: "空方分析师", icon: "🐻" },
  { key: "factcheck", label: "事实核查员", icon: "🔍" },
  { key: "synthesizer", label: "综合编辑", icon: "📝" },
];

export function ProgressPanel({ phase, agentOutputs }: Props) {
  const getStatus = (agentKey: string) => {
    if (agentOutputs[agentKey] && phase === "done") return "done";
    if (phase === agentKey) return "running";
    const order = ["bull", "bear", "factcheck", "synthesizer"];
    const phaseIdx = order.indexOf(phase);
    const agentIdx = order.indexOf(agentKey);
    if (agentIdx < phaseIdx) return "done";
    if (agentIdx === phaseIdx) return "running";
    return "idle";
  };

  return (
    <div className="grid grid-cols-2 gap-3 mb-6">
      {AGENTS.map((a) => (
        <AgentCard
          key={a.key}
          agent={a.key}
          label={a.label}
          icon={a.icon}
          status={getStatus(a.key)}
          output={agentOutputs[a.key] || ""}
        />
      ))}
    </div>
  );
}
```

- [ ] **Step 3: Create `frontend/src/app/report/[taskId]/page.tsx`**

```tsx
"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { createSSEConnection } from "@/lib/sse";
import { ResearchReport, Citation, SSEEvent } from "@/lib/types";
import { ProgressPanel } from "@/components/ProgressPanel";
import { ReportContent } from "@/components/ReportContent";
import { SidePanel } from "@/components/SidePanel";
import { AskFollowUp } from "@/components/AskFollowUp";
import { ViewToggle } from "@/components/ViewToggle";

export default function ReportPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const [phase, setPhase] = useState<string>("bull");
  const [agentOutputs, setAgentOutputs] = useState<Record<string, string>>({});
  const [citations, setCitations] = useState<Record<string, Citation>>({});
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"sources" | "timeline">("sources");
  const [selectedRef, setSelectedRef] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"balanced" | "bull" | "bear">("balanced");
  const [followUpAnswer, setFollowUpAnswer] = useState("");

  useEffect(() => {
    const close = createSSEConnection(api.streamUrl(taskId), (event: SSEEvent) => {
      switch (event.type) {
        case "phase":
          setPhase(event.phase);
          break;
        case "agent_progress":
          setAgentOutputs((prev) => ({
            ...prev,
            [event.agent]: (prev[event.agent] || "") + event.chunk,
          }));
          break;
        case "citation":
          setCitations((prev) => ({ ...prev, [event.ref_id]: event.source }));
          break;
        case "warning":
          // Warnings are embedded in the factcheck output
          break;
        case "error":
          setError(event.message);
          break;
        case "complete":
          setPhase("done");
          loadReport();
          break;
      }
    });
    return close;
  }, [taskId]);

  const loadReport = async () => {
    try {
      const r = await api.getReport(taskId);
      setReport(r);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleCitationClick = (refId: string) => {
    setSelectedRef(refId);
    setActiveTab("sources");
  };

  const handleFollowUp = async (question: string) => {
    try {
      const { answer } = await api.askFollowUp(taskId, question);
      setFollowUpAnswer(answer);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleViewChange = (mode: "balanced" | "bull" | "bear") => {
    setViewMode(mode);
  };

  if (error && !report) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-20 text-center">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  const displayContent = (() => {
    if (!report) return "";
    switch (viewMode) {
      case "bull": return report.bull_view || "Bull分析生成中...";
      case "bear": return report.bear_view || "Bear分析生成中...";
      default: return report.markdown;
    }
  })();

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">研究报告：{report?.query || "..."}</h1>
      </div>

      {phase !== "done" && (
        <ProgressPanel phase={phase} agentOutputs={agentOutputs} />
      )}

      <div className="flex gap-6">
        <div className="flex-1 min-w-0">
          <ReportContent
            markdown={displayContent}
            citations={citations}
            onCitationClick={handleCitationClick}
          />
          {followUpAnswer && (
            <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-100">
              <h3 className="font-semibold mb-2">💬 追问回复</h3>
              <div className="text-sm whitespace-pre-wrap">{followUpAnswer}</div>
            </div>
          )}
          <div className="mt-6">
            <AskFollowUp onSubmit={handleFollowUp} loading={false} />
          </div>
        </div>

        <SidePanel
          activeTab={activeTab}
          onTabChange={setActiveTab}
          citations={citations}
          selectedRef={selectedRef}
          taskId={taskId}
        />
      </div>

      <div className="fixed bottom-6 right-6">
        <ViewToggle active={viewMode} onChange={handleViewChange} />
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: ReportPage with SSE progress panel and AgentCards"
```

---

### Task 17: ReportContent, SidePanel, SourceTracing, EventTimeline

**Files:**
- Create: `frontend/src/components/ReportContent.tsx`
- Create: `frontend/src/components/SidePanel.tsx`
- Create: `frontend/src/components/SourceTracing.tsx`
- Create: `frontend/src/components/EventTimeline.tsx`

- [ ] **Step 1: Create `frontend/src/components/ReportContent.tsx`**

```tsx
"use client";

import ReactMarkdown from "react-markdown";
import { Citation } from "@/lib/types";

interface Props {
  markdown: string;
  citations: Record<string, Citation>;
  onCitationClick: (refId: string) => void;
}

export function ReportContent({ markdown, citations, onCitationClick }: Props) {
  if (!markdown) {
    return (
      <div className="flex items-center justify-center h-64 text-muted-foreground">
        等待报告生成...
      </div>
    );
  }

  return (
    <div className="prose prose-slate max-w-none">
      <ReactMarkdown
        components={{
          // Make citation references clickable: [ref:abc123]
          a: ({ href, children, ...props }) => {
            const refMatch = href?.match(/ref:([a-f0-9]+)/);
            if (refMatch) {
              const refId = refMatch[1];
              const citation = citations[refId];
              return (
                <button
                  onClick={() => onCitationClick(refId)}
                  className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded
                             bg-blue-50 text-blue-600 text-xs font-mono
                             hover:bg-blue-100 transition-colors"
                  title={citation?.text?.slice(0, 200)}
                >
                  [{refId}]
                </button>
              );
            }
            return <a href={href} {...props}>{children}</a>;
          },
          // Replace ⚠️ with styled warning
          p: ({ children, ...props }) => {
            const text = String(children);
            if (text.includes("⚠️") || text.includes("⚠")) {
              return (
                <p {...props} className="bg-amber-50 border-l-4 border-amber-400 pl-4 py-2 my-2">
                  {children}
                </p>
              );
            }
            return <p {...props}>{children}</p>;
          },
        }}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}
```

- [ ] **Step 2: Create `frontend/src/components/SidePanel.tsx`**

```tsx
"use client";

import { Citation, TimelineEvent } from "@/lib/types";
import { SourceTracing } from "./SourceTracing";
import { EventTimeline } from "./EventTimeline";

interface Props {
  activeTab: "sources" | "timeline";
  onTabChange: (tab: "sources" | "timeline") => void;
  citations: Record<string, Citation>;
  selectedRef: string | null;
  taskId: string;
}

export function SidePanel({ activeTab, onTabChange, citations, selectedRef, taskId }: Props) {
  return (
    <div className="w-96 shrink-0 border border-border rounded-xl bg-white overflow-hidden">
      <div className="flex border-b border-border">
        <button
          onClick={() => onTabChange("sources")}
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === "sources"
              ? "text-primary border-b-2 border-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          溯源面板
        </button>
        <button
          onClick={() => onTabChange("timeline")}
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === "timeline"
              ? "text-primary border-b-2 border-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          事件时间轴
        </button>
      </div>
      <div className="p-4 h-[calc(100vh-280px)] overflow-y-auto">
        {activeTab === "sources" ? (
          <SourceTracing citations={citations} selectedRef={selectedRef} />
        ) : (
          <EventTimeline taskId={taskId} />
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create `frontend/src/components/SourceTracing.tsx`**

```tsx
"use client";

import { Citation } from "@/lib/types";
import { FileText } from "lucide-react";

interface Props {
  citations: Record<string, Citation>;
  selectedRef: string | null;
}

export function SourceTracing({ citations, selectedRef }: Props) {
  const entries = Object.entries(citations);

  if (entries.length === 0) {
    return <p className="text-sm text-muted-foreground text-center py-8">暂无引用来源</p>;
  }

  return (
    <div className="space-y-3">
      {selectedRef && citations[selectedRef] && (
        <div className="p-3 rounded-lg bg-primary/5 border border-primary/20 mb-4">
          <p className="text-xs font-semibold text-primary mb-1">📍 当前选中引用</p>
          <p className="text-sm">{citations[selectedRef].text}</p>
          <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
            <span>ID: {selectedRef}</span>
            {citations[selectedRef].page && <span>页码: {citations[selectedRef].page}</span>}
            <span>置信度: {(citations[selectedRef].confidence * 100).toFixed(0)}%</span>
          </div>
        </div>
      )}
      {entries.map(([refId, c]) => (
        <div
          key={refId}
          id={`source-${refId}`}
          className={`p-3 rounded-lg border text-sm transition-colors ${
            selectedRef === refId
              ? "border-primary bg-primary/5 ring-1 ring-primary"
              : "border-border hover:border-primary/30"
          }`}
        >
          <div className="flex items-center gap-2 mb-1">
            <FileText className="w-3 h-3 text-muted-foreground" />
            <span className="text-xs font-mono text-primary">[{refId}]</span>
            <span className="text-xs text-muted-foreground">
              {c.page ? `第${c.page}页` : `片段#${c.chunk_index}`}
            </span>
          </div>
          <p className="text-sm leading-relaxed">{c.text}</p>
          {c.doc_id && (
            <p className="text-xs text-muted-foreground mt-1">来源: {c.doc_id}</p>
          )}
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 4: Create `frontend/src/components/EventTimeline.tsx`**

```tsx
"use client";

import { useEffect, useState } from "react";
import { TimelineEvent } from "@/lib/types";
import { api } from "@/lib/api";
import { Calendar, ChevronRight } from "lucide-react";

interface Props {
  taskId: string;
}

export function EventTimeline({ taskId }: Props) {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getTimeline(taskId).then((data) => {
      setEvents(data.events || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [taskId]);

  if (loading) {
    return <p className="text-sm text-muted-foreground text-center py-8">加载时间轴中...</p>;
  }

  if (events.length === 0) {
    return <p className="text-sm text-muted-foreground text-center py-8">暂无事件链数据</p>;
  }

  const typeColors: Record<string, string> = {
    financial: "bg-blue-100 text-blue-700",
    management: "bg-purple-100 text-purple-700",
    market: "bg-green-100 text-green-700",
    other: "bg-gray-100 text-gray-700",
  };

  return (
    <div className="relative pl-6 border-l-2 border-border space-y-6">
      {events.map((event, i) => (
        <div key={i} className="relative">
          <div className="absolute -left-[25px] top-1 w-3 h-3 rounded-full bg-primary border-2 border-white" />
          <div className="flex items-center gap-2 mb-1">
            <Calendar className="w-3 h-3 text-muted-foreground" />
            <span className="text-xs font-medium text-muted-foreground">{event.date}</span>
            <span className={`text-xs px-1.5 py-0.5 rounded ${typeColors[event.type] || typeColors.other}`}>
              {event.type}
            </span>
          </div>
          <p className="text-sm font-medium">{event.event}</p>
          {event.causes.length > 0 && (
            <p className="text-xs text-muted-foreground mt-1">
              原因: {event.causes.join(", ")}
            </p>
          )}
          {event.effects.length > 0 && (
            <div className="flex items-start gap-1 mt-1">
              <ChevronRight className="w-3 h-3 text-muted-foreground mt-0.5" />
              <p className="text-xs text-muted-foreground">
                导致: {event.effects.join(", ")}
              </p>
            </div>
          )}
          {event.source_ref && (
            <span className="text-xs font-mono text-primary mt-1 inline-block">
              [{event.source_ref}]
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: ReportContent, SidePanel, SourceTracing, and EventTimeline components"
```

---

### Task 18: AskFollowUp and ViewToggle components

**Files:**
- Create: `frontend/src/components/AskFollowUp.tsx`
- Create: `frontend/src/components/ViewToggle.tsx`

- [ ] **Step 1: Create `frontend/src/components/AskFollowUp.tsx`**

```tsx
"use client";

import { useState } from "react";
import { Send } from "lucide-react";

interface Props {
  onSubmit: (question: string) => void;
  loading: boolean;
}

export function AskFollowUp({ onSubmit, loading }: Props) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) {
      onSubmit(value.trim());
      setValue("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="💬 追问更多细节... 如：海外扩张进展如何？"
        className="flex-1 px-4 py-3 rounded-xl border border-border
                   focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary
                   text-sm"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !value.trim()}
        className="px-4 py-3 rounded-xl bg-primary text-primary-foreground
                   hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed
                   transition-colors"
      >
        <Send className="w-4 h-4" />
      </button>
    </form>
  );
}
```

- [ ] **Step 2: Create `frontend/src/components/ViewToggle.tsx`**

```tsx
"use client";

import { cn } from "@/lib/utils";

interface Props {
  active: "balanced" | "bull" | "bear";
  onChange: (mode: "balanced" | "bull" | "bear") => void;
}

const OPTIONS = [
  { key: "bull" as const, label: "🐂 多方", desc: "投资机会视角" },
  { key: "balanced" as const, label: "⚖ 均衡", desc: "综合报告" },
  { key: "bear" as const, label: "🐻 空方", desc: "风险警示视角" },
];

export function ViewToggle({ active, onChange }: Props) {
  return (
    <div className="flex gap-1 bg-muted p-1 rounded-xl shadow-lg">
      {OPTIONS.map((opt) => (
        <button
          key={opt.key}
          onClick={() => onChange(opt.key)}
          className={cn(
            "px-4 py-2 rounded-lg text-sm font-medium transition-all",
            active === opt.key
              ? "bg-white text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          )}
          title={opt.desc}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: AskFollowUp and ViewToggle components"
```

---

### Task 19: History page

**Files:**
- Create: `frontend/src/app/history/page.tsx`

- [ ] **Step 1: Create `frontend/src/app/history/page.tsx`**

```tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FileText, Clock } from "lucide-react";
import { ResearchReport } from "@/lib/types";

export default function HistoryPage() {
  const [reports, setReports] = useState<ResearchReport[]>([]);

  // Note: in MVP, history comes from localStorage since backend is in-memory
  useEffect(() => {
    const stored = localStorage.getItem("findeep_history");
    if (stored) {
      try {
        setReports(JSON.parse(stored));
      } catch {}
    }
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <h1 className="text-2xl font-bold mb-8">历史研报</h1>

      {reports.length === 0 ? (
        <div className="text-center py-20 text-muted-foreground">
          <FileText className="w-16 h-16 mx-auto mb-4 opacity-30" />
          <p>暂无历史研报</p>
          <Link href="/" className="text-primary hover:underline mt-2 inline-block">
            开始第一份研究 →
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {reports.map((r) => (
            <Link
              key={r.task_id}
              href={`/report/${r.task_id}`}
              className="block p-4 rounded-xl border border-border hover:border-primary/30 hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-primary" />
                  <span className="font-medium">{r.query}</span>
                </div>
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <Clock className="w-3 h-3" />
                  <span>{r.created_at.slice(0, 10)}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add -A && git commit -m "feat: History page with localStorage-based report list"
```

---

## Phase 7: Docker and Integration

### Task 20: Dockerfiles and final docker-compose refinement

**Files:**
- Create: `frontend/Dockerfile`
- Create: `backend/Dockerfile`
- Modify: `docker-compose.yml`

- [ ] **Step 1: Create `frontend/Dockerfile`**

```dockerfile
FROM node:20-alpine AS base

FROM base AS deps
WORKDIR /app
COPY package.json ./
RUN npm install

FROM base AS dev
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
CMD ["npm", "run", "dev"]
```

- [ ] **Step 2: Create `backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data/chroma

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Update `docker-compose.yml`**

Ensure it reads:

```yaml
version: "3.9"

services:
  frontend:
    build:
      context: ./frontend
      target: dev
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/package.json:/app/package.json

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      - CHROMA_HOST=chromadb
      - CHROMA_PORT=8000
    depends_on:
      chromadb:
        condition: service_healthy
    volumes:
      - ./backend/app:/app/app
      - backend_data:/app/data

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  chroma_data:
  backend_data:
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: Dockerfiles and refined docker-compose for full stack"
```

---

### Task 21: Final integration — history persistence and error boundaries

**Files:**
- Create: `frontend/src/components/ErrorBoundary.tsx`
- Modify: `frontend/src/app/report/[taskId]/page.tsx` (add history save)

- [ ] **Step 1: Create `frontend/src/components/ErrorBoundary.tsx`**

```tsx
"use client";

import { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: string;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: "" };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error: error.message };
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="p-8 text-center">
            <p className="text-red-500 mb-2">页面发生错误</p>
            <p className="text-sm text-muted-foreground">{this.state.error}</p>
            <button
              onClick={() => this.setState({ hasError: false, error: "" })}
              className="mt-4 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm"
            >
              重试
            </button>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
```

- [ ] **Step 2: Add history persistence to report page**

In `frontend/src/app/report/[taskId]/page.tsx`, in the `loadReport` function after `setReport(r)`:

```typescript
// Save to history
const stored = localStorage.getItem("findeep_history");
const history = stored ? JSON.parse(stored) : [];
const existing = history.findIndex((h: any) => h.task_id === r.task_id);
if (existing >= 0) {
  history[existing] = { task_id: r.task_id, query: r.query, created_at: r.created_at };
} else {
  history.unshift({ task_id: r.task_id, query: r.query, created_at: r.created_at });
}
localStorage.setItem("findeep_history", JSON.stringify(history.slice(0, 20)));
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: error boundary and history persistence"
```

---

### Task 22: Quick verification smoke test

- [ ] **Step 1: Verify backend imports work**

```bash
cd backend && python -c "
from app.config import settings
from app.models.research import ResearchRequest, DataSourceConfig
from app.llm.provider import get_llm
print('All imports OK')
print(f'LLM provider: {settings.llm_provider}')
"
```

- [ ] **Step 2: Verify frontend builds**

```bash
cd frontend && npm install && npm run build 2>&1 | tail -5
```

- [ ] **Step 3: Verify docker compose config**

```bash
docker compose config 2>&1 | head -5
# Should print the parsed docker compose configuration
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "chore: verify all imports and builds pass"
```

---

## Appendix A: Running the App

```bash
# 1. Configure API keys
cp .env.example .env
# Edit .env with your actual API keys

# 2. Start all services
docker compose up

# 3. Open browser
# http://localhost:3000
```

## Appendix B: Test Commands

```bash
# Backend unit tests (under development)
cd backend && python -m pytest tests/ -v

# Frontend unit tests (under development)
cd frontend && npx vitest run
```

## Appendix C: File Index

| # | File | Purpose |
|---|------|---------|
| 1 | `docker-compose.yml` | 3-service orchestration |
| 2 | `.env.example` | Configuration template |
| 3 | `backend/app/main.py` | FastAPI entry point |
| 4 | `backend/app/config.py` | Settings from environment |
| 5 | `backend/app/models/research.py` | Pydantic data models |
| 6 | `backend/app/models/schemas.py` | API request/response schemas |
| 7 | `backend/app/llm/provider.py` | LLM factory + per-agent config |
| 8 | `backend/app/llm/providers/*.py` | Claude, OpenAI, DeepSeek, Custom |
| 9 | `backend/app/rag/engine.py` | Multi-source RAG engine |
| 10 | `backend/app/rag/citation.py` | Citation tracking |
| 11 | `backend/app/rag/datasources/base.py` | Data source interface |
| 12 | `backend/app/rag/datasources/akshare.py` | A-share financial data |
| 13 | `backend/app/rag/datasources/news.py` | News context adapter |
| 14 | `backend/app/rag/datasources/user_upload.py` | Uploaded doc search |
| 15 | `backend/app/api/upload.py` | File upload + vectorization |
| 16 | `backend/app/api/research.py` | Research + SSE + report endpoints |
| 17 | `backend/app/api/timeline.py` | Event timeline extraction |
| 18 | `backend/app/agents/graph.py` | LangGraph multi-agent orchestration |
| 19 | `backend/app/agents/bull_agent.py` | Bull analyst agent |
| 20 | `backend/app/agents/bear_agent.py` | Bear analyst agent |
| 21 | `backend/app/agents/factcheck_agent.py` | Fact checker agent |
| 22 | `backend/app/agents/synthesizer_agent.py` | Synthesizer agent |
| 23 | `backend/app/agents/followup_agent.py` | Follow-up Q&A agent |
| 24 | `frontend/src/app/layout.tsx` | Root layout |
| 25 | `frontend/src/app/page.tsx` | Search page |
| 26 | `frontend/src/app/report/[taskId]/page.tsx` | Report page |
| 27 | `frontend/src/app/history/page.tsx` | History page |
| 28 | `frontend/src/lib/types.ts` | TypeScript types |
| 29 | `frontend/src/lib/api.ts` | API client |
| 30 | `frontend/src/lib/sse.ts` | SSE connection helper |
| 31-41 | `frontend/src/components/*.tsx` | 11 UI components |
