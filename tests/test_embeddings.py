"""Unit tests for Embedder."""

import pytest
import math
from app.ingestion.embedder import Embedder


def test_embed_dimension_and_normalization():
    embedder = Embedder(dimension=128, local_fallback=True)
    vec = embedder.embed_text("Lord Matthew rode to the northern bridge.")
    assert len(vec) == 128
    # Check unit norm
    norm = math.sqrt(sum(v * v for v in vec))
    assert abs(norm - 1.0) < 1e-4


def test_embed_batch():
    embedder = Embedder(dimension=64, local_fallback=True)
    texts = ["First passage", "Second passage"]
    vectors = embedder.embed_batch(texts)
    assert len(vectors) == 2
    assert len(vectors[0]) == 64
    assert len(vectors[1]) == 64
