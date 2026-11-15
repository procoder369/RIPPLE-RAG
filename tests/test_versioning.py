"""Unit and integration tests for Story Workspace and Version Control."""

import pytest
from app.database.connection import SessionLocal, init_db
from app.database.models import Story, Chapter, StoryCommit
from app.core.version_control import VersionControlService


@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    yield db
    db.close()


def test_story_creation_and_manuscript(db_session):
    story = Story(title="Test Saga", description="Test universe")
    db_session.add(story)
    db_session.commit()
    db_session.refresh(story)

    # Add chapter
    ch1 = Chapter(
        story_id=story.id,
        chapter_index=1,
        title="Chapter 1: Dawn",
        raw_text="The hero stepped out into the morning fog.",
        word_count=8,
    )
    db_session.add(ch1)
    db_session.commit()
    db_session.refresh(ch1)

    assert ch1.id is not None
    assert ch1.story_id == story.id


def test_version_control_commits_and_diff(db_session):
    story = Story(title="Commit Test Story")
    db_session.add(story)
    db_session.commit()

    chapter = Chapter(
        story_id=story.id,
        chapter_index=1,
        title="Prologue",
        raw_text="Sir Galahad drew his sword with his right hand.",
        word_count=9,
    )
    db_session.add(chapter)
    db_session.commit()

    # Commit 1
    c1 = VersionControlService.create_commit(
        db=db_session,
        story_id=story.id,
        chapter_id=chapter.id,
        message="Initial prologue draft",
        text_content=chapter.raw_text,
    )
    assert c1.commit_hash is not None
    assert c1.parent_commit_hash is None

    # Commit 2: Modify text
    updated_text = "Sir Galahad drew his flaming sword with both hands."
    c2 = VersionControlService.create_commit(
        db=db_session,
        story_id=story.id,
        chapter_id=chapter.id,
        message="Enhanced combat detail",
        text_content=updated_text,
    )
    assert c2.parent_commit_hash == c1.commit_hash
    assert c2.diff_summary is not None
    assert "-Sir Galahad drew his sword" in c2.diff_summary
    assert "+Sir Galahad drew his flaming sword" in c2.diff_summary

    # Diff inspection
    diff_res = VersionControlService.get_diff(db_session, c1.commit_hash, c2.commit_hash)
    assert diff_res["additions"] >= 1
    assert diff_res["deletions"] >= 1

    # Rollback test
    rollback_res = VersionControlService.rollback(db_session, c1.commit_hash)
    assert rollback_res["reverted_to"] == c1.commit_hash

    # Confirm chapter was reverted
    db_session.refresh(chapter)
    assert chapter.raw_text == "Sir Galahad drew his sword with his right hand."

