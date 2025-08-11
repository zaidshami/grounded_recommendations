
import asyncio, uuid
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.config import settings
from app.schemas import Reservation, RecResponse, Criteria, Place
from app.utils.logging import configure_logging
from app.graph.reco_graph import build_graph
from app.security.auth import api_key_guard
from pathlib import Path



log = configure_logging(settings.LOG_LEVEL)
graph = build_graph()
path = Path("graph.png")
# try:
#     # PNG (requires graphviz + pygraphviz or pydot)
#     png_bytes = graph.get_graph().draw_png()
#     path.parent.mkdir(parents=True, exist_ok=True)
#     path.write_bytes(png_bytes)
# except Exception as e:
#     log.warning("draw_png failed (%s). Trying Mermaid fallback…", e)
#     try:
#         # If available in your langgraph version
#         png_bytes = graph.get_graph().draw_mermaid_png()
#         path.parent.mkdir(parents=True, exist_ok=True)
#         path.write_bytes(png_bytes)
#     except Exception:
#         # Final fallback: write Mermaid source so you can render elsewhere
#         mmd = graph.get_graph().draw_mermaid()
#         mmd_path = path.with_suffix(".mmd")
#         mmd_path.parent.mkdir(parents=True, exist_ok=True)
#         mmd_path.write_text(mmd, encoding="utf-8")
#         log.info("Wrote Mermaid to %s (render it with your CI/editor).", mmd_path)

app = FastAPI(title="Local Recommendation API ( Vertex AI + LangChain)", version="1.0.0")
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


