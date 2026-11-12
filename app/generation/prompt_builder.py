"""Prompt template loader and builder."""

from pathlib import Path


class PromptBuilder:
    """Loads prompt templates from disk and constructs structured prompts."""

    PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"

    @classmethod
    def load_template(cls, template_name: str) -> str:
        """Reads a prompt template file."""
        template_path = cls.PROMPTS_DIR / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Prompt template {template_name} not found at {template_path}")
        return template_path.read_text(encoding="utf-8")

    @classmethod
    def build_qa_prompt(cls, context: str, query: str) -> str:
        """Constructs story Q&A prompt."""
        template = cls.load_template("story_qa.txt")
        return template.format(context=context, query=query)

    @classmethod
    def build_continuity_prompt(cls, context: str, manuscript_text: str) -> str:
        """Constructs continuity checking prompt."""
        template = cls.load_template("continuity_check.txt")
        return template.format(context=context, manuscript_text=manuscript_text)

    @classmethod
    def build_extraction_prompt(cls, chunk_text: str, chapter_index: int) -> str:
        """Constructs fact extraction prompt."""
        template = cls.load_template("fact_extraction.txt")
        return template.format(chunk_text=chunk_text, chapter_index=chapter_index)

