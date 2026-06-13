"""Citation mapping system -- links report claims to source documents."""
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
