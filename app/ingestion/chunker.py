"""Scene-aware chunker designed for narrative prose and dialogue."""

import re
from typing import List, Dict, Any


class SceneAwareChunker:
    """
    Chunks story manuscripts along natural scene boundaries (e.g. ***, ---, ###)
    and paragraph groups without splitting sentences or active character dialogue.
    """

    SCENE_BREAK_REGEX = re.compile(
        r"(?:^\s*(?:\*\s*\*\s*\*|---|===|#{2,3}\s*Scene|\. \. \.)\s*$)",
        re.MULTILINE,
    )

    def __init__(self, target_chunk_words: int = 350, max_chunk_words: int = 600):
        self.target_chunk_words = target_chunk_words
        self.max_chunk_words = max_chunk_words

    def split_into_scenes(self, text: str) -> List[str]:
        """Splits manuscript into distinct scenes using typical formatting breaks."""
        scenes = self.SCENE_BREAK_REGEX.split(text)
        scenes = [s.strip() for s in scenes if s and s.strip()]
        if not scenes:
            scenes = [text.strip()]
        return scenes

    def _split_long_paragraph(self, para: str) -> List[str]:
        """Splits an oversized paragraph into sentence clusters within word limits."""
        sentences = re.split(r"(?<=[.!?])\s+", para)
        sub_paras: List[str] = []
        cur_sentences: List[str] = []
        cur_words = 0

        for sent in sentences:
            sent_words = len(sent.split())
            if cur_words + sent_words > self.max_chunk_words and cur_sentences:
                sub_paras.append(" ".join(cur_sentences))
                cur_sentences = [sent]
                cur_words = sent_words
            else:
                cur_sentences.append(sent)
                cur_words += sent_words

        if cur_sentences:
            sub_paras.append(" ".join(cur_sentences))

        return sub_paras if sub_paras else [para]

    def chunk_scene(self, scene_text: str, scene_idx: int) -> List[Dict[str, Any]]:
        """Splits a single scene into structured chunks respecting paragraph blocks."""
        raw_paragraphs = [p.strip() for p in scene_text.split("\n\n") if p.strip()]
        paragraphs: List[str] = []
        for p in raw_paragraphs:
            if len(p.split()) > self.max_chunk_words:
                paragraphs.extend(self._split_long_paragraph(p))
            else:
                paragraphs.append(p)

        chunks: List[Dict[str, Any]] = []

        current_paragraphs: List[str] = []
        current_word_count = 0

        for para in paragraphs:
            para_words = len(para.split())
            if current_word_count + para_words > self.max_chunk_words and current_paragraphs:
                # Flush existing chunk
                content = "\n\n".join(current_paragraphs)
                chunks.append({
                    "content": content,
                    "scene_number": scene_idx,
                    "word_count": len(content.split()),
                })
                current_paragraphs = [para]
                current_word_count = para_words
            else:
                current_paragraphs.append(para)
                current_word_count += para_words

        if current_paragraphs:
            content = "\n\n".join(current_paragraphs)
            chunks.append({
                "content": content,
                "scene_number": scene_idx,
                "word_count": len(content.split()),
            })

        return chunks

    def process(self, text: str) -> List[Dict[str, Any]]:
        """Performs full scene-aware chunking on manuscript text."""
        scenes = self.split_into_scenes(text)
        all_chunks: List[Dict[str, Any]] = []
        chunk_idx = 0

        for scene_idx, scene_text in enumerate(scenes, start=1):
            scene_chunks = self.chunk_scene(scene_text, scene_idx)
            for item in scene_chunks:
                item["chunk_index"] = chunk_idx
                all_chunks.append(item)
                chunk_idx += 1

        return all_chunks

