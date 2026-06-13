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
