"""Glance GenAd - Attention Friction & Ad Blindness demo (FastAPI backend)."""
import logging
import os
import time
import uuid
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import analytics
import engine
import lakebase

log = logging.getLogger("glance")
logging.basicConfig(level=logging.INFO)
STATIC = Path(__file__).parent / "static"
CATALOG = os.getenv("DEMO_CATALOG", "glance_genad")
app = FastAPI(title="Glance GenAd")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
STATUS = {"lakebase": None, "models": None}


def load_models():
    try:
        rows, ms = lakebase.coefficients()
        if rows:
            engine.MODELS.load(rows, "Lakebase synced table glance_serving.model_coefficients", ms)
            return
    except Exception as e:  # noqa: BLE001
        log.warning("Lakebase coefficients unavailable (%s) - falling back to SQL warehouse", e)
    t0 = time.perf_counter()
    rows = analytics.sql(f"SELECT model_name, feature, weight, model_version FROM {CATALOG}.ml.model_coefficients", ttl=0)
    engine.MODELS.load(rows, f"Unity Catalog {CATALOG}.ml.model_coefficients (SQL warehouse)", round((time.perf_counter() - t0) * 1000))


@app.on_event("startup")
def startup():
    try:
        lakebase.init()
        STATUS["lakebase"] = "ok"
    except Exception as e:  # noqa: BLE001
        STATUS["lakebase"] = f"error: {e}"
        log.exception("lakebase init failed")
    try:
        load_models()
        STATUS["models"] = f"ok ({engine.MODELS.source}, v{engine.MODELS.version})"
    except Exception as e:  # noqa: BLE001
        STATUS["models"] = f"error: {e}"
        log.exception("model load failed")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/health")
def health():
    return STATUS | {"model_version": engine.MODELS.version, "model_source": engine.MODELS.source}


@app.post("/api/reload-models")
def reload_models():
    load_models()
    STATUS["models"] = f"ok ({engine.MODELS.source}, v{engine.MODELS.version})"
    return health()


@app.get("/api/bootstrap")
def bootstrap():
    personas = []
    try:
        personas = lakebase.personas()
    except Exception as e:  # noqa: BLE001
        log.warning("personas: %s", e)
    return {"taxonomy": engine.TAX, "personas": personas, "status": health(),
            "genie_enabled": bool(analytics.GENIE_SPACE)}


@app.get("/api/live-context")
def live_context(city: str):
    rows, ms = lakebase.live_context(city)
    out = {"city": city, "lakebase_ms": ms, "signals": rows, "suggested": {}}
    for r in rows:
        if r["signal_type"] == "weather" and r["signal_key"] in engine.TAX["weather"]:
            out["suggested"]["weather"] = r["signal_key"]
        if r["signal_type"] == "live_event" and r["signal_key"] in engine.TAX["live_event"]:
            out["suggested"]["live_event"] = r["signal_key"]
        if r["signal_type"] == "transit" and float(r.get("intensity") or 0) >= 0.6:
            out["suggested"]["user_state"] = "just_missed_train"
    return out


@app.get("/api/signals")
def signals():
    return lakebase.recent_signals(14)


class GenRequest(BaseModel):
    user_id: str
    brand: str
    weather: str
    time_slot: str
    user_state: str
    live_event: str = "none"
    phone_skin: str | None = None


@app.post("/api/generate")
def generate(req: GenRequest, request: Request):
    if not engine.MODELS.ready:
        load_models()
    profile, lb_ms = lakebase.user_profile(req.user_id)
    if not profile:
        raise HTTPException(404, "unknown user")
    s = {"user_id": req.user_id, "city": profile["city"], "segment": profile["segment"], "brand": req.brand,
         "weather": req.weather, "time_slot": req.time_slot, "user_state": req.user_state,
         "live_event": req.live_event, "phone_skin": req.phone_skin or profile["preferred_skin"]}
    out = engine.generate(s, profile)
    out["timings"]["lakebase_profile_ms"] = lb_ms
    out["profile"] = {k: profile[k] for k in ("user_id", "city", "segment", "preferred_skin", "device_os", "behavior_vector", "daily_unlocks")}
    g, st = out["generative"], out["static"]
    decision_id = f"dec-{uuid.uuid4().hex[:12]}"
    t0 = time.perf_counter()
    try:
        lakebase.insert_decision({
            "decision_id": decision_id, "requested_by": request.headers.get("x-forwarded-email", "local"),
            "user_id": s["user_id"], "segment": s["segment"], "brand": s["brand"], "city": s["city"],
            "weather": s["weather"], "time_slot": s["time_slot"], "user_state": s["user_state"],
            "live_event": s["live_event"], "phone_skin": s["phone_skin"], "chosen_theme": g["theme"],
            "chosen_angle": g["angle"], "matched_component": (out["component"] or {}).get("component_id"),
            "relevance_score": g["relevance"], "headline": g["copy"]["headline"], "body": g["copy"]["body"],
            "cta": g["copy"]["cta"], "copy_source": g["copy_source"],
            "pctr_static": st["pctr"], "pctr_generative": g["pctr"], "pdwell_static_s": st["pdwell_s"],
            "pdwell_generative_s": g["pdwell_s"], "poptout_static": st["poptout"], "poptout_generative": g["poptout"],
            "attention_static": st["attention"], "attention_generative": g["attention"],
            "ecpm_static": st["ecpm"], "ecpm_generative": g["ecpm"], "themes_scored": out["themes_scored"],
            "blocked_by_guardrail": out["guardrail"]["blocked_combos"] + len(out["rejected_components"]),
            "latency_ms": int(out["timings"]["total_ms"] + lb_ms),
            "scoring_detail": {"leaderboard": [{k: c[k] for k in ("theme", "angle", "pctr", "ecpm", "blocked")} for c in out["leaderboard"]],
                               "why": out["why"], "model_version": out["model_version"]},
        })
        out["timings"]["lakebase_write_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    except Exception as e:  # noqa: BLE001
        log.exception("decision insert failed")
        out["decision_error"] = str(e)[:200]
    out["decision_id"] = decision_id
    out["model_source"] = engine.MODELS.source
    return JSONResponse(out)


@lru_cache(maxsize=32)
def _asset(path):
    return w_files_download(path)


def w_files_download(path):
    return engine.w.files.download(path).contents.read()


@app.get("/api/assets/{brand}/{name}")
def asset(brand: str, name: str):
    if brand not in engine.TAX["brands"] or not name.endswith(".svg") or "/" in name:
        raise HTTPException(404)
    try:
        data = _asset(f"/Volumes/{CATALOG}/raw/creative_assets/{brand}/{name}")
    except Exception as e:  # noqa: BLE001
        raise HTTPException(404, str(e)[:100])
    return Response(data, media_type="image/svg+xml", headers={"Cache-Control": "max-age=3600"})


@app.get("/api/analytics")
def analytics_api(brand: str = "starbucks"):
    out = {}
    for k, fn in (("scorecard", analytics.historical_scorecard), ("trend", analytics.weekly_trend),
                  ("policy", analytics.policy_eval), ("theme_weather", lambda: analytics.theme_by_weather(brand))):
        try:
            out[k] = fn()
        except Exception as e:  # noqa: BLE001
            out[k + "_error"] = str(e)[:300]
    return out


@app.get("/api/decisions")
def decisions():
    return {"recent": lakebase.recent_decisions(8), "stats": lakebase.decision_stats()}


class GenieRequest(BaseModel):
    question: str
    conversation_id: str | None = None


@app.post("/api/genie")
def genie(req: GenieRequest):
    try:
        return analytics.genie_ask(req.question, req.conversation_id)
    except Exception as e:  # noqa: BLE001
        log.exception("genie")
        return {"error": str(e)[:400]}
