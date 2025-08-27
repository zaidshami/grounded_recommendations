"""
Reservations endpoint for getting reservation details.
"""

from fastapi import APIRouter, HTTPException
from app.core.logging import get_logger
from app.services.reservation_service import ReservationService
from app.services.property_service import PropertyService

logger = get_logger(__name__)
router = APIRouter()


@router.get("/{reservation_id}")
async def get_reservation_details(reservation_id: str):
    """
    Get reservation details (useful for debugging and verification).
    
    Returns comprehensive reservation information including:
    - Basic reservation details
    - Guest information
    - Property details (if available)
    - Relevant fields for personalization
    """
    try:
        logger.info(f"Fetching reservation details for ID: {reservation_id}")
        
        # Initialize services
        reservation_service = ReservationService()
        
        # Fetch reservation data (includes all property and conversation data)
        reservation_data = await reservation_service.get_reservation(reservation_id)
        
        # Extract relevant fields (includes property and conversation data)
        relevant_fields = reservation_service.extract_relevant_fields(
            reservation_data
        )
        
        # Determine group type
        group_type = reservation_service.determine_group_type(reservation_data)
        
        # Validate data
        is_valid = reservation_service.validate_reservation_data(reservation_data)
        
        return {
            "reservation_id": reservation_id,
            "is_valid": is_valid,
            "relevant_fields": relevant_fields,
            "group_type": group_type,
            "raw_data": reservation_data,
            "data_sources": {
                "reservations": " Available (includes all data)",
                "properties": " Available (embedded in reservations)",
                "conversations": " Available (embedded in reservations)"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching reservation details: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=str(e)
        )
