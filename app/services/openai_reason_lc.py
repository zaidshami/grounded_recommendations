
from typing import Dict, Any
import asyncio, json
from langchain_openai import ChatOpenAI
from app.config import settings

_llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=0.2,
    openai_api_key=settings.OPENAI_API_KEY,
)

PROMPT = (
    "You ONLY extract 'reason for travel' and 'sentiment' from the given sources.\n"
    "- Use ONLY the provided reservation + conversation snippets if relevant.\n"
    "- If not clearly present, return 'unknown'.\n"
    "Return JSON: {\"reason\":\"string\",\"sentiment\":\"positive|neutral|negative|unknown\"}.\n"
)

async def extract_reason_and_sentiment(payload: Dict[str, Any]) -> Dict[str, str]:
    text = payload.get("joined_context", "")
    msg = f"{PROMPT}\n---\nSources:\n{text}\n---"
    def _call():
        return _llm.invoke(msg).content or "{}"
    raw = await asyncio.to_thread(_call)
    try:
        return json.loads(raw)
    except Exception:
        return {"reason": "unknown", "sentiment": "unknown"}
