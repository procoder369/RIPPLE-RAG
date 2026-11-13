"""Core application configuration module for RippleRAG."""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime settings."""

    # Application
    APP_NAME: str = "RippleRAG"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "ripple-rag-insecure-dev-key-change-in-prod"
    SERVICE_AUTH_TOKEN: str = "dev-secret-token"

    # Database
    # Supports postgresql:// or sqlite:///
    DATABASE_URL: str = "sqlite:///./ripplerag_dev.db"

    # Embeddings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    USE_LOCAL_EMBEDDING_FALLBACK: bool = True

    # LLM Settings
    LLM_PROVIDER: str = "ollama"  # "mock", "anthropic", "openai", "gemini", "ollama"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None  # e.g. "http://localhost:11434/v1" for Ollama or LM Studio
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "claude-3-5-sonnet-20241022"
    LLM_TEMPERATURE: float = 0.2

    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"  # or mistral, qwen2.5, phi3
    OLLAMA_EMBED_MODEL: str = "all-minilm"  # or nomic-embed-text

    # Narrative Graph & Continuity
    MAX_GRAPH_DEPTH: int = 4
    RIPPLE_IMPACT_THRESHOLD: float = 0.65

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Singleton getter for cached settings."""
    return Settings()

