#
# from openai import OpenAI
# from typing import Dict, Any
# from app.config import settings
# import asyncio
#
# client = OpenAI(api_key=settings.OPENAI_API_KEY)
#
# PROMPT = (
#     "You are extracting ONLY the relevant 'reason for travel' and 'sentiment' from provided sources.\n"
#     "Rules:\n"
#     "- Use ONLY information from the provided reservation + conversation snippets if relevant.\n"
#     "- If not clearly present, return 'unknown'.\n"
#     "Return JSON with keys: { 'reason': 'string', 'sentiment': 'positive|neutral|negative|unknown' }.\n"
# )
#
# async def extract_reason_and_sentiment(payload: Dict[str, Any]) -> Dict[str, str]:
#     text = payload.get('joined_context', '')
#     msg = f"{PROMPT}\n---\nSources:\n{text}\n---"
#     # SDK is sync; run in thread
#     def _call():
#         return client.chat.completions.create(
#             model=settings.OPENAI_MODEL,
#             messages=[{"role":"user","content":msg}],
#             response_format={"type":"json_object"},
#             temperature=0.2,
#         )
#     resp = await asyncio.to_thread(_call)
#     try:
#         parsed = resp.choices[0].message.parsed or {}
#         return parsed
#     except Exception:
#         import json
#         try:
#             return json.loads(resp.choices[0].message.content or "{}")
#         except Exception:
#             return {"reason":"unknown","sentiment":"unknown"}
