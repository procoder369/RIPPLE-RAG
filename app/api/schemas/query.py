"""Pydantic schemas for story QA query requests and responses."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class StoryQueryRequest(BaseModel):
    story_id: str = Field(..., description="Target story identifier")
    query: str = Field(..., min_length=3, description="Writer question about lore, plot, or character")
    top_k: int = Field(default=4, ge=1, le=20, description="Number of evidence chunks to retrieve")


class CitationItem(BaseModel):
    source_index: int
    chunk_id: str
    chapter_id: str
    scene_number: int
    score: float
    preview: str


class StoryQueryResponse(BaseModel):
    query: str
    answer: str
    verified: bool
    verification_details: Dict[str, Any]
    citations: List[CitationItem]
    graph_evidence: Optional[Dict[str, Any]] = None

