"""
Property service for fetching and processing property data.
"""

import requests
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import PropertyNotFoundError, ExternalAPIError

logger = get_logger(__name__)


class PropertyService:
    """Service for handling property-related operations."""
    
    def __init__(self):
        # Note: Properties are now included in the main reservation API
        # This service is kept for potential future use or fallback
        self.timeout = settings.API_TIMEOUT
    
    async def get_property(self, property_id: str) -> Optional[Dict[str, Any]]:
        """
        Get property data. Since properties are now included in reservations,
        this method returns None to indicate no separate property fetch is needed.
        
        Args:
            property_id: The unique identifier for the property
            
        Returns:
            None - properties are embedded in reservation data
        """
        logger.info(f"Property {property_id} data is embedded in reservation data - no separate fetch needed")
        return None
    
    def enrich_reservation_data(
        self, 
        reservation_data: Dict[str, Any], 
        property_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Enrich reservation data with property information.
        
        Args:
            reservation_data: Raw reservation data
            property_data: Property details
            
        Returns:
            Enriched reservation data
        """
        if not property_data:
            return reservation_data
        
        # Add property details to reservation data
        enriched_data = reservation_data.copy()
        enriched_data.update({
            "property_address": property_data.get('address', ''),
            "property_city": property_data.get('city', reservation_data.get('city', '')),
            "property_state": property_data.get('state', ''),
            "property_country": property_data.get('country', ''),
            "property_amenities": property_data.get('amenities', []),
            "property_neighborhood": property_data.get('neighborhood', ''),
            "property_description": property_data.get('description', ''),
            "property_latitude": property_data.get('latitude'),
            "property_longitude": property_data.get('longitude')
        })
        
        return enriched_data
