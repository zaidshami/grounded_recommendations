"""
Custom exceptions for the Guest Recommendation Generation API.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for API errors."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra_data = extra_data or {}


class ReservationNotFoundError(BaseAPIException):
    """Raised when a reservation is not found."""
    
    def __init__(self, reservation_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with ID '{reservation_id}' not found",
            error_code="RESERVATION_NOT_FOUND",
            extra_data={"reservation_id": reservation_id}
        )


class PropertyNotFoundError(BaseAPIException):
    """Raised when a property is not found."""
    
    def __init__(self, property_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Property with ID '{property_id}' not found",
            error_code="PROPERTY_NOT_FOUND",
            extra_data={"property_id": property_id}
        )


class ConversationNotFoundError(BaseAPIException):
    """Raised when conversation data is not found."""
    
    def __init__(self, reservation_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation data for reservation '{reservation_id}' not found",
            error_code="CONVERSATION_NOT_FOUND",
            extra_data={"reservation_id": reservation_id}
        )


class GeminiError(BaseAPIException):
    """Raised when Gemini API fails."""
    
    def __init__(self, error_message: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable",
            error_code="GEMINI_ERROR",
            extra_data={"original_error": error_message}
        )


class GooglePlacesError(BaseAPIException):
    """Raised when Google Places API fails."""
    
    def __init__(self, error_message: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Location service temporarily unavailable",
            error_code="GOOGLE_PLACES_ERROR",
            extra_data={"original_error": error_message}
        )


class ExternalAPIError(BaseAPIException):
    """Raised when external APIs fail."""
    
    def __init__(self, api_name: str, error_message: str):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"External service '{api_name}' temporarily unavailable",
            error_code="EXTERNAL_API_ERROR",
            extra_data={"api_name": api_name, "original_error": error_message}
        )


class ValidationError(BaseAPIException):
    """Raised when request validation fails."""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error in field '{field}': {message}",
            error_code="VALIDATION_ERROR",
            extra_data={"field": field, "message": message}
        )


class RateLimitExceededError(BaseAPIException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, limit: int, window: str):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {limit} requests per {window}",
            error_code="RATE_LIMIT_EXCEEDED",
            extra_data={"limit": limit, "window": window}
        )


def handle_exception(exc: Exception) -> Dict[str, Any]:
    """Convert any exception to a standardized error response."""
    
    if isinstance(exc, BaseAPIException):
        return {
            "error": True,
            "error_code": exc.error_code,
            "message": exc.detail,
            "status_code": exc.status_code,
            "extra_data": exc.extra_data
        }
    
    # Handle unexpected exceptions
    return {
        "error": True,
        "error_code": "INTERNAL_SERVER_ERROR",
        "message": "An unexpected error occurred",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "extra_data": {"original_error": str(exc)}
    }
