"""Database setup and migration helper script."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import init_db
from app.core.logging import logger

if __name__ == "__main__":
    logger.info("Initializing RippleRAG Database...")
    init_db()
    logger.info("Database initialized successfully.")

