
import json, httpx, google.auth
from google.auth.transport.requests import Request
from app.config import settings

def _access_token() -> str:
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    if not creds.valid:
        creds.refresh(Request())
    return creds.token

def endpoint() -> str:
    loc = settings.VERTEX_LOCATION
    return f"https://{loc}-aiplatform.googleapis.com/v1beta1/projects/{settings.PROJECT_ID}/locations/{loc}/publishers/google/models/{settings.VERTEX_MODEL_ID}:generateContent"

def generation_config():
    return { "responseMimeType": "application/json"
             # ,    "temperature": 0.2,
}

def maps_tool(lat: float, lng: float) -> dict:
    return {
        "tools": [ { "googleMaps": {} } ],
        "toolConfig": { "retrievalConfig": { "latLng": { "latitude": lat, "longitude": lng } } }
    }

async def ask_gemini_grounded(prompt_text: str, lat: float, lng: float) -> dict:
    """
         Uses Grounding with Google Maps in Vertex AI to generate recommendations

         Args:
             prompt_text (str): The metadata query about user .
             lat (float): User's current latitude.
             lng (float): User's current longitude.

         Returns:
             " Return JSON ONLY : {"
                "\"results\": [{"
                "\"name\": \"str\","
                "\"maps_url\": \"str\","
                "\"place_id\": \"str\","
                "\"address\": \"str\","
                "\"lat\": 0,"
                "\"lng\": 0,"
                "\"rating\": 0,"
                "\"user_ratings_total\": 0,"
                "\"price_level\": 0,"
                "\"distance_m\": 0,"
                "\"why\": \"str\","
                "\"cuisine_tags\": []"
                "}]}"
         """

    print(prompt_text)
    body = {
        # "contents": [{"role": "user", "parts": [{"text": ' suggest a near restronts from my location for a Plan a family dinner '}]}],
        "contents": [{"role": "user", "parts": [{"text": prompt_text}]}],
        "model": f"projects/{settings.PROJECT_ID}/locations/{settings.VERTEX_LOCATION}/publishers/google/models/{settings.VERTEX_MODEL_ID}",
        **maps_tool(lat, lng),
        "generationConfig": generation_config(),
    }


    print(body)
    headers = {
        "Authorization": f"Bearer {_access_token()}",
        "Content-Type": "application/json; charset=utf-8"
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(endpoint(), headers=headers, json=body)
        r.raise_for_status()
        return r.json()


