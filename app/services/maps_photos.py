
import httpx
from app.config import settings

async def places_photo_url(photo_reference: str, maxwidth: int = 800) -> str | None:
    url = "https://maps.googleapis.com/maps/api/place/photo"
    params = {"photo_reference": photo_reference, "maxwidth": maxwidth, "key": settings.GOOGLE_MAPS_API_KEY}
    async with httpx.AsyncClient(follow_redirects=False, timeout=10) as client:
        r = await client.get(url, params=params)
        return r.headers.get("Location")
