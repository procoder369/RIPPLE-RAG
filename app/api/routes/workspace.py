"""API endpoints for Story Workspace and Chapter Management."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Story, Chapter
from app.api.schemas.workspace import (
    CreateStoryRequest,
    StoryResponse,
    CreateChapterRequest,
    UpdateChapterRequest,
    ChapterDetailResponse,
    ChapterSummary,
    ManuscriptResponse,
    ReorderChaptersRequest,
)
from app.core.version_control import VersionControlService
from app.core.security import verify_service_token

router = APIRouter(prefix="/workspace", tags=["Story Workspace"])


@router.post("/stories", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
def create_story(payload: CreateStoryRequest, db: Session = Depends(get_db)):
    """Create a new story universe / manuscript."""
    story = Story(
        title=payload.title,
        description=payload.description,
        author_id=payload.author_id,
    )
    db.add(story)
    db.commit()
    db.refresh(story)
    return story


@router.get("/stories", response_model=List[StoryResponse])
def list_stories(db: Session = Depends(get_db)):
    """List all stories in the workspace."""
    return db.query(Story).order_by(Story.created_at.desc()).all()


@router.get("/stories/{story_id}", response_model=StoryResponse)
def get_story(story_id: str, db: Session = Depends(get_db)):
    """Get metadata for a specific story."""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


@router.get("/stories/{story_id}/manuscript", response_model=ManuscriptResponse)
def get_full_manuscript(story_id: str, db: Session = Depends(get_db)):
    """View the complete manuscript with all chapters ordered sequentially."""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    chapters = (
        db.query(Chapter)
        .filter(Chapter.story_id == story_id)
        .order_by(Chapter.chapter_index.asc())
        .all()
    )

    total_words = sum(c.word_count or 0 for c in chapters)

    return ManuscriptResponse(
        story_id=story.id,
        story_title=story.title,
        total_chapters=len(chapters),
        total_words=total_words,
        chapters=[ChapterDetailResponse.from_orm(c) for c in chapters],
    )


@router.get("/stories/{story_id}/chapters", response_model=List[ChapterSummary])
def list_chapters(story_id: str, db: Session = Depends(get_db)):
    """List all chapters in order with summary metadata."""
    return (
        db.query(Chapter)
        .filter(Chapter.story_id == story_id)
        .order_by(Chapter.chapter_index.asc())
        .all()
    )


@router.post("/stories/{story_id}/chapters", response_model=ChapterDetailResponse, status_code=status.HTTP_201_CREATED)
def create_chapter(story_id: str, payload: CreateChapterRequest, db: Session = Depends(get_db)):
    """Write or upload a chapter to a story manuscript."""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    word_count = len(payload.raw_text.split())
    chapter = Chapter(
        story_id=story_id,
        chapter_index=payload.chapter_index,
        title=payload.title,
        raw_text=payload.raw_text,
        word_count=word_count,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    # Automatically record an initial commit for this chapter
    VersionControlService.create_commit(
        db=db,
        story_id=story_id,
        chapter_id=chapter.id,
        message=f"Initial draft: {payload.title}",
        text_content=payload.raw_text,
    )

    return chapter


@router.get("/chapters/{chapter_id}", response_model=ChapterDetailResponse)
def get_chapter(chapter_id: str, db: Session = Depends(get_db)):
    """Read full text of a specific chapter."""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.put("/chapters/{chapter_id}", response_model=ChapterDetailResponse)
def update_chapter(chapter_id: str, payload: UpdateChapterRequest, db: Session = Depends(get_db)):
    """Edit chapter manuscript and automatically log a version commit."""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    if payload.title is not None:
        chapter.title = payload.title
    if payload.chapter_index is not None:
        chapter.chapter_index = payload.chapter_index
    if payload.raw_text is not None:
        chapter.raw_text = payload.raw_text
        chapter.word_count = len(payload.raw_text.split())

    db.commit()
    db.refresh(chapter)

    commit_msg = payload.commit_message or f"Update chapter: {chapter.title}"
    VersionControlService.create_commit(
        db=db,
        story_id=chapter.story_id,
        chapter_id=chapter.id,
        message=commit_msg,
        text_content=chapter.raw_text,
    )

    return chapter


@router.post("/stories/{story_id}/chapters/reorder")
def reorder_chapters(story_id: str, payload: ReorderChaptersRequest, db: Session = Depends(get_db)):
    """Reorder and organise chapters in the story manuscript."""
    for new_idx, chapter_id in enumerate(payload.chapter_order, start=1):
        ch = db.query(Chapter).filter(Chapter.id == chapter_id, Chapter.story_id == story_id).first()
        if ch:
            ch.chapter_index = new_idx
    db.commit()
    return {"message": "Chapters successfully reordered", "total_reordered": len(payload.chapter_order)}

