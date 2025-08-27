"""
Logging configuration for the Guest Recommendation Generation API.
"""

import logging
import sys
from typing import Any, Dict
from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    
    # Create formatter
    formatter = logging.Formatter(
        fmt=settings.LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    root_logger.addHandler(console_handler)
    
    # File handler for production
    if not settings.DEBUG:
        try:
            file_handler = logging.FileHandler("app.log")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)
            root_logger.addHandler(file_handler)
        except Exception as e:
            logging.warning(f"Could not create file handler: {e}")
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Log startup
    logging.info(f"Logging configured with level: {settings.LOG_LEVEL}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


# Structured logging helpers
def log_api_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration: float,
    **kwargs: Any
) -> None:
    """Log API request details in a structured way."""
    logger.info(
        "API Request",
        extra={
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            **kwargs
        }
    )


def log_recommendation_generation(
    logger: logging.Logger,
    reservation_id: str,
    guest_name: str,
    duration: float,
    recommendations_count: int,
    **kwargs: Any
) -> None:
    """Log recommendation generation details."""
    logger.info(
        "Recommendations Generated",
        extra={
            "reservation_id": reservation_id,
            "guest_name": guest_name,
            "duration_ms": round(duration * 1000, 2),
            "recommendations_count": recommendations_count,
            **kwargs
        }
    )
