"""Health check endpoint."""

from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health")
def health_check():
    """Returns runtime health status and configuration info."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "llm_provider": settings.LLM_PROVIDER,
    }

