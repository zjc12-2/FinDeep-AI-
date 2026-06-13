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
