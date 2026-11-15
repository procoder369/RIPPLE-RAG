"""Version control service for tracking story revisions, diffs, commits, and rollbacks."""

import difflib
import hashlib
import time
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import StoryCommit, Chapter, Story


class VersionControlService:
    """Manages Git-like commits, diffs, and snapshots for stories and chapters."""

    @staticmethod
    def _generate_commit_hash(content: str, message: str, timestamp: float) -> str:
        raw_seed = f"{content}::{message}::{timestamp}"
        return hashlib.sha1(raw_seed.encode("utf-8")).hexdigest()

    @classmethod
    def create_commit(
        cls,
        db: Session,
        story_id: str,
        message: str,
        text_content: str,
        chapter_id: Optional[str] = None,
        author: str = "Author",
        branch: str = "main",
    ) -> StoryCommit:
        """Creates a snapshot commit and computes diff against previous head."""
        # Find latest commit for this story/chapter/branch
        query = db.query(StoryCommit).filter(
            StoryCommit.story_id == story_id,
            StoryCommit.branch == branch,
        )
        if chapter_id:
            query = query.filter(StoryCommit.chapter_id == chapter_id)
        
        last_commit = query.order_by(StoryCommit.created_at.desc()).first()
        parent_hash = last_commit.commit_hash if last_commit else None

        # Compute unified diff
        diff_summary = ""
        if last_commit and last_commit.snapshot_text:
            prev_lines = last_commit.snapshot_text.splitlines(keepends=True)
            curr_lines = text_content.splitlines(keepends=True)
            diff_lines = list(difflib.unified_diff(
                prev_lines,
                curr_lines,
                fromfile=f"a/{parent_hash[:7]}",
                tofile="b/current",
                lineterm="",
            ))
            diff_summary = "\n".join(diff_lines)

        commit_hash = cls._generate_commit_hash(text_content, message, time.time())

        commit = StoryCommit(
            commit_hash=commit_hash,
            story_id=story_id,
            chapter_id=chapter_id,
            author=author,
            message=message,
            branch=branch,
            snapshot_text=text_content,
            diff_summary=diff_summary,
            parent_commit_hash=parent_hash,
        )
        db.add(commit)
        db.commit()
        db.refresh(commit)
        return commit

    @classmethod
    def get_history(
        cls,
        db: Session,
        story_id: str,
        chapter_id: Optional[str] = None,
        branch: str = "main",
        limit: int = 50,
    ) -> List[StoryCommit]:
        """Returns commit history in reverse chronological order."""
        query = db.query(StoryCommit).filter(
            StoryCommit.story_id == story_id,
            StoryCommit.branch == branch,
        )
        if chapter_id:
            query = query.filter(StoryCommit.chapter_id == chapter_id)
        
        return query.order_by(StoryCommit.created_at.desc()).limit(limit).all()

    @classmethod
    def get_diff(
        cls,
        db: Session,
        from_commit_hash: str,
        to_commit_hash: str,
    ) -> Dict[str, Any]:
        """Calculates line-by-line diff and addition/deletion counts between two commits."""
        commit1 = db.query(StoryCommit).filter(StoryCommit.commit_hash == from_commit_hash).first()
        commit2 = db.query(StoryCommit).filter(StoryCommit.commit_hash == to_commit_hash).first()

        if not commit1 or not commit2:
            raise ValueError("One or both commits not found")

        text1 = commit1.snapshot_text.splitlines(keepends=True)
        text2 = commit2.snapshot_text.splitlines(keepends=True)

        diff_lines = list(difflib.unified_diff(
            text1,
            text2,
            fromfile=f"commit-{from_commit_hash[:7]}",
            tofile=f"commit-{to_commit_hash[:7]}",
            lineterm="",
        ))

        additions = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
        deletions = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))

        return {
            "from_commit": from_commit_hash,
            "to_commit": to_commit_hash,
            "diff": "\n".join(diff_lines),
            "additions": additions,
            "deletions": deletions,
        }

    @classmethod
    def rollback(
        cls,
        db: Session,
        commit_hash: str,
        branch: str = "main",
    ) -> Dict[str, Any]:
        """Rolls back the chapter or story to a previous commit state and creates a revert commit."""
        target_commit = db.query(StoryCommit).filter(StoryCommit.commit_hash == commit_hash).first()
        if not target_commit:
            raise ValueError(f"Commit '{commit_hash}' not found")

        # Update the live chapter raw_text if chapter_id is attached
        if target_commit.chapter_id:
            chapter = db.query(Chapter).filter(Chapter.id == target_commit.chapter_id).first()
            if chapter:
                chapter.raw_text = target_commit.snapshot_text
                chapter.word_count = len(target_commit.snapshot_text.split())
                db.commit()

        # Create a new commit documenting the revert
        revert_commit = cls.create_commit(
            db=db,
            story_id=target_commit.story_id,
            chapter_id=target_commit.chapter_id,
            message=f"Revert to commit {commit_hash[:7]}: {target_commit.message}",
            text_content=target_commit.snapshot_text,
            author="Rollback System",
            branch=branch,
        )

        return {
            "message": f"Successfully reverted to commit {commit_hash[:7]}",
            "current_commit_hash": revert_commit.commit_hash,
            "chapter_id": target_commit.chapter_id,
            "reverted_to": commit_hash,
        }

