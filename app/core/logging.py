"""Application logging configuration for RippleRAG."""

import logging
import sys
from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> logging.Logger:
    """Configures structured stream logging."""
    logger = logging.getLogger("ripplerag")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s:%(module)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    return logger


logger = setup_logging()

