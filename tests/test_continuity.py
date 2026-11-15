"""Unit tests for deterministic continuity rules and contradiction detector."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Story, CanonEntity, CanonFact
from app.continuity.rules_engine import DeterministicRulesEngine


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_character_death_rule(test_db):
    story = Story(id="test-story", title="Test Story")
    test_db.add(story)
    test_db.commit()

    matthew = CanonEntity(
        story_id="test-story",
        name="Matthew",
        entity_type="character",
    )
    test_db.add(matthew)
    test_db.commit()

    # Matthew died in Chapter 2
    death_fact = CanonFact(
        story_id="test-story",
        entity_id=matthew.id,
        statement="Lord Matthew died in the battle of the river",
        timeline_order=2,
        status="APPROVED",
    )
    test_db.add(death_fact)
    test_db.commit()

    # Check action in Chapter 4 (should trigger blocking contradiction)
    violation = DeterministicRulesEngine.check_character_state(
        db=test_db,
        story_id="test-story",
        character_name="Matthew",
        target_chapter=4,
        attempted_action="Matthew rides his horse to the capital",
    )
    assert violation is not None
    assert violation["severity"] == "BLOCKING"
    assert "died in Chapter 2" in violation["description"]

    # Flashback should be permitted
    flashback_result = DeterministicRulesEngine.check_character_state(
        db=test_db,
        story_id="test-story",
        character_name="Matthew",
        target_chapter=4,
        attempted_action="In a flashback, Matthew smiles warmly",
    )
    assert flashback_result is None


def test_physical_impairment_rule(test_db):
    story = Story(id="test-story-2", title="Combat Story")
    test_db.add(story)
    test_db.commit()

    knight = CanonEntity(
        story_id="test-story-2",
        name="Sir Justin",
        entity_type="character",
    )
    test_db.add(knight)
    test_db.commit()

    # Justin lost his right arm in Chapter 1
    injury_fact = CanonFact(
        story_id="test-story-2",
        entity_id=knight.id,
        statement="Sir Justin had his right arm severed in battle",
        timeline_order=1,
        status="APPROVED",
    )
    test_db.add(injury_fact)
    test_db.commit()

    # Attempt action requiring both hands in Chapter 3
    violation = DeterministicRulesEngine.check_character_state(
        db=test_db,
        story_id="test-story-2",
        character_name="Sir Justin",
        target_chapter=3,
        attempted_action="Sir Justin swung the heavy greatsword with both hands",
    )
    assert violation is not None
    assert violation["violation_type"] == "PHYSICAL_IMPAIRMENT_CONTRADICTION"
    assert "impairment" in violation["description"].lower()

