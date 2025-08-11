
import google.generativeai as genai
import asyncio, json
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
GEMINI_MODEL = "gemini-1.5-pro"

EXTRACTION_SYS = """You extract dining preferences from noisy reservation text.
Return strict JSON: { "cuisines":[], "avoid_cuisines":[], "price_band":"low|mid|high|any",
"ambiance":[], "dietary":[], "notes":"" }"""
RERANK_SYS = """You are a ranking model. Score 0..1 for restaurants vs criteria.
Consider cuisine match, price fit, distance, rating & volume, ambiance, dietary/halal/accessibility.
Return JSON list: [{"place_id": "...", "score": 0.82, "why": "..."}]"""

async def gemini_json(system_instruction: str, user_prompt: str) -> dict | list:
    model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_instruction)
    resp = await asyncio.to_thread(
        model.generate_content,
        user_prompt,
        generation_config={"response_mime_type": "application/json"},
    )
    txt = resp.text or "{}"
    try:
        return json.loads(txt)
    except Exception:
        return {}
