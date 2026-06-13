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
