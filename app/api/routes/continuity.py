"""API route for contradiction checking and continuity audits."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.api.schemas.continuity import ContinuityCheckRequest, ContinuityCheckResponse
from app.continuity.contradiction import ContradictionDetector
from app.core.security import verify_service_token

router = APIRouter(prefix="/continuity", tags=["Continuity Engine"])
detector = ContradictionDetector()


@router.post(
    "/check",
    response_model=ContinuityCheckResponse,
    dependencies=[Depends(verify_service_token)],
)
def check_continuity(
    payload: ContinuityCheckRequest,
    db: Session = Depends(get_db),
):
    """
    Audits a new scene or manuscript excerpt against canon facts and character statuses
    to detect plot contradictions or physical timeline paradoxes.
    """
    try:
        result = detector.analyze_manuscript(
            db=db,
            story_id=payload.story_id,
            chapter_index=payload.chapter_index,
            text=payload.manuscript_text,
            mentioned_characters=payload.mentioned_characters,
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Continuity check failed: {str(exc)}",
        )

