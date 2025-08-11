
from typing import Dict, Any
from app.config import settings
from app.utils.http import HttpClientFactory, retry_strategy
from tenacity import retry

@retry(**retry_strategy)
async def place_details(place_id: str) -> Dict[str, Any]:
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    fields = "place_id,name,formatted_address,geometry/location,price_level,rating,user_ratings_total,types,website,url,reviews,photos"
    params = {"place_id": place_id, "fields": fields, "key": settings.GOOGLE_MAPS_API_KEY}
    async with HttpClientFactory.client(12.0) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json().get("result", {})
