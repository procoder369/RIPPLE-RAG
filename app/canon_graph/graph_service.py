"""Graph service for building and querying the narrative CanonGraph."""

from typing import List, Dict, Any, Optional
import networkx as nx
from sqlalchemy.orm import Session
from app.database.models import CanonEntity, CanonRelationship, CanonFact


class CanonGraphService:
    """Manages in-memory graph representation and topological lookups for a story."""

    @classmethod
    def build_graph_for_story(cls, db: Session, story_id: str) -> nx.DiGraph:
        """Constructs a NetworkX directed multigraph from database entities and relationships."""
        graph = nx.DiGraph()

        # Add entities as nodes
        entities = db.query(CanonEntity).filter(CanonEntity.story_id == story_id).all()
        for ent in entities:
            graph.add_node(
                ent.id,
                name=ent.name,
                entity_type=ent.entity_type,
                attributes=ent.attributes or {},
                aliases=ent.aliases or [],
            )

        # Add relationships as edges
        relationships = (
            db.query(CanonRelationship)
            .filter(CanonRelationship.story_id == story_id)
            .all()
        )
        for rel in relationships:
            graph.add_edge(
                rel.source_entity_id,
                rel.target_entity_id,
                relation_type=rel.relation_type,
                valid_from=rel.valid_from_chapter,
                valid_to=rel.valid_to_chapter,
            )

        return graph

    @classmethod
    def get_entity_neighborhood(
        cls,
        graph: nx.DiGraph,
        entity_name_or_id: str,
        depth: int = 2,
    ) -> List[Dict[str, Any]]:
        """Retrieves k-hop neighbors and relationships around an entity."""
        target_id = None
        # Check by id or name
        for node_id, data in graph.nodes(data=True):
            if node_id == entity_name_or_id or data.get("name", "").lower() == entity_name_or_id.lower():
                target_id = node_id
                break

        if not target_id or target_id not in graph:
            return []

        subgraph_nodes = nx.single_source_shortest_path_length(graph, target_id, cutoff=depth).keys()
        subgraph = graph.subgraph(subgraph_nodes)

        results: List[Dict[str, Any]] = []
        for u, v, data in subgraph.edges(data=True):
            u_name = graph.nodes[u].get("name", u)
            v_name = graph.nodes[v].get("name", v)
            results.append({
                "source": u_name,
                "target": v_name,
                "relation": data.get("relation_type", "RELATED_TO"),
                "valid_from": data.get("valid_from", 1),
                "valid_to": data.get("valid_to"),
            })
        return results

