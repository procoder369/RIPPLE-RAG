"""Unit tests for CanonGraph operations and fact store."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Story, CanonEntity, CanonRelationship
from app.canon_graph.fact_store import FactStore
from app.canon_graph.graph_service import CanonGraphService


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_fact_store_approval_flow(test_db):
    story = Story(id="story-1", title="Saga")
    test_db.add(story)
    test_db.commit()

    fact = FactStore.propose_fact(
        db=test_db,
        story_id="story-1",
        statement="Kaelen wields the Obsidian Crown",
        timeline_order=1,
    )
    assert fact.status == "PROPOSED"

    # Only approved should be empty
    approved = FactStore.get_canon_facts(test_db, "story-1", only_approved=True)
    assert len(approved) == 0

    FactStore.update_fact_status(test_db, fact.id, "APPROVED")
    approved = FactStore.get_canon_facts(test_db, "story-1", only_approved=True)
    assert len(approved) == 1
    assert approved[0].statement == "Kaelen wields the Obsidian Crown"


def test_canon_graph_service(test_db):
    story = Story(id="story-g", title="Graph Story")
    test_db.add(story)
    test_db.commit()

    e1 = CanonEntity(id="e1", story_id="story-g", name="Kaelen", entity_type="character")
    e2 = CanonEntity(id="e2", story_id="story-g", name="Aethelgard", entity_type="location")
    test_db.add_all([e1, e2])
    test_db.commit()

    rel = CanonRelationship(
        story_id="story-g",
        source_entity_id="e1",
        target_entity_id="e2",
        relation_type="DEFENDS",
    )
    test_db.add(rel)
    test_db.commit()

    graph = CanonGraphService.build_graph_for_story(test_db, "story-g")
    assert graph.number_of_nodes() == 2
    assert graph.number_of_edges() == 1

    neighborhood = CanonGraphService.get_entity_neighborhood(graph, "Kaelen")
    assert len(neighborhood) == 1
    assert neighborhood[0]["source"] == "Kaelen"
    assert neighborhood[0]["target"] == "Aethelgard"
    assert neighborhood[0]["relation"] == "DEFENDS"

