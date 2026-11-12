"""Embedding generator for story chunks and queries."""

import hashlib
import math
from typing import List
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class Embedder:
    """Generates dense vector representations for narrative text."""

    def __init__(self, model_name: str = None, dimension: int = None, local_fallback: bool = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.dimension = dimension or settings.EMBEDDING_DIM
        if local_fallback is not None:
            self.local_fallback = local_fallback
        else:
            self.local_fallback = settings.USE_LOCAL_EMBEDDING_FALLBACK or (self.model_name == "mock")
        self._model = None
        if not self.local_fallback:
            self._initialize_model()

    def _initialize_model(self) -> None:
        """Loads sentence-transformers model if available, else logs fallback."""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as exc:
            logger.warning(
                f"SentenceTransformer not loaded ({exc}). Using deterministic pseudo-embedding fallback."
            )
            self._model = None

    def embed_text(self, text: str) -> List[float]:
        """Generates embedding vector for a single piece of text."""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of texts."""
        if not texts:
            return []

        if self._model is not None:
            embeddings = self._model.encode(texts, convert_to_numpy=True)
            return [vec.tolist() for vec in embeddings]

        # Deterministic fallback embedding for dev/testing
        results: List[List[float]] = []
        for text in texts:
            vec = []
            for i in range(self.dimension):
                seed_str = f"{text}_{i}"
                digest = hashlib.sha256(seed_str.encode("utf-8")).hexdigest()
                val = (int(digest[:8], 16) / 0xFFFFFFFF) * 2.0 - 1.0
                vec.append(val)
            # Normalize vector to unit length
            norm = math.sqrt(sum(v * v for v in vec))
            if norm > 0:
                vec = [v / norm for v in vec]
            results.append(vec)

        return results
