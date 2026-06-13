"""RAG engine integrating LlamaIndex with ChromaDB and multi-source retrieval."""
import os
import uuid
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings as app_settings
from app.rag.datasources.base import DataSourceAdapter, Document
from app.rag.datasources import AkShareAdapter, NewsSearchAdapter, UserUploadAdapter
from app.rag.citation import CitationManager
from app.models.research import DataSourceConfig


def _get_chroma_client():
    """Get ChromaDB client based on configured mode — local (zero-dep) or docker."""
    if app_settings.chroma_mode == "docker":
        return chromadb.HttpClient(
            host=app_settings.chroma_host,
            port=app_settings.chroma_port,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    else:
        # 本地模式：数据存在项目目录下，无需额外服务
        os.makedirs(app_settings.chroma_data_dir, exist_ok=True)
        return chromadb.PersistentClient(
            path=app_settings.chroma_data_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )


class RAGEngine:
    """Orchestrates multi-source document retrieval and citation tracking."""

    def __init__(self, data_sources: DataSourceConfig):
        self.data_sources = data_sources
        self.adapters: List[DataSourceAdapter] = []
        self.citations = CitationManager()

        # Initialize ChromaDB client (auto-detects local/docker mode)
        self.chroma_client = _get_chroma_client()

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
