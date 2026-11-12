"""End-to-end integration tests for Indexing and RAG pipelines."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base
from app.ingestion.embedder import Embedder
from app.retrieval.dense_retriever import DenseRetriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.pipelines.indexing_pipeline import IndexingPipeline
from app.pipelines.rag_pipeline import RAGPipeline


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_pipeline_a_and_b_integration(test_db):
    story_id = "test-integration-story"
    test_embedder = Embedder(local_fallback=True)

    # Run Pipeline A (Ingestion)
    idx_pipeline = IndexingPipeline(embedder=test_embedder)
    manuscript = (
        'The battle raged at the northern gate. Commander Kaelen rallied the guards.\n\n'
        '***\n\n'
        'Lord Matthew was struck down by an arrow near the bridge.'
    )
    res_a = idx_pipeline.run(
        db=test_db,
        story_id=story_id,
        chapter_title="Battle of the Gate",
        chapter_index=1,
        raw_text=manuscript,
    )
    assert res_a["status"] == "SUCCESS"
    assert res_a["chunks_indexed"] >= 2

    # Run Pipeline B (RAG Q&A)
    dense_retriever = DenseRetriever(embedder=test_embedder)
    hybrid_retriever = HybridRetriever(dense_retriever=dense_retriever)
    rag = RAGPipeline(hybrid_retriever=hybrid_retriever)

    res_b = rag.run(
        db=test_db,
        story_id=story_id,
        query="What happened to Lord Matthew at the bridge?",
        top_k=2,
    )
    assert "answer" in res_b
    assert len(res_b["citations"]) > 0
    assert res_b["citations"][0]["scene_number"] in [1, 2]
