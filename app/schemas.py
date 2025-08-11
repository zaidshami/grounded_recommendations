
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

class LatLng(BaseModel):
    lat: float
    lng: float

class HardConstraints(BaseModel):
    halal: Optional[bool] = None
    wheelchair_accessible: Optional[bool] = None

class Reservation(BaseModel):
    reservation_id: str
    guest_name: Optional[str] = None
    party_size: int = Field(default=2, ge=1, le=20)
    datetime_iso: Optional[str] = None
    location: LatLng
    radius_m: int = Field(default=3000, ge=200, le=10000)
    notes: Optional[str] = ""
    hard_constraints: Optional[HardConstraints] = HardConstraints()

class Criteria(BaseModel):
    cuisines: List[str] = []
    avoid_cuisines: List[str] = []
    price_band: str = "any"
    ambiance: List[str] = []
    dietary: List[str] = []
    notes: str = ""

class Place(BaseModel):
    name: Optional[str] = None
    place_id: Optional[str] = None
    address: Optional[str] = None
    maps_url: Optional[HttpUrl] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    price_level: Optional[int] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    cuisine_tags: List[str] = []
    distance_m: Optional[int] = None
    why: Optional[str] = None
    score: Optional[float] = None
    reviews: Optional[list] = None
    photo_references: Optional[list] = None
    photo_urls: Optional[list] = None

class RecResponse(BaseModel):
    reservation_id: str
    criteria: Criteria
    results: List[Place]
