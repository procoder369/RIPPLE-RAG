"""Temporal validity and chronological timeline logic."""

from typing import Optional


class TemporalInterval:
    """Represents a chapter range where a state or relation is valid."""

    def __init__(self, start_chapter: int = 1, end_chapter: Optional[int] = None):
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter

    def is_valid_at(self, chapter: int) -> bool:
        """Determines if the interval covers the specified chapter."""
        if chapter < self.start_chapter:
            return False
        if self.end_chapter is not None and chapter > self.end_chapter:
            return False
        return True

    def overlaps(self, other: "TemporalInterval") -> bool:
        """Checks if two temporal intervals overlap."""
        self_end = self.end_chapter if self.end_chapter is not None else float("inf")
        other_end = other.end_chapter if other.end_chapter is not None else float("inf")
        return max(self.start_chapter, other.start_chapter) <= min(self_end, other_end)

