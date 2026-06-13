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
