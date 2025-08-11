
# Local Recommendation API — Complex LangGraph (LangChain OpenAI & Gemini + Vertex Maps Grounding)

Pipeline:
1) Fetch reservation & conversation from Kamrul
2) Extract relevant fields & flatten guests
3) OpenAI (via LangChain) → travel reason + sentiment
4) Hybrid recs: standard seed + Gemini grounded in Google Maps (Vertex REST)
5) Enrich each candidate with Places Details & Photos
6) Assemble final recommendations


---

## Kamrul API Mocking
Set in `.env`:
```
KAMRUL_USE_MOCK=true
KAMRUL_MOCK_DIR=./data/mocks
```
Place mock files:
- `data/mocks/reservations/<reservation_id>.json`
- `data/mocks/conversations/<reservation_id>.json`

Example IDs included:
- `demo-1`
- `demo-2`
