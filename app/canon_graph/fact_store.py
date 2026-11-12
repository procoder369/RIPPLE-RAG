"""Fact store management for story canon."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import CanonFact, CanonEntity


class FactStore:
    """Provides persistence operations for canon facts."""

    @staticmethod
    def propose_fact(
        db: Session,
        story_id: str,
        statement: str,
        entity_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        timeline_order: int = 0,
        source_quote: Optional[str] = None,
        category: str = "general",
    ) -> CanonFact:
        """Stores a freshly extracted story fact awaiting author approval."""
        fact = CanonFact(
            story_id=story_id,
            entity_id=entity_id,
            chapter_id=chapter_id,
            statement=statement,
            category=category,
            timeline_order=timeline_order,
            status="PROPOSED",
            source_quote=source_quote,
        )
        db.add(fact)
        db.commit()
        db.refresh(fact)
        return fact

    @staticmethod
    def update_fact_status(
        db: Session,
        fact_id: str,
        status: str,
    ) -> Optional[CanonFact]:
        """Approves, rejects, or marks a fact as superseded."""
        fact = db.query(CanonFact).filter(CanonFact.id == fact_id).first()
        if fact:
            fact.status = status
            db.commit()
            db.refresh(fact)
        return fact

    @staticmethod
    def get_canon_facts(
        db: Session,
        story_id: str,
        only_approved: bool = True,
        entity_id: Optional[str] = None,
    ) -> List[CanonFact]:
        """Retrieves facts matching the criteria."""
        query = db.query(CanonFact).filter(CanonFact.story_id == story_id)
        if only_approved:
            query = query.filter(CanonFact.status == "APPROVED")
        if entity_id:
            query = query.filter(CanonFact.entity_id == entity_id)
        return query.order_by(CanonFact.timeline_order.asc()).all()

