"""API route for Canon fact review, entity registration, and graph management."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import CanonEntity, CanonFact, CanonRelationship
from app.canon_graph.fact_store import FactStore
from app.api.schemas.canon import (
    FactApprovalRequest,
    CreateEntityRequest,
    CreateRelationshipRequest,
)
from app.core.security import verify_service_token

router = APIRouter(prefix="/canon", tags=["Canon Graph"])


@router.get("/facts")
def get_story_facts(
    story_id: str = Query(...),
    only_approved: bool = Query(True),
    entity_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(verify_service_token),
):
    """Retrieves facts for a story."""
    facts = FactStore.get_canon_facts(
        db, story_id, only_approved=only_approved, entity_id=entity_id
    )
    return [
        {
            "id": f.id,
            "statement": f.statement,
            "category": f.category,
            "timeline_order": f.timeline_order,
            "status": f.status,
            "entity_id": f.entity_id,
            "source_quote": f.source_quote,
        }
        for f in facts
    ]


@router.post("/facts/review")
def review_fact(
    payload: FactApprovalRequest,
    db: Session = Depends(get_db),
    _=Depends(verify_service_token),
):
    """Approves, rejects, or marks a story fact as superseded."""
    updated = FactStore.update_fact_status(db, payload.fact_id, payload.status)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fact ID '{payload.fact_id}' not found",
        )
    return {
        "status": "SUCCESS",
        "fact_id": updated.id,
        "new_status": updated.status,
    }


@router.post("/entities", status_code=status.HTTP_201_CREATED)
def create_entity(
    payload: CreateEntityRequest,
    db: Session = Depends(get_db),
    _=Depends(verify_service_token),
):
    """Registers a new canon character, location, or faction."""
    entity = CanonEntity(
        story_id=payload.story_id,
        name=payload.name,
        entity_type=payload.entity_type,
        aliases=payload.aliases,
        attributes=payload.attributes,
        first_seen_chapter=payload.first_seen_chapter,
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return {
        "id": entity.id,
        "name": entity.name,
        "entity_type": entity.entity_type,
    }


@router.post("/relationships", status_code=status.HTTP_201_CREATED)
def create_relationship(
    payload: CreateRelationshipRequest,
    db: Session = Depends(get_db),
    _=Depends(verify_service_token),
):
    """Establishes a directed relationship between two entities."""
    rel = CanonRelationship(
        story_id=payload.story_id,
        source_entity_id=payload.source_entity_id,
        target_entity_id=payload.target_entity_id,
        relation_type=payload.relation_type,
        valid_from_chapter=payload.valid_from_chapter,
        valid_to_chapter=payload.valid_to_chapter,
    )
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return {
        "id": rel.id,
        "relation": rel.relation_type,
        "source": rel.source_entity_id,
        "target": rel.target_entity_id,
    }

