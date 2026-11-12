"""Ripple Analyzer for counterfactual what-if analysis and dependency impact."""

from typing import Dict, Any, List, Optional
import networkx as nx
from sqlalchemy.orm import Session
from app.database.models import CanonFact, CanonEntity, Chapter
from app.canon_graph.graph_service import CanonGraphService
from app.core.config import get_settings

settings = get_settings()


class RippleAnalyzer:
    """Calculates downstream narrative consequences of altering a story event or canon fact."""

    @classmethod
    def analyze_what_if(
        cls,
        db: Session,
        story_id: str,
        hypothesis_description: str,
        target_entity_name: str,
        changed_at_chapter: int,
    ) -> Dict[str, Any]:
        """
        Traverses dependency pathways to determine what chapters, facts,
        and character arcs are affected by a narrative divergence.
        """
        graph = CanonGraphService.build_graph_for_story(db, story_id)

        # 1. Locate entity node
        target_node = None
        for node_id, data in graph.nodes(data=True):
            if data.get("name", "").lower() == target_entity_name.lower():
                target_node = node_id
                break

        impacted_entities: List[str] = [target_entity_name]
        if target_node and target_node in graph:
            # Multi-hop connected entities
            subgraph_nodes = nx.single_source_shortest_path_length(
                graph, target_node, cutoff=settings.MAX_GRAPH_DEPTH
            ).keys()
            for n in subgraph_nodes:
                ent_name = graph.nodes[n].get("name")
                if ent_name and ent_name not in impacted_entities:
                    impacted_entities.append(ent_name)

        # 2. Find downstream chapters
        downstream_chapters = (
            db.query(Chapter)
            .filter(Chapter.story_id == story_id, Chapter.chapter_index >= changed_at_chapter)
            .order_by(Chapter.chapter_index.asc())
            .all()
        )

        # 3. Find downstream canon facts that depend on impacted entities
        downstream_facts = (
            db.query(CanonFact)
            .filter(
                CanonFact.story_id == story_id,
                CanonFact.timeline_order >= changed_at_chapter,
                CanonFact.status == "APPROVED",
            )
            .all()
        )

        impacted_facts_list: List[Dict[str, Any]] = []
        for fact in downstream_facts:
            # Check if fact statement mentions any of the impacted entities
            if any(ent.lower() in fact.statement.lower() for ent in impacted_entities):
                impacted_facts_list.append({
                    "fact_id": fact.id,
                    "statement": fact.statement,
                    "timeline_chapter": fact.timeline_order,
                    "category": fact.category,
                })

        # Calculate ripple severity
        total_downstream_facts = len(downstream_facts)
        impact_score = min(
            1.0,
            (len(impacted_facts_list) / max(total_downstream_facts, 1)) * 0.5
            + (len(impacted_entities) * 0.1),
        )

        return {
            "hypothesis": hypothesis_description,
            "origin_chapter": changed_at_chapter,
            "impact_score": round(impact_score, 2),
            "impact_level": "HIGH" if impact_score >= settings.RIPPLE_IMPACT_THRESHOLD else "MODERATE",
            "impacted_entities": impacted_entities,
            "affected_chapters": [ch.chapter_index for ch in downstream_chapters],
            "invalidated_or_rippled_facts": impacted_facts_list,
            "recommendation": (
                f"Altering events in Chapter {changed_at_chapter} ripples across {len(impacted_facts_list)} "
                f"facts and impacts {len(impacted_entities)} characters/entities. "
                "Downstream scenes should be audited for continuity."
            ),
        }

