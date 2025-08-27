"""
Chat request and response schemas for the Guest Recommendation Generation API.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Individual chat message structure."""
    
    message_id: str = Field(..., description="Unique identifier for the message")
    role: str = Field(..., description="Who sent the message (user/assistant)")
    content: str = Field(..., description="The message content")
    timestamp: datetime = Field(..., description="When the message was sent")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional message metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message_id": "msg_20250116_143022_1234",
                "role": "user",
                "content": "I'm looking for good Italian restaurants near the hotel",
                "timestamp": "2025-01-16T14:30:22.123Z",
                "metadata": {"reservation_id": "142766272"}
            }
        }
    }


class ChatRequest(BaseModel):
    """Request schema for chat interactions."""
    
    reservation_id: str = Field(..., description="The reservation ID to get context for")
    message: str = Field(..., description="The user's message")
    conversation_history: List[ChatMessage] = Field(default=[], description="Previous conversation messages")
    include_conversation_context: bool = Field(default=True, description="Whether to include conversation data")
    max_recommendations: Optional[int] = Field(default=None, description="Maximum number of recommendations to generate")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "reservation_id": "142766272",
                "message": "I'm looking for good Italian restaurants near the hotel",
                "conversation_history": [],
                "include_conversation_context": True,
                "max_recommendations": 5
            }
        }
    }


class ChatResponse(BaseModel):
    """Response schema for chat interactions."""
    
    message_id: str = Field(..., description="Unique identifier for the response message")
    response: str = Field(..., description="The AI-generated response")
    recommendations: Optional[Dict[str, Any]] = Field(default=None, description="Generated recommendations (optional for fast chat)")
    timestamp: str = Field(..., description="When the response was generated")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message_id": "msg_20250116_143022_1234",
                "response": "I'd be happy to help you find great Italian restaurants! Based on your location in New Haven...",
                "recommendations": {
                    "guest_name": "Guest",
                    "destination": "New Haven",
                    "stay_dates": "N/A",
                    "recommendations": [
                        {
                            "name": "Sally's Apizza",
                            "type": "Restaurant",
                            "category": "Italian",
                            "rating": 4.5,
                            "distance": "0.3 miles",
                            "description": "Famous New Haven pizza institution"
                        }
                    ]
                },
                "timestamp": "2025-01-16T14:30:22.123Z"
            }
        }
    }
