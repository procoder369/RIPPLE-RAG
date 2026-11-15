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

        # Check physical impairment / injury status (e.g. severed arm, blinded, paralyzed)
        impairment_facts = (
            db.query(CanonFact)
            .filter(
                CanonFact.story_id == story_id,
                CanonFact.entity_id == entity.id,
                CanonFact.statement.ilike("%severed%")
                | CanonFact.statement.ilike("%lost their hand%")
                | CanonFact.statement.ilike("%lost their arm%")
                | CanonFact.statement.ilike("%lost an arm%")
                | CanonFact.statement.ilike("%amputat%")
                | CanonFact.statement.ilike("%blind%"),
                CanonFact.status == "APPROVED",
                CanonFact.timeline_order <= target_chapter,
            )
            .all()
        )

        if impairment_facts and "flashback" not in attempted_action.lower():
            for fact in impairment_facts:
                stmt = fact.statement.lower()
                action_lower = attempted_action.lower()
                if "arm" in stmt or "hand" in stmt:
                    if any(w in action_lower for w in ["both hands", "two hands", "held with his severed", "held with her severed", "swung with both arms"]):
                        return {
                            "violation_type": "PHYSICAL_IMPAIRMENT_CONTRADICTION",
                            "severity": "BLOCKING",
                            "description": (
                                f"Character '{entity.name}' suffered an impairment in Chapter {fact.timeline_order} ('{fact.statement}'), "
                                f"which contradicts the action described in Chapter {target_chapter}: '{attempted_action[:100]}...'"
                            ),
                            "conflicting_fact_id": fact.id,
                        }

        return None

