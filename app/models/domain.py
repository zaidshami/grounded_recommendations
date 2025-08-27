"""
Domain models for the Guest Recommendation Generation API.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Guest(BaseModel):
    """Guest information model."""
    
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class Property(BaseModel):
    """Property information model."""
    
    id: str
    name: str
    address: str
    city: str
    state: str
    country: str
    neighborhood: Optional[str] = None
    amenities: List[str] = []
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Reservation(BaseModel):
    """Reservation information model."""
    
    id: str
    guest: Guest
    property: Property
    check_in: datetime
    check_out: datetime
    length_of_stay: int
    number_of_guests: int
    group_type: str
    status: str
    created_at: datetime
    updated_at: datetime


class ConversationMessage(BaseModel):
    """Individual conversation message model."""
    
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class Conversation(BaseModel):
    """Conversation history model."""
    
    reservation_id: str
    messages: List[ConversationMessage]
    preferences: Optional[Dict[str, Any]] = None
    sentiment: Optional[str] = None
    summary: Optional[str] = None


class Recommendation(BaseModel):
    """Recommendation model."""
    
    id: str
    name: str
    type: str  # 'restaurant', 'attraction', 'activity', etc.
    description: str
    personalization_reason: str
    address: Optional[str] = None
    rating: Optional[float] = None
    price_level: Optional[str] = None
    image_url: Optional[str] = None
    google_place_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RecommendationSet(BaseModel):
    """Complete set of recommendations for a guest."""
    
    reservation_id: str
    guest_name: str
    destination: str
    stay_dates: str
    group_type: str
    recommendations: List[Recommendation]
    personalization_summary: str
    generated_at: datetime
    source_data: Dict[str, Any]  # Track what data was used
