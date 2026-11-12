"""API route for indexing story chapters (Pipeline A)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.api.schemas.indexing import IndexChapterRequest, IndexChapterResponse
from app.pipelines.indexing_pipeline import IndexingPipeline
from app.core.security import verify_service_token

router = APIRouter(prefix="/indexing", tags=["Indexing"])
pipeline = IndexingPipeline()


@router.post(
    "/chapter",
    response_model=IndexChapterResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_service_token)],
)
def index_chapter(
    payload: IndexChapterRequest,
    db: Session = Depends(get_db),
):
    """
    Ingests chapter text, executes scene-aware chunking, generates embeddings,
    extracts proposed story facts, and stores everything for RAG retrieval.
    """
    try:
        result = pipeline.run(
            db=db,
            story_id=payload.story_id,
            chapter_title=payload.chapter_title,
            chapter_index=payload.chapter_index,
            raw_text=payload.raw_text,
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Indexing failed: {str(exc)}",
        )

