"""API route for ripple and what-if narrative impact analysis."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.api.schemas.canon import WhatIfAnalysisRequest
from app.continuity.ripple_analyzer import RippleAnalyzer
from app.core.security import verify_service_token

router = APIRouter(prefix="/ripple", tags=["What-If & Ripple Analysis"])


@router.post(
    "/analyze",
    dependencies=[Depends(verify_service_token)],
)
def run_what_if_analysis(
    payload: WhatIfAnalysisRequest,
    db: Session = Depends(get_db),
):
    """
    Performs counterfactual dependency traversal across CanonGraph and chapter sequence
    to calculate ripple effects of changing an event or character status.
    """
    try:
        result = RippleAnalyzer.analyze_what_if(
            db=db,
            story_id=payload.story_id,
            hypothesis_description=payload.hypothesis_description,
            target_entity_name=payload.target_entity_name,
            changed_at_chapter=payload.changed_at_chapter,
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ripple analysis failed: {str(exc)}",
        )

