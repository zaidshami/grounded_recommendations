"""
Chat endpoint for interactive guest recommendations.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.recommendation_service import RecommendationService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat_with_guest(request: ChatRequest):
    """
    Chat endpoint for interactive conversations with guests.
    
    This endpoint maintains conversation history and provides contextual responses
    based on the guest's reservation, property details, and conversation history.
    """
    try:
        logger.info(f"Chat request for reservation: {request.reservation_id}")
        
        # Initialize recommendation service
        recommendation_service = RecommendationService()
        
        # First, fetch the reservation data using the reservation_id
        # We'll use the same API that the frontend uses
        import requests
        from app.core.config import settings
        
        reservation_url = f"https://api.gptpricing.com/zendesk-comments/ai-summary?reservation_id={request.reservation_id}&secret=agentsecretnjzd7f89asa878d97asd&customPromptFieldType=static&returnDataOnly=true&truncateData=false&returnFields=reservation-info,comments-info&aiPromptType=summary&textformat=JSON"
        
        try:
            reservation_response = requests.get(reservation_url, timeout=30)
            if reservation_response.status_code == 200:
                reservation_data = reservation_response.json()
                logger.info(f"Successfully fetched reservation data for ID: {request.reservation_id}")
            else:
                logger.error(f"Failed to fetch reservation data: {reservation_response.status_code}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to fetch reservation data for ID: {request.reservation_id}"
                )
        except requests.RequestException as e:
            logger.error(f"Error fetching reservation data: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Error fetching reservation data: {str(e)}"
            )
        
        # Handle chat interaction with the actual reservation data
        logger.info(f"Calling handle_chat_only_interaction for message: '{request.message[:50]}...'")
        logger.info(f"Conversation history length: {len(request.conversation_history)}")
        
        response = await recommendation_service.handle_chat_only_interaction(
            reservation_data=reservation_data,
            user_message=request.message,
            conversation_history=request.conversation_history
        )
        
        logger.info(f"Chat response generated with message ID: {response.get('message_id', 'unknown')}")
        logger.info(f"Response content preview: {response.get('response', '')[:100]}...")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )
