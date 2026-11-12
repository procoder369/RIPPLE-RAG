"""Response generator orchestrating context and LLM."""

from typing import Dict, Any, List, Tuple
from app.database.models import StoryChunk
from app.generation.context_builder import ContextBuilder
from app.generation.prompt_builder import PromptBuilder
from app.generation.llm_client import LLMClient


class Generator:
    """Generates answers with grounded narrative context."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()

    def generate_answer(
        self,
        query: str,
        retrieved_chunks: List[Tuple[StoryChunk, float]],
        graph_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Builds grounded context and queries LLM for an answer."""
        context_str = ContextBuilder.build_context(retrieved_chunks, graph_context)
        prompt = PromptBuilder.build_qa_prompt(context=context_str, query=query)
        raw_answer = self.llm_client.generate(prompt)

        citations: List[Dict[str, Any]] = []
        for idx, (chunk, score) in enumerate(retrieved_chunks, start=1):
            citations.append({
                "source_index": idx,
                "chunk_id": chunk.id,
                "chapter_id": chunk.chapter_id,
                "scene_number": chunk.scene_number,
                "score": round(score, 4),
                "preview": chunk.content[:140] + "..." if len(chunk.content) > 140 else chunk.content,
            })

        return {
            "answer": raw_answer,
            "citations": citations,
            "context_used": context_str,
        }

