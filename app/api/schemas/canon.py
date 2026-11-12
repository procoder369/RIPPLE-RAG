"""Pydantic schemas for CanonGraph entities, facts, and approval workflows."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FactApprovalRequest(BaseModel):
    fact_id: str
    status: str = Field(..., pattern="^(APPROVED|REJECTED|SUPERSEDED)$")


class CreateEntityRequest(BaseModel):
    story_id: str
    name: str
    entity_type: str = Field(default="character")
    aliases: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    first_seen_chapter: Optional[int] = 1


class CreateRelationshipRequest(BaseModel):
    story_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    valid_from_chapter: int = 1
    valid_to_chapter: Optional[int] = None


class WhatIfAnalysisRequest(BaseModel):
    story_id: str
    hypothesis_description: str
    target_entity_name: str
    changed_at_chapter: int = Field(ge=1)

