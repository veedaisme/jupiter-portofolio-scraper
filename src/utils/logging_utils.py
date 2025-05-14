"""Logging utilities for the portfolio scraper application."""

import logging
import sys
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and level.
    
    Args:
        name: Name of the logger
        level: Logging level
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


# Create a default logger for the application
logger = setup_logger("portfolio_scraper")


def log_exception(e: Exception, message: Optional[str] = None) -> None:
    """
    Log an exception with an optional message.
    
    Args:
        e: Exception to log
        message: Optional message to include
    """
    if message:
        logger.error(f"{message}: {str(e)}")
    else:
        logger.error(str(e))
    logger.debug("Exception details:", exc_info=True)
