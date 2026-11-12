"""Unit tests for dense, sparse, and hybrid retrieval."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Story, Chapter, StoryChunk
from app.retrieval.sparse_retriever import SparseRetriever
from app.retrieval.reranker import Reranker


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_sparse_retrieval_and_reranker(test_db):
    story = Story(id="ret-story", title="Retrieval Story")
    test_db.add(story)
    test_db.commit()

    chunk1 = StoryChunk(
        id="c1",
        story_id="ret-story",
        chapter_id="ch1",
        chunk_index=0,
        content='Lady Kaelen shouted: "Hold the fortress gates at all costs!"',
    )
    chunk2 = StoryChunk(
        id="c2",
        story_id="ret-story",
        chapter_id="ch1",
        chunk_index=1,
        content="The autumn wind blew gently across the empty wheat fields.",
    )
    test_db.add_all([chunk1, chunk2])
    test_db.commit()

    results = SparseRetriever.retrieve(test_db, "ret-story", "Kaelen fortress", top_k=2)
    assert len(results) >= 1
    assert results[0][0].id == "c1"

    # Test reranker
    reranked = Reranker.rerank("Kaelen fortress", results, top_n=2)
    assert len(reranked) >= 1
    assert reranked[0][0].id == "c1"

