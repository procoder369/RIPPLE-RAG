"""Pydantic schemas for story indexing requests and responses."""

from pydantic import BaseModel, Field


class IndexChapterRequest(BaseModel):
    story_id: str = Field(..., description="Unique story or manuscript identifier")
    chapter_index: int = Field(..., ge=1, description="Chapter sequence number (1-based)")
    chapter_title: str = Field(..., description="Title of the chapter")
    raw_text: str = Field(..., min_length=10, description="Full chapter manuscript text")


class IndexChapterResponse(BaseModel):
    status: str
    story_id: str
    chapter_id: str
    chapter_index: int
    chunks_indexed: int
    facts_proposed: int

