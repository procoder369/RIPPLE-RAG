"""Text cleaning and normalization for fiction manuscripts."""

import re


class TextPreprocessor:
    """Normalizes chapter text, fixes typographic artifacts, and prepares text for chunking."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Cleans and standardizes raw manuscript text."""
        if not text:
            return ""
        # Standardize newline representations
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace typographic smart quotes and dashes with uniform unicode
        text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        text = text.replace("—", " - ").replace("–", " - ")
        # Collapse excessive blank lines (> 3) to standard double newline
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

