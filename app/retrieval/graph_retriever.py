"""Retrieves grounded canon facts and entity relationships from CanonGraph."""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.canon_graph.graph_service import CanonGraphService
from app.canon_graph.fact_store import FactStore
from app.database.models import CanonEntity


class GraphRetriever:
    """Queries CanonGraph for facts and relational neighborhoods."""

    @staticmethod
    def retrieve_entity_context(
        db: Session,
        story_id: str,
        entity_names: List[str],
        depth: int = 2,
    ) -> Dict[str, Any]:
        """Extracts facts and relationships for a list of entity names."""
        graph = CanonGraphService.build_graph_for_story(db, story_id)
        relationships: List[Dict[str, Any]] = []
        facts_list: List[Dict[str, Any]] = []

        for name in entity_names:
            # 1. Fetch multi-hop relational neighborhood
            neighborhood = CanonGraphService.get_entity_neighborhood(graph, name, depth=depth)
            relationships.extend(neighborhood)

            # 2. Fetch approved facts for this entity
            entity = (
                db.query(CanonEntity)
                .filter(CanonEntity.story_id == story_id, CanonEntity.name.ilike(f"%{name}%"))
                .first()
            )
            if entity:
                facts = FactStore.get_canon_facts(db, story_id, only_approved=True, entity_id=entity.id)
                for f in facts:
                    facts_list.append({
                        "id": f.id,
                        "statement": f.statement,
                        "timeline_order": f.timeline_order,
                        "category": f.category,
                    })

        return {
            "entities": entity_names,
            "relationships": relationships,
            "canon_facts": facts_list,
        }

