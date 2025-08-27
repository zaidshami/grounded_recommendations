"""
Recommendation schemas for the Guest Recommendation Generation API.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    """Individual recommendation item structure."""
    
    name: str = Field(..., description="Name of the recommended item")
    type: str = Field(..., description="Type of recommendation (restaurant, activity, etc.)")
    category: str = Field(..., description="Category within the type")
    description: str = Field(..., description="Detailed description")
    rating: Optional[float] = Field(None, description="Rating if available")
    distance: Optional[str] = Field(None, description="Distance from hotel")
    price_range: Optional[str] = Field(None, description="Price range indicator")
    address: Optional[str] = Field(None, description="Physical address")
    phone: Optional[str] = Field(None, description="Contact phone number")
    website: Optional[str] = Field(None, description="Website URL")
    hours: Optional[str] = Field(None, description="Operating hours")
    special_features: Optional[List[str]] = Field(None, description="Special features or amenities")
    personalization_reason: Optional[str] = Field(None, description="Why this recommendation was chosen for this guest")
    image_url: Optional[str] = Field(None, description="URL to an image of the place")
    google_place_id: Optional[str] = Field(None, description="Google Places API place ID")
    walking_duration: Optional[str] = Field(None, description="Walking time from hotel")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Sally's Apizza",
                "type": "Restaurant",
                "category": "Italian",
                "description": "Famous New Haven pizza institution known for thin-crust coal-fired pizza",
                "rating": 4.5,
                "distance": "0.3 miles",
                "price_range": "$$",
                "address": "237 Wooster St, New Haven, CT 06511",
                "phone": "(203) 624-5271",
                "website": "https://sallysapizza.com",
                "hours": "Tue-Sun 5:00 PM - 10:00 PM",
                "special_features": ["Historic", "Coal-fired oven", "Cash only"],
                "personalization_reason": "Based on your location and preference for authentic local dining",
                "image_url": "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=...",
                "google_place_id": "ChIJ..."
            }
        }
    }


class RecommendationRequest(BaseModel):
    """Request schema for generating recommendations."""
    
    reservation_id: str = Field(..., description="The reservation ID to get context for")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="Guest preferences")
    max_recommendations: Optional[int] = Field(default=None, description="Maximum number of recommendations")
    categories: Optional[List[str]] = Field(default=None, description="Specific categories to focus on")
    radius_miles: Optional[float] = Field(default=5.0, description="Search radius in miles")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "reservation_id": "142766272",
                "preferences": {
                    "cuisine": "Italian",
                    "budget": "moderate",
                    "atmosphere": "casual"
                },
                "max_recommendations": 5,
                "categories": ["restaurants", "activities"],
                "radius_miles": 3.0
            }
        }
    }


class RecommendationResponse(BaseModel):
    """Response schema for generated recommendations."""
    
    request_id: str = Field(..., description="Unique identifier for this request")
    reservation_id: str = Field(..., description="The reservation ID this was generated for")
    recommendations: List[RecommendationItem] = Field(..., description="Generated recommendations")
    personalization_summary: str = Field(..., description="Summary of how recommendations were personalized")
    group_type: str = Field(..., description="Type of guest group (family, business, couple, etc.)")
    generated_at: datetime = Field(..., description="When recommendations were generated")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "request_id": "rec_20250116_143022_1234",
                "reservation_id": "142766272",
                "recommendations": [
                    {
                        "name": "Sally's Apizza",
                        "type": "Restaurant",
                        "category": "Italian",
                        "description": "Famous New Haven pizza institution",
                        "rating": 4.5,
                        "distance": "0.3 miles"
                    }
                ],
                "personalization_summary": "Based on family with children, Italian cuisine preference, and moderate budget",
                "group_type": "Family",
                "generated_at": "2025-01-16T14:30:22.123Z",
                "metadata": {"total_recommendations": 1, "search_radius": 3.0}
            }
        }
    }
