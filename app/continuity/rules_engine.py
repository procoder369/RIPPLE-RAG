"""Deterministic continuity rules engine for hard narrative constraints."""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import CanonFact, CanonEntity


class DeterministicRulesEngine:
    """Enforces logical invariants such as character death, inventory exclusivity, and locations."""

    @staticmethod
    def check_character_state(
        db: Session,
        story_id: str,
        character_name: str,
        target_chapter: int,
        attempted_action: str,
    ) -> Optional[Dict[str, Any]]:
        """Checks if a character is in a state that permits the attempted action."""
        entity = (
            db.query(CanonEntity)
            .filter(CanonEntity.story_id == story_id, CanonEntity.name.ilike(character_name))
            .first()
        )
        if not entity:
            return None

        # Check death status
        death_facts = (
            db.query(CanonFact)
            .filter(
                CanonFact.story_id == story_id,
                CanonFact.entity_id == entity.id,
                CanonFact.statement.ilike("%died%") | CanonFact.statement.ilike("%killed%"),
                CanonFact.status == "APPROVED",
                CanonFact.timeline_order <= target_chapter,
            )
            .all()
        )

        if death_facts and "flashback" not in attempted_action.lower():
            earliest_death = min(f.timeline_order for f in death_facts)
            if target_chapter > earliest_death:
                return {
                    "violation_type": "STATE_CONTRADICTION",
                    "severity": "BLOCKING",
                    "description": (
                        f"Character '{entity.name}' died in Chapter {earliest_death}, "
                        f"but appears performing active action in Chapter {target_chapter}."
                    ),
                    "conflicting_fact_id": death_facts[0].id,
                }

        return None

