"""API endpoints for Story Version Control, Commits, Diffs, and Rollbacks."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.api.schemas.versioning import (
    CreateCommitRequest,
    CommitResponse,
    CommitDetailResponse,
    DiffResponse,
    RollbackRequest,
    RollbackResponse,
)
from app.core.version_control import VersionControlService
from app.core.security import verify_service_token

router = APIRouter(prefix="/versioning", tags=["Story Version Control"])


@router.post("/commit", response_model=CommitResponse, status_code=status.HTTP_201_CREATED)
def create_commit(payload: CreateCommitRequest, db: Session = Depends(get_db)):
    """Record an explicit Git-like commit snapshot for a story or chapter."""
    try:
        commit = VersionControlService.create_commit(
            db=db,
            story_id=payload.story_id,
            chapter_id=payload.chapter_id,
            message=payload.message,
            text_content=payload.text_content,
            author=payload.author or "Author",
            branch=payload.branch or "main",
        )
        return commit
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/history/{story_id}", response_model=List[CommitResponse])
def get_commit_history(
    story_id: str,
    chapter_id: Optional[str] = Query(None, description="Optional filter by chapter ID"),
    branch: str = Query("main", description="Target branch"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Retrieve chronologically ordered commit history for a story or chapter."""
    return VersionControlService.get_history(
        db=db,
        story_id=story_id,
        chapter_id=chapter_id,
        branch=branch,
        limit=limit,
    )


@router.get("/commits/{commit_hash}", response_model=CommitDetailResponse)
def get_commit_details(commit_hash: str, db: Session = Depends(get_db)):
    """Retrieve full details and snapshot text for a specific commit."""
    from app.database.models import StoryCommit
    commit = db.query(StoryCommit).filter(StoryCommit.commit_hash == commit_hash).first()
    if not commit:
        raise HTTPException(status_code=404, detail="Commit not found")
    return commit


@router.get("/diff", response_model=DiffResponse)
def get_diff(
    from_commit: str = Query(..., description="Source commit hash"),
    to_commit: str = Query(..., description="Target commit hash"),
    db: Session = Depends(get_db),
):
    """Inspect line-by-line unified diff between two commits."""
    try:
        return VersionControlService.get_diff(
            db=db,
            from_commit_hash=from_commit,
            to_commit_hash=to_commit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/rollback", response_model=RollbackResponse)
def rollback_commit(payload: RollbackRequest, db: Session = Depends(get_db)):
    """Rollback a chapter/story to a past commit state."""
    try:
        return VersionControlService.rollback(
            db=db,
            commit_hash=payload.commit_hash,
            branch=payload.branch or "main",
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

