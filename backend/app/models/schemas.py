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
