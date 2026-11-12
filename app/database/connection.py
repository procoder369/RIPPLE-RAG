"""Database session and connection management."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import get_settings
from app.core.logging import logger
from app.database.models import Base

settings = get_settings()

# SQLite specific connect args if needed
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create tables if they do not exist."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.error(f"Error creating database tables: {exc}")
        raise


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

