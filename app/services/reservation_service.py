"""
Reservation service for fetching and processing reservation data.
"""

import requests
import json
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ReservationNotFoundError, ExternalAPIError

logger = get_logger(__name__)


class ReservationService:
    """Service for handling reservation-related operations."""
    
    def __init__(self):
        self.base_url = settings.RESERVATION_API_BASE
        self.secret = settings.RESERVATION_API_SECRET
        self.timeout = settings.API_TIMEOUT
    
    async def get_reservation(self, reservation_id: str) -> Dict[str, Any]:
        """
        Fetch reservation data from the external API.
        
        Args:
            reservation_id: The unique identifier for the reservation
            
        Returns:
            Dictionary containing reservation information
            
        Raises:
            ReservationNotFoundError: If reservation is not found
            ExternalAPIError: If external API fails
        """
        try:
            logger.info(f"Fetching reservation data for ID: {reservation_id}")
            
            params = {
                "reservation_id": reservation_id,
                "secret": self.secret,
                "customPromptFieldType": "static",
                "returnDataOnly": "true",
                "truncateData": "false",
                "returnFields": "reservation-info",
                "aiPromptType": "summary",
                "textformat": "JSON"
            }
            
            response = requests.get(
                self.base_url, 
                params=params, 
                timeout=self.timeout
            )
            
            if response.status_code == 404:
                raise ReservationNotFoundError(reservation_id)
            
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("reservationInfos"):
                raise ReservationNotFoundError(reservation_id)
            
            reservation_data = data["reservationInfos"][0]
            
            logger.info(f"Successfully fetched reservation data for ID: {reservation_id}")
            return reservation_data
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch reservation data: {e}")
            raise ExternalAPIError("Reservation API", str(e))
        except ReservationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching reservation: {e}")
            raise ExternalAPIError("Reservation API", str(e))
    
    def extract_relevant_fields(self, reservation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant fields from reservation data for personalization.
        
        Args:
            reservation_data: Raw reservation data from API
            
        Returns:
            Dictionary with relevant fields extracted
        """
        return {
            "guest_name": f"{reservation_data.get('guest_name_preferred', '')} {reservation_data.get('sur_name', '')}".strip(),
            "city": reservation_data.get('city', ''),
            "building": reservation_data.get('building', ''),
            "property_type": reservation_data.get('property_type', ''),
            "number_of_guests": reservation_data.get('number_of_guests', '2'),
            "date_from": reservation_data.get('date_from', ''),
            "date_to": reservation_data.get('date_to', ''),
            "length_of_stay": reservation_data.get('length_of_stay', 1),
            "checkin_time": reservation_data.get('checkin_time', ''),
            "checkout_time": reservation_data.get('checkout_time', ''),
            "conversation_summary": reservation_data.get('conversation_summary', ''),
            "timezone": reservation_data.get('timezone', 'US/Eastern'),
            "property_id": reservation_data.get('property_id', ''),
            
            # Property details (already in reservations API)
            "property_address": f"{reservation_data.get('unit_number', '')} {reservation_data.get('building', '')}, {reservation_data.get('city', '')}",
            "property_neighborhood": reservation_data.get('city', ''),
            "property_amenities": [
                f"WiFi: {reservation_data.get('apt_wifi', 'N/A')}",
                f"Parking: {reservation_data.get('parking_spot_number', 'N/A')}",
                f"Access: {reservation_data.get('access_code', 'N/A')}"
            ],
            "property_description": reservation_data.get('listing_name', ''),
            
            # Conversation data (already in reservations API)
            "guest_preferences": self._extract_guest_preferences(reservation_data),
            "guest_feedback": reservation_data.get('conversation_summary', ''),
            "reservation_notes": reservation_data.get('initial_reservation_note', ''),
            "guest_requests": self._extract_guest_requests(reservation_data)
        }
    
    def _extract_guest_preferences(self, reservation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract guest preferences from reservation data."""
        preferences = {}
        
        # Extract from conversation summary
        if reservation_data.get('conversation_summary'):
            summary = reservation_data['conversation_summary'].lower()
            if 'positive' in summary or 'gratitude' in summary:
                preferences['sentiment'] = 'positive'
            if 'amazing' in summary:
                preferences['experience_rating'] = 'excellent'
        
        # Extract from initial notes
        if reservation_data.get('initial_reservation_note'):
            notes = reservation_data['initial_reservation_note'].lower()
            if 'early check-in' in notes:
                preferences['early_checkin'] = True
            if 'late check-out' in notes:
                preferences['late_checkout'] = True
        
        # Extract from comments
        if reservation_data.get('comments'):
            try:
                comments = json.loads(reservation_data['comments'])
                if 'default_comments' in comments:
                    default = comments['default_comments'].lower()
                    if 'children' in default:
                        preferences['has_children'] = True
                    if 'pets' in default:
                        preferences['has_pets'] = True
            except:
                pass
        
        return preferences
    
    def _extract_guest_requests(self, reservation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract specific guest requests from reservation data."""
        requests = {}
        
        # Check-in/check-out preferences
        if reservation_data.get('early_checkin'):
            requests['early_checkin'] = True
        if reservation_data.get('late_checkout'):
            requests['late_checkout'] = True
        
        # Special requirements
        if reservation_data.get('has_pet'):
            requests['pet_friendly'] = True
        if reservation_data.get('number_of_vehicles'):
            requests['parking_needed'] = True
        
        return requests
    
    def determine_group_type(self, reservation_data: Dict[str, Any]) -> str:
        """
        Determine the type of group based on reservation data.
        
        Args:
            reservation_data: Reservation data dictionary
            
        Returns:
            String representing the group type
        """
        guests = int(reservation_data.get('number_of_guests', 2))
        
        if guests == 1:
            return "solo_traveler"
        elif guests == 2:
            return "couple"
        elif guests <= 4:
            return "family_small"
        elif guests <= 6:
            return "family_large"
        else:
            return "group"
    
    def validate_reservation_data(self, reservation_data: Dict[str, Any]) -> bool:
        """
        Validate that reservation data contains required fields.
        
        Args:
            reservation_data: Reservation data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['guest_name_preferred', 'sur_name', 'city', 'building']
        
        for field in required_fields:
            if not reservation_data.get(field):
                logger.warning(f"Missing required field: {field}")
                return False
        
        return True
