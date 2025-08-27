"""
Recommendations endpoint for direct JSON recommendations.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.core.logging import get_logger
from app.schemas.recommendations import RecommendationRequest, RecommendationResponse
from app.services.recommendation_service import RecommendationService
from datetime import datetime

logger = get_logger(__name__)
router = APIRouter()


@router.post("/generate", response_model=RecommendationResponse)
async def generate_recommendations(
    request: RecommendationRequest,
    background_tasks: BackgroundTasks
):
    """
    Direct recommendations endpoint - returns JSON recommendations without chat interaction.
    
    Use this for one-time requests or when you just need the data.
    Both chat and direct endpoints use the same underlying recommendation tool.
    """
    try:
        logger.info(f"Generating recommendations for reservation: {request.reservation_id}")
        
        # Initialize recommendation service
        recommendation_service = RecommendationService()
        
        # Fetch all data from single reservations API
        reservation_data = await recommendation_service.reservation_service.get_reservation(
            request.reservation_id
        )
        
        # Generate AI-powered recommendations with all data
        ai_recommendations = await recommendation_service.generate_recommendations(
            reservation_data
        )
        
        # Enrich with Google Places data if available
        location = f"{reservation_data.get('city', '')}, {reservation_data.get('building', '')}"
        enriched_recommendations = await recommendation_service.enrich_with_google_places(
            ai_recommendations["recommendations"],
            location
        )
        
        # Limit recommendations if requested
        if request.max_recommendations and len(enriched_recommendations) > request.max_recommendations:
            enriched_recommendations = enriched_recommendations[:request.max_recommendations]
        
        # Build response
        relevant_fields = recommendation_service.reservation_service.extract_relevant_fields(
            reservation_data
        )
        group_type = recommendation_service.reservation_service.determine_group_type(reservation_data)
        
        # Generate a unique request ID
        request_id = f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.reservation_id) % 10000}"
        
        response = RecommendationResponse(
            request_id=request_id,
            reservation_id=request.reservation_id,
            recommendations=enriched_recommendations,
            personalization_summary=ai_recommendations.get("ai_analysis", ""),
            group_type=group_type,
            generated_at=datetime.now()
        )
        
        logger.info(f"Successfully generated {len(enriched_recommendations)} recommendations")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )
