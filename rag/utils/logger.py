"""
Logger Configuration

Creates a logger that writes logs to:
1. Console
2. Log file
"""

import logging

from config import LOG_DIR

# Create logs directory if it doesn't exist
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


def setup_logger(name: str = "HealthcareFraudRAG"):
    """
    Create and return a configured logger.
    """

    logger = logging.getLogger(name)

    # Prevent duplicate log messages
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File Handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger