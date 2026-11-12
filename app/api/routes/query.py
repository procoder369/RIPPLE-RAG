"""API route for asking questions about stories (Pipeline B)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.api.schemas.query import StoryQueryRequest, StoryQueryResponse
from app.pipelines.rag_pipeline import RAGPipeline
from app.core.security import verify_service_token

router = APIRouter(prefix="/query", tags=["Story Q&A"])
rag_pipeline = RAGPipeline()


@router.post(
    "/ask",
    response_model=StoryQueryResponse,
    dependencies=[Depends(verify_service_token)],
)
def ask_story_question(
    payload: StoryQueryRequest,
    db: Session = Depends(get_db),
):
    """
    Executes hybrid retrieval (dense + sparse + graph), generates a grounded answer,
    and returns citations and verification diagnostics.
    """
    try:
        result = rag_pipeline.run(
            db=db,
            story_id=payload.story_id,
            query=payload.query,
            top_k=payload.top_k,
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(exc)}",
        )

