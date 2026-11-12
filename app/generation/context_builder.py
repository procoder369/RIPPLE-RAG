"""Builds grounded context payloads for LLM generation."""

from typing import List, Dict, Any, Tuple
from app.database.models import StoryChunk


class ContextBuilder:
    """Assembles manuscript passages and canon graph facts into a structured prompt context."""

    @staticmethod
    def build_context(
        chunks: List[Tuple[StoryChunk, float]],
        graph_context: Dict[str, Any] = None,
    ) -> str:
        """Formats evidence passages and approved facts into grounded narrative context."""
        context_parts: List[str] = []

        # 1. Canon Facts Section
        if graph_context and graph_context.get("canon_facts"):
            context_parts.append("=== VERIFIED CANON FACTS ===")
            for fact in graph_context["canon_facts"]:
                context_parts.append(f"- Fact: {fact['statement']} (Timeline: Ch {fact.get('timeline_order', 1)})")
            context_parts.append("")

        # 2. Entity Relationships
        if graph_context and graph_context.get("relationships"):
            context_parts.append("=== CANON RELATIONSHIPS ===")
            for rel in graph_context["relationships"]:
                context_parts.append(
                    f"- {rel['source']} --[{rel['relation']}]--> {rel['target']} (Active: Ch {rel['valid_from']}+)"
                )
            context_parts.append("")

        # 3. Manuscript Excerpts with citations
        context_parts.append("=== MANUSCRIPT EXCERPTS ===")
        for idx, (chunk, score) in enumerate(chunks, start=1):
            scene_info = f"Scene {chunk.scene_number}" if chunk.scene_number else "Scene Unknown"
            context_parts.append(
                f"[Source #{idx} | Chapter ID: {chunk.chapter_id} | {scene_info} | Chunk {chunk.chunk_index}]:\n{chunk.content}\n"
            )

        return "\n".join(context_parts)

