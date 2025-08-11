
from typing import Dict, Any, List
import orjson, httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.schemas import Reservation, Criteria
from app.services.kamrul import fetch_reservation, fetch_conversation
from app.services.openai_reason_lc import extract_reason_and_sentiment
from app.services.vertex_maps_grounding import ask_gemini_grounded
from app.services.maps import place_details
from app.services.maps_photos import places_photo_url
from app.config import settings

def safe_get(d: dict, path: List[str], default=None):
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur

def join_relevant_fields(res_json: dict, conv_json: dict) -> Dict[str, Any]:
    fields = {
        "reason_for_travel_personalization": safe_get(res_json, ["reason_for_travel_personalization"]),
        "reason_for_travel_sentiment_classification": safe_get(res_json, ["reason_for_travel_sentiment_classification"]),
        "number_of_guests": safe_get(res_json, ["number_of_guests"]),
        "date_from": safe_get(res_json, ["date_from"]),
        "date_to": safe_get(res_json, ["date_to"]),
        "length_of_stay": safe_get(res_json, ["length_of_stay"]),
        "buildings.city": safe_get(res_json, ["buildings","city"]),
        "buildings.address": safe_get(res_json, ["buildings","address"]),
        "conversation_snippets": safe_get(conv_json, ["snippets"], []),
    }
    conv_text = "\n".join(s.get("text","") for s in fields["conversation_snippets"] or [])
    joined = []
    for k,v in fields.items():
        if v not in (None, "", []):
            joined.append(f"{k}: {v}")
    return {"fields": fields, "joined_context": "\n".join(joined + [conv_text] if conv_text else joined)}

def flatten_additional_guests(res_json: dict) -> List[dict]:
    guests = safe_get(res_json, ["additional_guests"], []) or []
    out = []
    for g in guests:
        out.append({
            "name": g.get("name"),
            "age": g.get("age"),
            "dietary": g.get("dietary"),
            "notes": g.get("notes"),
        })
    return out

def _standard_recos_seed(city: str | None) -> List[Dict[str, Any]]:
    return [
        {"name":"Classic Grill", "cuisine_tags":["Grill","Steak"], "city":city, "seed":True},
        {"name":"Family Mezze", "cuisine_tags":["Mediterranean","Lebanese"], "city":city, "seed":True},
    ]

async def node_fetch_reservation(state: Dict[str, Any]) -> Dict[str, Any]:
    rid = state["reservation_id"]
    state["reservation_raw"] = await fetch_reservation(rid)
    return state

async def node_fetch_conversation(state: Dict[str, Any]) -> Dict[str, Any]:
    rid = state["reservation_id"]
    state["conversation_raw"] = await fetch_conversation(rid)
    return state

async def node_extract_join_base(state: Dict[str, Any]) -> Dict[str, Any]:
    resj = state.get("reservation_raw", {})
    convj = state.get("conversation_raw", {})
    joined = join_relevant_fields(resj, convj)
    state["base_joined"] = joined

    res: Reservation = state["reservation"]
    ps = joined["fields"].get("number_of_guests")
    if isinstance(ps, int) and ps > 0:
        res.party_size = ps
    state["reservation"] = res

    criteria = state.get("criteria") or Criteria()
    criteria.notes = "Travel personalization pipeline"
    state["criteria"] = criteria
    return state

async def node_flatten_guests(state: Dict[str, Any]) -> Dict[str, Any]:
    resj = state.get("reservation_raw", {})
    state["additional_guests_flat"] = flatten_additional_guests(resj)
    return state

async def node_reason_sentiment(state: Dict[str, Any]) -> Dict[str, Any]:
    data = state.get("base_joined", {})
    out = await extract_reason_and_sentiment(data)
    print('zizo')
    print(out)
    state["travel_reason"] = out.get("reason","unknown")
    state["travel_sentiment"] = out.get("sentiment","unknown")
    return state

# async def node_hybrid_recos(state: Dict[str, Any]) -> Dict[str, Any]:
#     import math, logging
#     log = logging.getLogger("hybrid_recos")
#
#     def _haversine_m(lat1, lng1, lat2, lng2):
#         R = 6371000.0
#         p1, p2 = math.radians(lat1), math.radians(lat2)
#         dphi  = math.radians(lat2 - lat1)
#         dlmb  = math.radians(lng2 - lng1)
#         a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
#         return int(2*R*math.asin(math.sqrt(a)))
#
#     def _strip_code_fences(s: str) -> str:
#         s = s.strip()
#         if s.startswith("```"):
#             parts = s.split("```")
#             if len(parts) >= 3:
#                 s = parts[1]  # content between first and second ```
#             else:
#                 s = s.lstrip("`")
#         # drop a leading language hint line like `json`
#         lines = s.splitlines()
#         if lines and lines[0].strip().lower() in {"json", "javascript"}:
#             s = "\n".join(lines[1:])
#         return s.strip()
#
#     def _collect_vertex_results(vresp: dict) -> list[dict]:
#         out: list[dict] = []
#         for cand in (vresp.get("candidates") or []):
#             content = cand.get("content") or {}
#             for part in (content.get("parts") or []):
#                 txt = (part.get("text") or "").strip()
#                 if not txt:
#                     continue
#                 try:
#                     payload = orjson.loads(_strip_code_fences(txt))
#                 except Exception:
#                     continue
#                 if isinstance(payload, dict) and isinstance(payload.get("results"), list):
#                     out.extend(payload["results"])
#                 elif isinstance(payload, list):
#                     out.extend(payload)
#         return out
#
#     res: Reservation = state["reservation"]
#     joined = state.get("base_joined", {})
#     city = (joined.get("fields") or {}).get("buildings.city")
#     std = _standard_recos_seed(city)
#
#     reason = state.get("travel_reason","")
#     sentiment = state.get("travel_sentiment","")
#
#     prompt = (
#         "You are a local recommendation assistant. Blend to the travel context.\n"
#         f"Travel reason: {reason}\n"
#         f"Sentiment: {sentiment}\n"
#         "Return JSON ONLY with up to 4 items:\n"
#         "{ \"results\": [ {"
#         "\"name\":\"str\",\"maps_url\":\"str\",\"place_id\":\"str\",\"address\":\"str\","
#         "\"lat\":0,\"lng\":0,\"rating\":0,\"user_ratings_total\":0,"
#         "\"price_level\":0,\"distance_m\":0,\"why\":\"str\",\"cuisine_tags\":[] } ] }"
#     )
#
#     vresp = await ask_gemini_grounded(prompt, res.location.lat, res.location.lng)
#
#     # Collect ALL results from ALL candidates/parts
#     grounded_list = _collect_vertex_results(vresp)
#
#     # Compute distance if lat/lng present
#     for it in grounded_list:
#         try:
#             plat, plng = it.get("lat"), it.get("lng")
#             if plat is not None and plng is not None:
#                 it["distance_m"] = _haversine_m(res.location.lat, res.location.lng, float(plat), float(plng))
#         except Exception:
#             pass
#
#     # Merge + dedupe: prefer entries with place_id; fallback to name
#     merged: list[dict] = []
#     seen_pid: set[str] = set()
#     seen_name: set[str] = set()
#
#     for x in grounded_list:
#         pid = (x.get("place_id") or "").strip()
#         name = (x.get("name") or "").strip()
#         key_ok = False
#         if pid and pid not in seen_pid:
#             seen_pid.add(pid); key_ok = True
#         elif not pid and name and name.lower() not in seen_name:
#             seen_name.add(name.lower()); key_ok = True
#         if key_ok:
#             merged.append(x)
#
#     # Add seed fallbacks (skip if already present)
#     for s in std:
#         name = (s.get("name") or "").strip()
#         if name and name.lower() not in seen_name:
#             seen_name.add(name.lower())
#             merged.append(s)
#
#     # Optionally trim pre-enrichment for performance
#     pre_cap = max(settings.GRAPH_MAX_RESULTS * 2, 10)
#     state["candidates_raw"] = merged[:pre_cap]
#     return state

async def node_hybrid_recos(state: Dict[str, Any]) -> Dict[str, Any]:
    def _strip_code_fences(s: str) -> str:
        s = s.strip()
        if s.startswith("```"):
            parts = s.split("```")
            # content between first and second ```
            if len(parts) >= 3:
                s = parts[1]
            else:
                s = s.lstrip("`")
        # remove leading language hint like `json`
        lines = s.splitlines()
        if lines and lines[0].strip().lower() in {"json", "javascript"}:
            s = "\n".join(lines[1:])
        return s.strip()

    def _collect_vertex_results(vresp: dict) -> list[dict]:
        import orjson
        results: list[dict] = []
        for cand in (vresp.get("candidates") or []):
            content = cand.get("content") or {}
            for part in (content.get("parts") or []):
                txt = (part.get("text") or "").strip()
                if not txt:
                    continue
                try:
                    payload = orjson.loads(_strip_code_fences(txt))
                except Exception:
                    continue
                # Accept either {"results":[...]} or a bare list [...]
                if isinstance(payload, dict) and isinstance(payload.get("results"), list):
                    results.extend(payload["results"])
                elif isinstance(payload, list):
                    results.extend(payload)
        return results
    res: Reservation = state["reservation"]
    joined = state.get("base_joined", {})
    city = (joined.get("fields") or {}).get("buildings.city")
    std = _standard_recos_seed(city)

    reason = state.get("travel_reason","")
    sentiment = state.get("travel_sentiment","")
    # prompt="suggest a top 3 near restronts from my location for a Plan a family dinner "
    # prompt="suggest a 3 near restraints from my location for a Plan a family dinner "

    #
    prompt = (
        "You are a local recommendation assistant. Blend to the travel context. please use my coordinates to help :\n"
        f"Latitude : { res.location.lat} \n'"
        f"Longitude : { res.location.lng} \n'"
        f"Travel reason: {reason}\n"
        f"Sentiment: {sentiment}\n"
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
    )


    vresp = await ask_gemini_grounded(prompt, res.location.lat, res.location.lng)
    print('zizo 4')
    print(vresp)

    parsed_items = _collect_vertex_results(vresp)
    vjson = {"results": parsed_items} if parsed_items else {"results": []}

    merged = []
    seen = set()
    for x in (vjson.get("results") or []):
        pid = x.get("place_id")
        if pid and pid not in seen:
            seen.add(pid);
            merged.append(x)
    for s in std:
        name = s.get("name")
        if name and name not in seen:
            merged.append(s)

    state["candidates_raw"] = merged
    return state
    # try:
    #     vjson = orjson.loads(vresp["candidates"][0]["content"]["parts"][0]["text"]) or {}
    # except Exception:
    #     vjson = {"results":[]}
    #
    # merged = []
    # seen = set()
    # for x in (vjson.get("results") or []):
    #     pid = x.get("place_id")
    #     if pid and pid not in seen:
    #         seen.add(pid); merged.append(x)
    # for s in std:
    #     name = s.get("name")
    #     if name and name not in seen:
    #         merged.append(s)
    # state["candidates_raw"] = merged
    # return state

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(0.4, 0.4, 2), 
       retry=retry_if_exception_type((httpx.ReadTimeout, httpx.ConnectTimeout, httpx.RemoteProtocolError)))
async def _details(place_id: str) -> dict:
    return await place_details(place_id)


async def node_enrich_candidates(state: Dict[str, Any]) -> Dict[str, Any]:
    import math

    def _haversine_m(lat1, lng1, lat2, lng2):
        R = 6371000.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dphi  = math.radians(lat2 - lat1)
        dlmb  = math.radians(lng2 - lng1)
        a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
        return int(2 * R * math.asin(math.sqrt(a)))

    res: Reservation = state["reservation"]
    out = []

    for c in state.get("candidates_raw", []):
        pid = (c.get("place_id") or "").strip()

        # Try Places Details if we have a place_id
        d = {}
        if pid:
            try:
                d = await _details(pid) or {}
            except Exception:
                d = {}

        # Pull details (prefer Places; fallback to candidate)
        name = d.get("name") or c.get("name")
        addr = d.get("formatted_address") or c.get("address")
        plat = (d.get("geometry") or {}).get("location", {}).get("lat")
        plng = (d.get("geometry") or {}).get("location", {}).get("lng")
        if plat is None or plng is None:
            # fallback to candidate lat/lng if Places didn't return geometry
            plat = c.get("lat")
            plng = c.get("lng")

        price_level = d.get("price_level", c.get("price_level"))
        rating = d.get("rating", c.get("rating"))
        user_ratings_total = d.get("user_ratings_total", c.get("user_ratings_total"))
        maps_url = d.get("url") or d.get("website") or c.get("maps_url")
        cuisine_tags = c.get("cuisine_tags") or d.get("types", [])
        why = c.get("why")  # keep model rationale if provided

        # Photos (Places → URLs), safe defaults
        photos = (d.get("photos") or [])[:3]
        photo_refs = [p.get("photo_reference") for p in photos if p.get("photo_reference")]
        photo_urls = []
        for pr in photo_refs:
            try:
                url = await places_photo_url(pr, 800)
                if url:
                    photo_urls.append(url)
            except Exception:
                pass

        # Distance (compute if we have coordinates)
        dist_m = None
        try:
            if plat is not None and plng is not None:
                dist_m = _haversine_m(res.location.lat, res.location.lng, float(plat), float(plng))
        except Exception:
            pass

        # Reviews (trim)
        reviews = (d.get("reviews") or [])[:3]

        # If we have almost nothing, skip
        if not (pid or name):
            continue

        out.append({
            "place_id": pid or c.get("place_id"),
            "name": name,
            "address": addr,
            "lat": plat,
            "lng": plng,
            "price_level": price_level,
            "rating": rating,
            "user_ratings_total": user_ratings_total,
            "maps_url": maps_url,
            "cuisine_tags": cuisine_tags or [],
            "distance_m": dist_m if dist_m is not None else c.get("distance_m"),
            "why": why,
            "score": c.get("score"),
            "reviews": reviews,
            "photo_references": photo_refs,
            "photo_urls": photo_urls,
        })

    state["enriched"] = out
    return state
# async def node_enrich_candidates(state: Dict[str, Any]) -> Dict[str, Any]:
#     out = []
#     for c in state.get("candidates_raw", []):
#         pid = c.get("place_id")
#         if not pid:
#             continue
#         d = await _details(pid)
#         photos = (d.get("photos") or [])[:3]
#         photo_refs = [p.get("photo_reference") for p in photos if p.get("photo_reference")]
#         photo_urls = []
#         for pr in photo_refs:
#             try:
#                 url = await places_photo_url(pr, 800)
#                 if url: photo_urls.append(url)
#             except Exception:
#                 pass
#         out.append({
#             "place_id": pid,
#             "name": d.get("name") or c.get("name"),
#             "address": d.get("formatted_address"),
#             "lat": (d.get("geometry") or {}).get("location",{}).get("lat"),
#             "lng": (d.get("geometry") or {}).get("location",{}).get("lng"),
#             "price_level": d.get("price_level"),
#             "rating": d.get("rating"),
#             "user_ratings_total": d.get("user_ratings_total"),
#             "maps_url": d.get("url") or d.get("website"),
#             "cuisine_tags": c.get("cuisine_tags") or d.get("types", []),
#             "reviews": (d.get("reviews") or [])[:3],
#             "photo_references": photo_refs,
#             "photo_urls": photo_urls,
#         })
#     state["enriched"] = out
#     return state

async def node_assemble(state: Dict[str, Any]) -> Dict[str, Any]:
    enriched = state.get("enriched", [])
    enriched.sort(key=lambda x: ((x.get("rating") or 0), (x.get("user_ratings_total") or 0)), reverse=True)
    state["final"] = enriched[: settings.GRAPH_MAX_RESULTS]
    return state
