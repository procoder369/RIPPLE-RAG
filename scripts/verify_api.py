"""End-to-end verification script for RippleRAG components."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import SessionLocal, init_db
from app.pipelines.rag_pipeline import RAGPipeline
from app.continuity.contradiction import ContradictionDetector
from app.continuity.ripple_analyzer import RippleAnalyzer
from app.canon_graph.fact_store import FactStore


def run_checks():
    print("=" * 65)
    print("           RIPPLE RAG APPLICATION VERIFICATION          ")
    print("=" * 65)

    # 1. Database Check
    print("\n[1/5] Verifying Database Connection...")
    init_db()
    db = SessionLocal()
    print("       Database connection: OK")

    story_id = "story-obsidian-crown"

    # 2. Pipeline B (Story Lore Q&A)
    print("\n[2/5] Testing Pipeline B (Hybrid Retrieval + RAG Q&A)...")
    rag = RAGPipeline()
    query = "Where did Lord Matthew fall in battle?"
    result = rag.run(db=db, story_id=story_id, query=query, top_k=3)
    print(f"       Query: '{query}'")
    print(f"       Answer: {result['answer']}")
    print(f"       Verified: {result['verified']}")
    print(f"       Citations Found: {len(result['citations'])}")
    for c in result["citations"]:
        print(f"         * [Source #{c['source_index']}] Scene {c['scene_number']}: {c['preview'][:80]}...")

    # 3. Continuity Contradiction Check
    print("\n[3/5] Testing Continuity Engine (Deterministic & Semantic)...")
    detector = ContradictionDetector()
    cont_result = detector.analyze_manuscript(
        db=db,
        story_id=story_id,
        chapter_index=4,
        text="Lord Matthew mounted his warhorse and charged the enemy fortress.",
        mentioned_characters=["Matthew"],
    )
    print(f"       Has Contradictions: {cont_result['has_contradictions']}")
    print(f"       Violations Found: {cont_result['total_violations']}")
    for v in cont_result["violations"]:
        print(f"         * [{v.get('severity')}] {v.get('description')}")

    # 4. Canon Facts Inspection
    print("\n[4/5] Testing Canon Graph Fact Store...")
    facts = FactStore.get_canon_facts(db, story_id, only_approved=True)
    print(f"       Approved Facts Count: {len(facts)}")
    for f in facts[:3]:
        print(f"         * Ch {f.timeline_order}: {f.statement}")

    # 5. Ripple What-If Analyzer
    print("\n[5/5] Testing What-If & Ripple Impact Analyzer...")
    hypothesis = "What if Lord Matthew survived the river crossing?"
    ripple_result = RippleAnalyzer.analyze_what_if(
        db=db,
        story_id=story_id,
        hypothesis_description=hypothesis,
        target_entity_name="Matthew",
        changed_at_chapter=2,
    )
    print(f"       Hypothesis: '{hypothesis}'")
    print(f"       Impact Level: {ripple_result['impact_level']} (Score: {ripple_result['impact_score']})")
    print(f"       Affected Chapters: {ripple_result['affected_chapters']}")
    print(f"       Rippled Facts Count: {len(ripple_result['invalidated_or_rippled_facts'])}")
    print(f"       Recommendation: {ripple_result['recommendation']}")

    db.close()
    print("\n" + "=" * 65)
    print("             ALL CHECKS COMPLETED SUCCESSFULLY!          ")
    print("=" * 65)


if __name__ == "__main__":
    run_checks()
