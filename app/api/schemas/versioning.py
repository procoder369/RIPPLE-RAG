"""Pydantic schemas for version control, commits, diffs, and branch/history tracking."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CreateCommitRequest(BaseModel):
    story_id: str
    chapter_id: Optional[str] = None
    message: str = Field(..., example="Revise duel outcome in chapter 3")
    author: Optional[str] = "Author"
    branch: Optional[str] = "main"
    text_content: str = Field(..., description="Snapshot text content at this commit")


class CommitResponse(BaseModel):
    id: str
    commit_hash: str
    story_id: str
    chapter_id: Optional[str] = None
    author: str
    message: str
    branch: str
    diff_summary: Optional[str] = None
    parent_commit_hash: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CommitDetailResponse(CommitResponse):
    snapshot_text: str


class DiffResponse(BaseModel):
    from_commit: str
    to_commit: str
    diff: str
    additions: int
    deletions: int


class RollbackRequest(BaseModel):
    commit_hash: str
    branch: Optional[str] = "main"


class RollbackResponse(BaseModel):
    message: str
    current_commit_hash: str
    chapter_id: Optional[str] = None
    reverted_to: str

