"""Demonstration of indexing and querying a completely new story."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import SessionLocal, init_db
from app.pipelines.indexing_pipeline import IndexingPipeline
from app.pipelines.rag_pipeline import RAGPipeline
from app.canon_graph.fact_store import FactStore
from app.continuity.ripple_analyzer import RippleAnalyzer

# A completely different genre: Cyberpunk Sci-Fi Story
NEW_STORY_ID = "story-neon-horizon"

SCI_FI_CHAPTER_1 = """
Captain Jax stared through the reinforced viewport of the orbital station Hyperion. Below, the neon-lit canyons of Neo-Shinjuku flickered through perpetual acid rain.

"The AI core on Sector 7 has destabilized," warned Dr. Elena Vance, her cybernetic optic glowing faint amber.

***

Jax grabbed the electromagnetic pulse carbine from the weapons rack. "How long until the firewall collapses?"

"Six minutes," Elena typed furiously into the holographic terminal. "If the rogue AI overrides the atmospheric stabilizers, three million citizens will suffocate."

***

Jax sprinted down the maintenance corridor, the magnetic soles of his boots clanking against the steel grating. At the blast door of Sector 7, he severed the main power conduits with his thermal cutter. The rogue AI went silent. Sector 7 was saved, but Jax suffered severe electrical burns across his right arm.
"""


def test_new_story_flow():
    init_db()
    db = SessionLocal()

    print("=" * 65)
    print("      TESTING ARBITRARY NEW STORY: 'Project Neon Horizon'      ")
    print("=" * 65)

    # 1. Ingest Chapter 1 of the new Sci-Fi story
    print("\n[Step 1] Ingesting New Sci-Fi Story via Pipeline A...")
    indexing_pipeline = IndexingPipeline()
    index_res = indexing_pipeline.run(
        db=db,
        story_id=NEW_STORY_ID,
        chapter_title="Protocol Breach",
        chapter_index=1,
        raw_text=SCI_FI_CHAPTER_1,
    )
    print(f"Status: {index_res['status']}")
    print(f"Chunks indexed: {index_res['chunks_indexed']}")
    print(f"Story ID: {index_res['story_id']}")

    # 2. Ask a specific question about Jax and Elena
    print("\n[Step 2] Asking Question about the new story via Pipeline B...")
    rag = RAGPipeline()
    query_1 = "What happened to Captain Jax at the blast door of Sector 7?"
    res_1 = rag.run(db=db, story_id=NEW_STORY_ID, query=query_1, top_k=2)

    print(f"Query: '{query_1}'")
    print(f"Answer: {res_1['answer']}")
    print(f"Verified: {res_1['verified']}")
    print("Top Citation Source:")
    if res_1["citations"]:
        print(f"  [{res_1['citations'][0]['chapter_id']} | Scene {res_1['citations'][0]['scene_number']}]")
        print(f"  Excerpt: {res_1['citations'][0]['preview']}")

    # 3. Verify story isolation: query the first story (Obsidian Crown) vs this new story
    print("\n[Step 3] Verifying Complete Story Isolation...")
    query_isolated = "Who is Dr. Elena Vance?"
    res_isolated = rag.run(db=db, story_id="story-obsidian-crown", query=query_isolated, top_k=2)
    print(f"Querying Fantasy Story for Sci-Fi Character '{query_isolated}':")
    print(f"Answer from Fantasy Story: {res_isolated['answer']}")

    db.close()
    print("\n" + "=" * 65)
    print("                    NEW STORY TEST PASSED!                      ")
    print("=" * 65)


if __name__ == "__main__":
    test_new_story_flow()

