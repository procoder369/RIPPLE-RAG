"""Chapter document loader."""

from typing import Dict, Any


class DocumentLoader:
    """Loads raw manuscript text and chapter metadata."""

    @staticmethod
    def load_from_text(raw_text: str, chapter_title: str, chapter_index: int) -> Dict[str, Any]:
        """Loads and returns standardized chapter payload."""
        return {
            "title": chapter_title.strip(),
            "chapter_index": chapter_index,
            "raw_text": raw_text.strip(),
            "word_count": len(raw_text.split()),
        }

