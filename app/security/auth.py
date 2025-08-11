
from fastapi import Header, HTTPException
from app.config import settings

async def api_key_guard(x_api_key: str | None = Header(default=None, alias=settings.API_KEY_HEADER_NAME)):
    if not settings.API_KEY_AUTH_ENABLED:
        return
    if not x_api_key or x_api_key != settings.API_KEY_VALUE:
        raise HTTPException(status_code=401, detail="Invalid API key")
