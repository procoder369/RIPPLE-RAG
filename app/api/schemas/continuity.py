"""Pydantic schemas for continuity checking and contradiction analysis."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ContinuityCheckRequest(BaseModel):
    story_id: str = Field(..., description="Target story identifier")
    chapter_index: int = Field(..., ge=1, description="Current chapter position in timeline")
    manuscript_text: str = Field(..., min_length=10, description="New scene or chapter text to audit")
    mentioned_characters: Optional[List[str]] = Field(default_factory=list, description="Characters involved in scene")


class ContinuityViolationItem(BaseModel):
    violation_type: str
    severity: str
    description: str
    source_excerpt: Optional[str] = None
    conflicting_canon: Optional[str] = None
    suggested_fix: Optional[str] = None


class ContinuityCheckResponse(BaseModel):
    has_contradictions: bool
    total_violations: int
    violations: List[Dict[str, Any]]

