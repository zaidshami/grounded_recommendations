
import asyncio, uuid
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.config import settings
from app.schemas import Reservation, RecResponse, Criteria, Place
from app.utils.logging import configure_logging
from app.graph.reco_graph import build_graph
from app.security.auth import api_key_guard



log = configure_logging(settings.LOG_LEVEL)
graph = build_graph()

app = FastAPI(title="Local Recommendation API (Complex Flow + LangChain)", version="1.0.0")
#
@app.middleware("http")
async def add_request_context(request: Request, call_next):
    req_id = str(uuid.uuid4())
    request.state.req_id = req_id
    try:
        response = await call_next(request)
        response.headers["x-request-id"] = req_id
        return response
    except Exception as e:
        log.error("unhandled_error", req_id=req_id, error=str(e))
        return JSONResponse({"detail": "internal error", "req_id": req_id}, status_code=500)

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.post("/v1/recommendations", response_model=RecResponse, dependencies=[Depends(api_key_guard)])
async def recommend(res: Reservation):

    # print(_access_token())
    if res.radius_m > settings.GRAPH_MAX_RADIUS_M:
        res.radius_m = settings.GRAPH_MAX_RADIUS_M
    try:
        state_in = {
            "reservation_id": res.reservation_id,
            "reservation": res,
            "criteria": Criteria()
        }
        result = await asyncio.wait_for(graph.ainvoke(state_in), timeout=settings.REQUEST_TIMEOUT_S)
        final = result.get("final", []) or []
        places = [Place(**p) for p in final]
        criteria = result.get("criteria") or Criteria()
        return RecResponse(reservation_id=res.reservation_id, criteria=criteria, results=places)
    except asyncio.TimeoutError:
        raise HTTPException(504, "Recommendation timed out")
import json, httpx, google.auth

def _access_token() -> str:
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    if not creds.valid:
        creds.refresh(Request())
    return creds.token
