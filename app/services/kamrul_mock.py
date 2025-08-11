
import os, json
from typing import Any, Dict
from app.config import settings

def _mock_path(kind: str, reservation_id: str) -> str:
    base = settings.KAMRUL_MOCK_DIR
    return os.path.join(base, kind, f"{reservation_id}.json")

async def fetch_reservation_mock(reservation_id: str) -> Dict[str, Any]:
    path = _mock_path("reservations", reservation_id)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

async def fetch_conversation_mock(reservation_id: str) -> Dict[str, Any]:
    path = _mock_path("conversations", reservation_id)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
