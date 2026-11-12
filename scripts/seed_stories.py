"""Seeds demo stories, characters, and indexed chapters for testing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import SessionLocal, init_db
from app.database.models import Story, CanonEntity, CanonRelationship, CanonFact
from app.ingestion.embedder import Embedder
from app.pipelines.indexing_pipeline import IndexingPipeline
from app.core.logging import logger

SAMPLE_STORY_ID = "story-obsidian-crown"

CHAPTER_1_TEXT = """
The rain lashed against the obsidian ramparts of Aethelgard. Kaelen tightened her grip on the silver pommel of her dagger, her breath misting in the freezing mountain air.

"The northern pass has fallen," whispered Lord Matthew, stepping through the low archway of the watchtower. His mantle was soaked, stained with soot and trail dust.

***

In the war room below, three maps lay unrolled across the oak table. Matthew pointed a trembling finger at the Frostpeak fortress. "The vanguard struck at dusk. We held the gates for two hours, but their siege beasts breached the iron portcullis."

Kaelen listened in grim silence. "Then we march before dawn. Matthew, take the scouts and secure the valley bridge. We cannot allow them to cross the Silver River."
"""

CHAPTER_2_TEXT = """
Dawn broke cold and gray over the Silver River. Kaelen surveyed the vanguard ranks from atop her mare. The frost crunched under heavy iron hooves.

***

A sudden horn echoed through the misty pines. Enemy archers appeared along the high ridge, their arrows black tipped with viper venom. Matthew charged forward with the eastern flank, his shield raised high.

A black shaft struck Matthew squarely through the breastplate. He fell into the rushing currents of the Silver River, lost beneath the icy foam.

***

By nightfall, the battle was won, but the cost was devastating. In the commander's tent, Kaelen placed Matthew's broken insignia upon the battle ledger. Lord Matthew was dead, buried in the river's depths.
"""


def seed_database():
    init_db()
    db = SessionLocal()
    pipeline = IndexingPipeline(embedder=Embedder(local_fallback=True))

    try:
        logger.info("Creating demo story: 'The Obsidian Crown'...")
        story = db.query(Story).filter(Story.id == SAMPLE_STORY_ID).first()
        if not story:
            story = Story(
                id=SAMPLE_STORY_ID,
                title="The Obsidian Crown",
                description="An epic fantasy saga of war, betrayed oaths, and ancient artifacts.",
            )
            db.add(story)
            db.commit()

        # Seed Entities
        logger.info("Registering Canon Entities...")
        kaelen = CanonEntity(
            story_id=SAMPLE_STORY_ID,
            name="Kaelen",
            entity_type="character",
            aliases=["Commander Kaelen", "Lady of Aethelgard"],
            attributes={"status": "ALIVE", "role": "Commander"},
            first_seen_chapter=1,
        )
        matthew = CanonEntity(
            story_id=SAMPLE_STORY_ID,
            name="Matthew",
            entity_type="character",
            aliases=["Lord Matthew"],
            attributes={"status": "DECEASED", "death_chapter": 2},
            first_seen_chapter=1,
        )
        db.add_all([kaelen, matthew])
        db.commit()
        db.refresh(kaelen)
        db.refresh(matthew)

        # Seed Relationships
        logger.info("Seeding Canon Relationships...")
        rel = CanonRelationship(
            story_id=SAMPLE_STORY_ID,
            source_entity_id=matthew.id,
            target_entity_id=kaelen.id,
            relation_type="ALLIED_WITH",
            valid_from_chapter=1,
            valid_to_chapter=2,
        )
        db.add(rel)
        db.commit()

        # Index Chapter 1 and Chapter 2
        logger.info("Indexing Chapter 1 via Pipeline A...")
        pipeline.run(
            db=db,
            story_id=SAMPLE_STORY_ID,
            chapter_title="The Falling Watch",
            chapter_index=1,
            raw_text=CHAPTER_1_TEXT,
        )

        logger.info("Indexing Chapter 2 via Pipeline A...")
        pipeline.run(
            db=db,
            story_id=SAMPLE_STORY_ID,
            chapter_title="The Silver River Crossing",
            chapter_index=2,
            raw_text=CHAPTER_2_TEXT,
        )

        # Approve critical facts & insert core canon statements
        core_facts = [
            CanonFact(
                story_id=SAMPLE_STORY_ID,
                entity_id=kaelen.id,
                statement="Commander Kaelen held the obsidian ramparts of Aethelgard",
                category="state",
                timeline_order=1,
                status="APPROVED",
                confidence=1.0,
            ),
            CanonFact(
                story_id=SAMPLE_STORY_ID,
                entity_id=matthew.id,
                statement="Lord Matthew died in the battle of the Silver River",
                category="state_change",
                timeline_order=2,
                status="APPROVED",
                confidence=1.0,
            ),
        ]
        db.add_all(core_facts)

        facts = db.query(CanonFact).filter(CanonFact.story_id == SAMPLE_STORY_ID).all()
        for f in facts:
            f.status = "APPROVED"
        db.commit()

        logger.info("Seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

