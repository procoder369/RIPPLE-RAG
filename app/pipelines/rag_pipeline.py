"""Pipeline B: Hybrid retrieval, reranking, grounded generation, and verification."""

from typing import Dict, Any
from sqlalchemy.orm import Session
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import Reranker
from app.generation.generator import Generator
from app.generation.verifier import OutputVerifier
from app.core.logging import logger


class RAGPipeline:
    """Orchestrates Pipeline B (Writer query to grounded verified answer)."""

    def __init__(
        self,
        hybrid_retriever: HybridRetriever = None,
        generator: Generator = None,
    ):
        self.retriever = hybrid_retriever or HybridRetriever()
        self.reranker = Reranker()
        self.generator = generator or Generator()
        self.verifier = OutputVerifier()

    def run(
        self,
        db: Session,
        story_id: str,
        query: str,
        top_k: int = 4,
    ) -> Dict[str, Any]:
        """Executes full RAG workflow for narrative queries."""
        logger.info(f"Running RAG Pipeline for story {story_id} with query: '{query}'")

        # 1. Hybrid Retrieval (Dense + Sparse + Canon Graph)
        retrieval_bundle = self.retriever.retrieve(db, story_id, query, top_k=top_k)
        candidate_chunks = retrieval_bundle["text_chunks"]
        graph_context = retrieval_bundle["graph_context"]

        # 2. Rerank Evidence Chunks
        reranked_chunks = self.reranker.rerank(query, candidate_chunks, top_n=top_k)

        # 3. Grounded Answer Generation
        gen_result = self.generator.generate_answer(
            query=query,
            retrieved_chunks=reranked_chunks,
            graph_context=graph_context,
        )

        # 4. Output Citation Verification
        verification = self.verifier.verify(
            answer=gen_result["answer"],
            citations=gen_result["citations"],
            context=gen_result["context_used"],
        )

        return {
            "query": query,
            "answer": gen_result["answer"],
            "verified": verification["verified"],
            "verification_details": verification,
            "citations": gen_result["citations"],
            "graph_evidence": graph_context,
        }

