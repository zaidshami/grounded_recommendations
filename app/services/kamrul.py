
from typing import Any, Dict
from app.config import settings
from app.services.kamrul_mock import fetch_reservation_mock, fetch_conversation_mock
from app.utils.http import HttpClientFactory, retry_strategy
from tenacity import retry

BASE = settings.KAMRUL_API_BASE
HEADERS = {"Authorization": f"Bearer {settings.KAMRUL_API_KEY}"} if settings.KAMRUL_API_KEY else {}

@retry(**retry_strategy)

async def fetch_reservation(reservation_id: str) -> Dict[str, Any]:
    if settings.KAMRUL_USE_MOCK:
        return await fetch_reservation_mock(reservation_id)

    url = f"{BASE}/v1/reservations/{reservation_id}"
    async with HttpClientFactory.client(12) as client:
        r = await client.get(url, headers=HEADERS)
        r.raise_for_status()
        return r.json()

@retry(**retry_strategy)

async def fetch_conversation(reservation_id: str) -> Dict[str, Any]:
    if settings.KAMRUL_USE_MOCK:
        return await fetch_conversation_mock(reservation_id)

    url = f"{BASE}/v1/reservations/{reservation_id}/conversation"
    async with HttpClientFactory.client(12) as client:
        r = await client.get(url, headers=HEADERS)
        r.raise_for_status()
        return r.json()
