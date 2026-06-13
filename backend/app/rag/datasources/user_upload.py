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
