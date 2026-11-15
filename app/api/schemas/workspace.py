"""Pydantic schemas for story workspace, chapter management, and manuscript operations."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CreateStoryRequest(BaseModel):
    title: str = Field(..., example="The Chronicles of Eldoria")
    description: Optional[str] = Field(None, example="An epic high-fantasy saga of forgotten gods and warring kingdoms.")
    author_id: Optional[str] = Field("Author", example="author-123")


class StoryResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    author_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChapterSummary(BaseModel):
    id: str
    chapter_index: int
    title: str
    word_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChapterDetailResponse(BaseModel):
    id: str
    story_id: str
    chapter_index: int
    title: str
    raw_text: str
    word_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class CreateChapterRequest(BaseModel):
    title: str = Field(..., example="Chapter 1: The Broken Oath")
    chapter_index: int = Field(..., example=1)
    raw_text: str = Field(..., example="The wind howled across the frozen spires...")


class UpdateChapterRequest(BaseModel):
    title: Optional[str] = None
    raw_text: Optional[str] = None
    chapter_index: Optional[int] = None
    commit_message: Optional[str] = Field(None, example="Update battle scene and fix dialogue")


class ReorderChaptersRequest(BaseModel):
    chapter_order: List[str] = Field(..., description="List of Chapter IDs in the desired new sequence")


class ManuscriptResponse(BaseModel):
    story_id: str
    story_title: str
    total_chapters: int
    total_words: int
    chapters: List[ChapterDetailResponse]

