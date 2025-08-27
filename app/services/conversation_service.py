"""
Conversation service for fetching and processing conversation data.
"""

import requests
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ConversationNotFoundError, ExternalAPIError

logger = get_logger(__name__)


class ConversationService:
    """Service for handling conversation-related operations."""
    
    def __init__(self):
        # Note: Conversations are now included in the main reservation API
        # This service is kept for potential future use or fallback
        self.timeout = settings.API_TIMEOUT
    
    async def get_conversation(self, reservation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation data. Since conversations are now included in reservations,
        this method returns None to indicate no separate conversation fetch is needed.
        
        Args:
            reservation_id: The reservation ID to fetch conversations for
            
        Returns:
            None - conversations are embedded in reservation data
        """
        logger.info(f"Conversation data for reservation {reservation_id} is embedded in reservation data - no separate fetch needed")
        return None
    
    def extract_preferences(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract guest preferences from conversation data.
        
        Args:
            conversation_data: Raw conversation data
            
        Returns:
            Dictionary with extracted preferences
        """
        if not conversation_data:
            return {}
        
        preferences = {}
        
        # Extract preferences if they exist
        if 'preferences' in conversation_data:
            preferences.update(conversation_data['preferences'])
        
        # Extract sentiment
        if 'sentiment' in conversation_data:
            preferences['sentiment'] = conversation_data['sentiment']
        
        # Extract summary
        if 'summary' in conversation_data:
            preferences['summary'] = conversation_data['summary']
        
        # Extract key topics from messages if available
        if 'messages' in conversation_data:
            messages = conversation_data['messages']
            topics = []
            for msg in messages:
                if msg.get('role') == 'guest':
                    content = msg.get('content', '').lower()
                    # Simple topic extraction
                    if 'restaurant' in content or 'food' in content or 'dining' in content:
                        topics.append('dining')
                    if 'activity' in content or 'attraction' in content or 'visit' in content:
                        topics.append('attractions')
                    if 'shopping' in content or 'store' in content or 'mall' in content:
                        topics.append('shopping')
                    if 'transport' in content or 'parking' in content or 'walk' in content:
                        topics.append('transportation')
            
            if topics:
                preferences['topics_of_interest'] = list(set(topics))
        
        return preferences
    
    def build_conversation_context(
        self, 
        conversation_data: Optional[Dict[str, Any]], 
        reservation_data: Dict[str, Any]
    ) -> str:
        """
        Build conversation context for AI recommendations.
        
        Args:
            conversation_data: Conversation data
            reservation_data: Reservation data
            
        Returns:
            Formatted conversation context string
        """
        if not conversation_data:
            return "No conversation history available."
        
        context_parts = []
        
        # Add conversation summary if available
        if conversation_data.get('summary'):
            context_parts.append(f"Conversation Summary: {conversation_data['summary']}")
        
        # Add preferences if available
        preferences = self.extract_preferences(conversation_data)
        if preferences:
            context_parts.append(f"Guest Preferences: {preferences}")
        
        # Add recent messages context
        if conversation_data.get('messages'):
            messages = conversation_data['messages']
            recent_messages = messages[-3:] if len(messages) > 3 else messages
            
            message_context = []
            for msg in recent_messages:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:100]  # Limit content length
                message_context.append(f"{role}: {content}")
            
            if message_context:
                context_parts.append(f"Recent Messages: {' | '.join(message_context)}")
        
        return " | ".join(context_parts) if context_parts else "No conversation history available."
