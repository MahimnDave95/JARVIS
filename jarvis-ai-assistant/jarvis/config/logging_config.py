"""
Logging configuration using loguru.
Handles console and file logging with rotation.
"""

import sys
from loguru import logger
from jarvis.config.settings import LOGS_DIR

def setup_logging():
    """Configure loguru logger with console and file handlers."""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with color
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # File handler with rotation (10 MB max, keep 5 backups)
    log_file = LOGS_DIR / "jarvis.log"
    logger.add(
        str(log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="5 days",
        compression="zip",
        encoding="utf-8"
    )
    
    logger.info("Logging configured successfully")
    return logger