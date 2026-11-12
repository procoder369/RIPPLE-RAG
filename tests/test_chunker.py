"""Unit tests for SceneAwareChunker."""

import pytest
from app.ingestion.chunker import SceneAwareChunker


def test_scene_splitting():
    text = """
    Scene one begins here with character introduction.
    
    ***
    
    Scene two shifts to the mountain fortress.
    """
    chunker = SceneAwareChunker(target_chunk_words=100, max_chunk_words=200)
    scenes = chunker.split_into_scenes(text)
    assert len(scenes) == 2
    assert "Scene one" in scenes[0]
    assert "Scene two" in scenes[1]


def test_chunking_preserves_dialogue():
    text = (
        '"Do not venture past the river," said Kaelen.\n\n'
        '"I am not afraid," replied Matthew, unsheathing his sword.\n\n'
        '***\n\n'
        'The forest was quiet.'
    )
    chunker = SceneAwareChunker(target_chunk_words=50, max_chunk_words=100)
    chunks = chunker.process(text)
    assert len(chunks) >= 2
    assert chunks[0]["scene_number"] == 1
    assert chunks[-1]["scene_number"] == 2

